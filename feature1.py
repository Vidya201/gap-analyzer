# feature1.py - Extract skills from user resume using Groq LLM

import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("groq_key"))

def extract_skills(resume_text):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": f"""Extract all technical skills from this resume text.
                Return ONLY a JSON array of skills. Nothing else.
                Example: ["Python", "SQL", "React", "Git"]
                
                Resume text:
                {resume_text}"""
            }
        ]
    )
    result = response.choices[0].message.content
    skills = json.loads(result)
    print("user skills:", skills)
    return skills


# test
if __name__ == "__main__":
    with open("VIDYA M.txt", "r", encoding="utf8") as f:
        resume_text = f.read()
    skills = extract_skills(resume_text)
    print("Extracted skills:", skills)
