"""Use OpenAI to extract structured profile from resume text and keywords from job description."""

import json
import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

RESUME_EXTRACT_SYSTEM = """You are an expert resume parser. Extract structured information from resume text.
Output valid JSON only. Preserve exact company names, job titles, and date ranges (do not modify or infer).
For education, preserve exact institution names and date ranges."""

RESUME_EXTRACT_USER = """Extract the following from this resume text. Return JSON with these keys (use empty arrays/strings if not found):
- name: string (full name)
- email: string
- mobile: string (phone number)
- location: string (city, state/country, or full address if present)
- summary: string (professional summary or objective, if any)
- education: array of {{ degree, institution, duration, score_or_grade }} (preserve exact institution name and duration)
- skills: array of strings (technical and soft skills)
- experience: array of {{ company, role, period, bullets }} where bullets is array of strings (preserve exact company, role, period)
- projects: array of {{ name, description, technologies_or_outcome }} 
- achievements: array of strings
- other_activities: array of strings (hobbies, volunteer, etc.)

Resume text:
---
{resume_text}
---"""

JD_EXTRACT_SYSTEM = """You are an expert job description analyzer. Extract key requirements and keywords for resume matching.
Output valid JSON only."""

JD_EXTRACT_USER = """From this job description, extract:
- job_title: string
- skills: array of strings (technical skills, tools, frameworks mentioned)
- qualifications: array of strings (degree level, certifications, experience years)
- responsibilities: array of strings (key responsibilities)
- keywords: array of strings (important terms for ATS and matching)
- bonus_points: array of strings (items from "Bonus Points", "Nice to Have", "Preferred", or similar sections - e.g. "Familiar with Pixel Crushers' Dialogue System for Unity", "Familiar with XML processing using DOM, SAX, XSD", "Located in Seattle, Los Angeles, or Edmonton". Keep each as a short phrase or sentence.)

Job description:
---
{jd_text}
---"""


def _client() -> "OpenAI":
    if OpenAI is None:
        raise ImportError("Install openai: pip install openai")
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise ValueError("Set OPENAI_API_KEY in environment or .env")
    return OpenAI(api_key=key)


def _model() -> str:
    return os.environ.get("OPENAI_MODEL", "gpt-4o-mini")


def extract_resume_profile(resume_text: str) -> dict[str, Any]:
    """Extract structured profile from raw resume text using OpenAI."""
    client = _client()
    resp = client.chat.completions.create(
        model=_model(),
        messages=[
            {"role": "system", "content": RESUME_EXTRACT_SYSTEM},
            {"role": "user", "content": RESUME_EXTRACT_USER.format(resume_text=resume_text)},
        ],
        temperature=0.1,
    )
    raw = resp.choices[0].message.content
    # Strip markdown code block if present
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0]
    return json.loads(raw.strip())


def extract_job_description(jd_text: str) -> dict[str, Any]:
    """Extract skills, qualifications, and keywords from job description."""
    client = _client()
    resp = client.chat.completions.create(
        model=_model(),
        messages=[
            {"role": "system", "content": JD_EXTRACT_SYSTEM},
            {"role": "user", "content": JD_EXTRACT_USER.format(jd_text=jd_text)},
        ],
        temperature=0.1,
    )
    raw = resp.choices[0].message.content
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0]
    return json.loads(raw.strip())
