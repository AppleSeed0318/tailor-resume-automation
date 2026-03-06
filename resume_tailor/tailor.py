"""Tailor resume content to job description using OpenAI. Preserve companies, periods, and institutions."""

import json
import os
import random
import re
from typing import Any

from dotenv import load_dotenv

load_dotenv()

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

TAILOR_SYSTEM = """You tailor resumes to job descriptions. Output valid JSON only.

Rules: Keep every company name and period unchanged. Keep every education institution and duration unchanged. You may change job role/title per entry to match JD. 4-10 bullets per job, tailored to JD. Summary: match job title; do not mention employment type (Part-Time/Full-Time/Contract); must state "10 years of experience" (or "10+ years"); highlight top 3-5 JD skills. skills_by_category: keep ~90%+ of candidate skills; preserve all categories; add 1-2 JD skills per category if relevant. Same number of experience and education entries."""

TAILOR_USER = """Tailor the candidate profile to the job. Return one JSON object.

Candidate:
{profile_json}

Job:
{jd_json}

Keys: summary (string; include "10 years of experience", highlight top 3-5 JD skills, no Part-Time/Full-Time/Contract), skills ([string]), skills_by_category (object: category -> [skills]; keep ~90% candidate skills), experience ([{{company, role, period, bullets}}]; company/period unchanged, 4-10 bullets), education ([{{degree, institution, duration, score_or_grade}}]; all entries, institution/duration unchanged), projects ([{{name, description}}]), achievements ([string]), other_activities ([string])."""


def _client() -> "OpenAI":
    if OpenAI is None:
        raise ImportError("Install openai: pip install openai")
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise ValueError("Set OPENAI_API_KEY in environment or .env")
    return OpenAI(api_key=key)


def _model() -> str:
    return os.environ.get("OPENAI_MODEL", "gpt-4o-mini")


def tailor_resume(profile: dict[str, Any], jd_extract: dict[str, Any]) -> dict[str, Any]:
    """
    Tailor the resume content to the job description.
    Returns a full profile-like dict with tailored summary, skills, experience bullets, etc.,
    while preserving all company names, periods, and institution names/periods from profile.
    """
    client = _client()
    resp = client.chat.completions.create(
        model=_model(),
        messages=[
            {"role": "system", "content": TAILOR_SYSTEM},
            {
                "role": "user",
                "content": TAILOR_USER.format(
                    profile_json=json.dumps(profile),
                    jd_json=json.dumps(jd_extract),
                ),
            },
        ],
        temperature=0.3,
    )
    raw = resp.choices[0].message.content
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0]
    tailored = json.loads(raw.strip())

    # Enforce immutables from original profile
    name = profile.get("name") or ""
    email = profile.get("email") or ""
    mobile = profile.get("mobile") or ""

    # Ensure experience keeps company and period from profile; role can be tailored (don't overwrite role)
    exp_profile = {i: (e.get("company"), e.get("period")) for i, e in enumerate(profile.get("experience") or [])}
    exp_tailored = tailored.get("experience") or []
    for i, ex in enumerate(exp_tailored):
        if i in exp_profile:
            c, p = exp_profile[i]
            ex["company"] = c or ex.get("company")
            ex["period"] = p or ex.get("period")
            # role is left as tailored by LLM (can be "Senior Frontend Developer" etc.)

    # Ensure education keeps exact institution and duration; never drop any entry
    edu_profile = list(profile.get("education") or [])
    edu_tailored = tailored.get("education") or []
    for i, ed in enumerate(edu_tailored):
        if i < len(edu_profile):
            orig = edu_profile[i]
            ed["institution"] = orig.get("institution") or ed.get("institution")
            ed["duration"] = orig.get("duration") or ed.get("duration")
    # If LLM returned fewer education entries than profile has, append the missing ones
    for i in range(len(edu_tailored), len(edu_profile)):
        orig = edu_profile[i]
        edu_tailored.append({
            "degree": orig.get("degree") or "",
            "institution": orig.get("institution") or "",
            "duration": orig.get("duration") or "",
            "score_or_grade": orig.get("score_or_grade") or "",
        })

    tailored["name"] = name
    tailored["email"] = email
    tailored["mobile"] = mobile
    tailored["location"] = (profile.get("location") or "").strip()
    tailored["experience"] = exp_tailored
    tailored["education"] = edu_tailored

    # Summary: remove parentheticals like (Part-Time), (Full-Time), (Contract)
    if tailored.get("summary"):
        tailored["summary"] = _strip_summary_parentheticals(tailored["summary"])

    # Ensure 90%+ of base resume skills appear in skills_by_category (merge any missing)
    _ensure_base_skills_in_tailored(profile, tailored)

    # Mix skill order within each category (category titles stay the same)
    _shuffle_skills_within_categories(tailored)

    # Header role line: cleaned job title with Senior/Principal/Professional if missing | top 4 JD skills
    jd_title_raw = (jd_extract.get("job_title") or "").strip()
    jd_title = _normalize_role_line_title(jd_title_raw)
    jd_skills = jd_extract.get("skills") or []
    top_4 = [s.strip() for s in jd_skills[:4] if s and str(s).strip()]
    if jd_title or top_4:
        parts = [jd_title] if jd_title else []
        parts.extend(top_4)
        tailored["role_line"] = " | ".join(parts)

    return tailored


