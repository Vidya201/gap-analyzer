# llm_utils.py - shared helpers for talking to Groq and parsing its output safely
#
# Why this exists: every feature file (1, 3, 5) asks the LLM to "return only JSON",
# but LLMs don't always obey that instruction perfectly - they sometimes wrap the
# answer in ```json fences, add a leading sentence, or occasionally return nothing
# parseable at all. Without handling that, a single odd response crashes the whole
# /analyze pipeline with an unhandled 500. This module centralizes the fix so it's
# written once and tested once, instead of copy-pasted three times.

import os
import re
import json
import logging
import time

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("skill_gap_analyzer")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

MODEL_NAME = "openai/gpt-oss-120b"  # Groq deprecated llama-3.3-70b-versatile (June 2026, fully
# decommissioned Aug 2026) — this is Groq's own recommended replacement. Keep this the single
# source of truth for the model name across the project.

# Support the new standard env var name, but fall back to the old one so existing
# .env files (groq_key=...) don't silently break.
_API_KEY = os.getenv("GROQ_API_KEY") or os.getenv("groq_key")

if not _API_KEY:
    logger.warning(
        "No Groq API key found. Set GROQ_API_KEY in your .env file "
        "(see .env.example). LLM-powered features will fail until this is set."
    )

client = Groq(api_key=_API_KEY)


def _strip_code_fences(text: str) -> str:
    """Remove ```json ... ``` or ``` ... ``` wrappers some models add anyway."""
    text = text.strip()
    fence_match = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, re.DOTALL)
    if fence_match:
        return fence_match.group(1).strip()
    return text


def _extract_first_json_block(text: str):
    """Last-resort fallback: pull out the first [...] or {...} block in the text."""
    array_match = re.search(r"\[.*\]", text, re.DOTALL)
    if array_match:
        return array_match.group(0)
    obj_match = re.search(r"\{.*\}", text, re.DOTALL)
    if obj_match:
        return obj_match.group(0)
    return None


def safe_json_parse(raw_text: str):
    """
    Try increasingly forgiving strategies to turn an LLM's text response into
    a Python object. Raises ValueError with a clear message if nothing works,
    so callers can decide how to degrade gracefully instead of crashing.
    """
    if not raw_text:
        raise ValueError("Empty response from LLM")

    cleaned = _strip_code_fences(raw_text)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    fallback_block = _extract_first_json_block(cleaned)
    if fallback_block:
        try:
            return json.loads(fallback_block)
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not parse JSON from LLM response: {raw_text[:200]!r}")


def call_llm_for_json(prompt: str, retries: int = 2, backoff_seconds: float = 1.5):
    """
    Call the Groq chat completion endpoint and parse the result as JSON,
    retrying on transient failures (network hiccups, malformed JSON) before
    giving up. Returns the parsed object, or raises the last error.
    """
    last_error = None

    for attempt in range(1, retries + 2):  # e.g. retries=2 -> 3 total attempts
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,  # deterministic-ish output helps JSON reliability
            )
            raw_text = response.choices[0].message.content
            return safe_json_parse(raw_text)

        except Exception as e:
            last_error = e
            logger.warning(f"LLM call attempt {attempt} failed: {e}")
            if attempt <= retries:
                time.sleep(backoff_seconds)

    raise RuntimeError(f"LLM call failed after {retries + 1} attempts: {last_error}")
