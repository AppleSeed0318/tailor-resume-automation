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

RESUME_EXTRACT_SYSTEM = """You are a resume parser. Output valid JSON only. Preserve exact company names, job titles, date ranges, and institution names."""

RESUME_EXTRACT_USER = """Extract from the resume below. Return JSON with these keys (empty string or [] if missing):
name, email, mobile, location, summary (strings)
education: [{{degree, institution, duration, score_or_grade}}]
skills: [string]
experience: [{{company, role, period, bullets}}]
projects: [{{name, description, technologies_or_outcome}}]
achievements: [string], other_activities: [string]
Preserve exact companies, periods, institutions.

Resume:
---
{resume_text}
---"""

JD_EXTRACT_SYSTEM = """Extract job requirements as JSON. Output valid JSON only."""

JD_EXTRACT_USER = """From the job description extract JSON:
job_title, skills: [string], qualifications: [string], responsibilities: [string], keywords: [string]
bonus_points: [string] (from "Bonus Points", "Nice to Have", "Preferred" - short phrases)
Preserve exact wording where it matters.

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