def _normalize_role_line_title(title: str) -> str:
    """Remove parentheticals (Part-Time, Full-Time, etc.) and ensure Senior/Principal/Professional prefix."""
    if not title:
        return ""
    # Remove parenthetical suffixes: (Part-Time), (Full-Time), (Contract), (Remote), etc.
    cleaned = re.sub(r"\s*\([^)]*\)\s*$", "", title).strip()
    # If already has a seniority prefix, return as-is
    if re.match(r"^(Senior|Principal|Lead|Staff|Professional|Chief)\s+", cleaned, re.I):
        return cleaned
    # Prepend "Senior " so it reads e.g. "Senior Frontend Developer"
    return f"Senior {cleaned}" if cleaned else ""


def _strip_summary_parentheticals(text: str) -> str:
    """Remove parentheticals like (Part-Time), (Full-Time), (Contract) from summary."""
    if not text:
        return text
    # Remove any (...) and collapse multiple spaces
    cleaned = re.sub(r"\s*\([^)]*\)\s*", " ", text)
    return re.sub(r"\s+", " ", cleaned).strip()


def _normalize_skill(s: str) -> str:
    """Normalize skill string for comparison (lowercase, strip)."""
    return (s or "").strip().lower()


def _shuffle_skills_within_categories(tailored: dict[str, Any]) -> None:
    """Shuffle the order of skills within each category; category titles are unchanged."""
    skills_by_cat = tailored.get("skills_by_category")
    if not isinstance(skills_by_cat, dict):
        return
    for cat, skill_list in skills_by_cat.items():
        if isinstance(skill_list, list) and len(skill_list) > 1:
            random.shuffle(skill_list)


def _ensure_base_skills_in_tailored(profile: dict[str, Any], tailored: dict[str, Any]) -> None:
    """Ensure at least 90% of profile skills appear in tailored skills_by_category; add missing to 'Other'."""
    base_skills = profile.get("skills") or []
    if not base_skills:
        return
    base_set = {_normalize_skill(s) for s in base_skills if (s and str(s).strip())}
    if not base_set:
        return

    skills_by_cat = tailored.get("skills_by_category")
    if not isinstance(skills_by_cat, dict):
        # No categories; set tailored to a single category with all base skills
        tailored["skills_by_category"] = {"Technical Skills": [str(s).strip() for s in base_skills if s]}
        return

    # Collect all skills currently in tailored (normalized)
    in_tailored = set()
    for skill_list in skills_by_cat.values():
        if isinstance(skill_list, list):
            for s in skill_list:
                if s:
                    in_tailored.add(_normalize_skill(str(s)))

    missing = base_set - in_tailored
    if not missing:
        return

    # Build original skill string -> display form (use first occurrence from base_skills)
    base_display = {}
    for s in base_skills:
        if not s:
            continue
        key = _normalize_skill(str(s))
        if key not in base_display:
            base_display[key] = str(s).strip()

    missing_display = [base_display[k] for k in missing if k in base_display]
    if not missing_display:
        return

    # Append missing skills to "Other" or "Additional Skills" category
    if "Other" in skills_by_cat and isinstance(skills_by_cat["Other"], list):
        skills_by_cat["Other"] = list(skills_by_cat["Other"]) + missing_display
    elif "Additional Skills" in skills_by_cat and isinstance(skills_by_cat["Additional Skills"], list):
        skills_by_cat["Additional Skills"] = list(skills_by_cat["Additional Skills"]) + missing_display
    else:
        skills_by_cat["Other"] = missing_display
