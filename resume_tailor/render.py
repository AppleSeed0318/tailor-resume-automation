"""Render tailored resume to Markdown and HTML (with CSS) for PDF conversion."""

from typing import Any


def _escape_md(s: str) -> str:
    if not s:
        return ""
    return str(s).strip()


def render_markdown(data: dict[str, Any]) -> str:
    """Produce Markdown resume from tailored profile dict."""
    lines = []

    # Header
    name = _escape_md(data.get("name") or "Name")
    email = _escape_md(data.get("email") or "")
    mobile = _escape_md(data.get("mobile") or "")
    location = _escape_md(data.get("location") or "")
    role_line = _escape_md(data.get("role_line") or "")
    contact_parts = [p for p in [email, mobile, location] if p]
    if name or contact_parts:
        lines.append(f"# {name}\n")
        if role_line:
            lines.append(f"**{role_line}**\n")
        if contact_parts:
            lines.append("**" + " | ".join(contact_parts) + "**\n")

    # Summary
    summary = _escape_md(data.get("summary"))
    if summary:
        lines.append("## Professional Summary\n")
        lines.append(f"{summary}\n")

    # Skills: structured by category (CORE TECHNICAL SKILLS) or flat fallback
    skills_by_category = data.get("skills_by_category") or {}
    if isinstance(skills_by_category, dict) and skills_by_category:
        lines.append("## Core Technical Skills\n")
        for cat, skill_list in skills_by_category.items():
            if not cat or not skill_list:
                continue
            skills_str = ", ".join(str(s).strip() for s in skill_list if s)
            if skills_str:
                lines.append(f"**{_escape_md(str(cat))}:** {skills_str}\n")
    else:
        skills = data.get("skills") or []
        if skills:
            lines.append("## Skills\n")
            lines.append(", ".join(str(s).strip() for s in skills if s) + "\n")

    # Experience
    exp = data.get("experience") or []
    if exp:
        lines.append("## Experience\n")
        for job in exp:
            company = _escape_md(job.get("company") or "Company")
            role = _escape_md(job.get("role") or "Role")
            period = _escape_md(job.get("period") or "")
            lines.append(f"**{role}** — *{company}*")
            if period:
                lines.append(f" ({period})")
            lines.append("\n\n")
            for b in job.get("bullets") or []:
                if b:
                    lines.append(f"- {_escape_md(str(b))}")
            lines.append("\n")

    # Education
    edu = data.get("education") or []
    if edu:
        lines.append("## Education\n")
        for e in edu:
            degree = _escape_md(e.get("degree") or "")
            institution = _escape_md(e.get("institution") or "")
            duration = _escape_md(e.get("duration") or "")
            score = _escape_md(e.get("score_or_grade") or "")
            line = f"**{degree}**"
            if institution:
                line += f", {institution}"
            if duration:
                line += f" — {duration}"
            if score:
                line += f" ({score})"
            lines.append(line + "\n")
        lines.append("\n")

    # Projects
    projects = data.get("projects") or []
    if projects:
        lines.append("## Projects\n")
        for p in projects:
            name = _escape_md(p.get("name") if isinstance(p, dict) else str(p))
            desc = _escape_md(p.get("description") if isinstance(p, dict) else "")
            if name:
                lines.append(f"- **{name}**: {desc}\n" if desc else f"- **{name}**\n")
        lines.append("\n")

    # Achievements
    achievements = data.get("achievements") or []
    if achievements:
        lines.append("## Achievements\n")
        for a in achievements:
            if a:
                lines.append(f"- {_escape_md(str(a))}")
        lines.append("\n")

    # Other activities
    other = data.get("other_activities") or []
    if other:
        lines.append("## Other Activities\n")
        for o in other:
            if o:
                lines.append(f"- {_escape_md(str(o))}")
        lines.append("\n")

    return "\n".join(lines).strip()


def render_html(data: dict[str, Any], css_content: str) -> str:
    """Produce a full HTML document with embedded CSS for print-to-PDF."""
    name = _escape_md(data.get("name") or "Name")
    email = _escape_md(data.get("email") or "")
    mobile = _escape_md(data.get("mobile") or "")
    location = _escape_md(data.get("location") or "")
    role_line = _escape_md(data.get("role_line") or "")

    contact_parts = [p for p in [email, mobile, location] if p]
    contact_html = " • ".join(contact_parts) if contact_parts else ""

    summary = _escape_md(data.get("summary") or "")
    summary_html = f'<p class="resume-summary">{summary}</p>' if summary else ""

    skills = data.get("skills") or []
    skills_by_category = data.get("skills_by_category") or {}
    skills_html = ""
    if isinstance(skills_by_category, dict) and skills_by_category:
        parts = []
        for cat, skill_list in skills_by_category.items():
            if not cat or not skill_list:
                continue
            skills_str = ", ".join(str(s).strip() for s in skill_list if s)
            if skills_str:
                parts.append(f'<div class="skills-category"><span class="skills-category-name">{_escape_md(str(cat))}:</span> {_escape_md(skills_str)}</div>')
        skills_html = "\n  ".join(parts) if parts else ""
    elif skills:
        items = "".join(f"<li>{_escape_md(str(s))}</li>" for s in skills if s)
        skills_html = f'<ul class="skills-list">{items}</ul>'

    exp = data.get("experience") or []
    exp_html = ""
    for job in exp:
        company = _escape_md(job.get("company") or "")
        role = _escape_md(job.get("role") or "")
        period = _escape_md(job.get("period") or "")
        bullets = job.get("bullets") or []
        bl = "".join(f"<li>{_escape_md(str(b))}</li>" for b in bullets if b)
        exp_html += f'''
<div class="resume-block">
  <p class="block-title">{role} — {company}</p>
  <p class="block-subtitle">{period}</p>
  <ul>{bl}</ul>
</div>'''

    edu = data.get("education") or []
    edu_html = ""
    for e in edu:
        degree = _escape_md(e.get("degree") or "")
        institution = _escape_md(e.get("institution") or "")
        duration = _escape_md(e.get("duration") or "")
        score = _escape_md(e.get("score_or_grade") or "")
        line = degree
        if institution:
            line += f", {institution}"
        if duration:
            line += f" — {duration}"
        if score:
            line += f" ({score})"
        edu_html += f'<div class="resume-block"><p class="block-title">{line}</p></div>'

    projects = data.get("projects") or []
    proj_html = ""
    if projects:
        items = []
        for p in projects:
            n = _escape_md(p.get("name") if isinstance(p, dict) else str(p))
            d = _escape_md(p.get("description") if isinstance(p, dict) else "")
            items.append(f"<li><strong>{n}</strong>: {d}</li>" if d else f"<li><strong>{n}</strong></li>")
        proj_html = f"<ul class=\"resume-list\">{''.join(items)}</ul>"

    achievements = data.get("achievements") or []
    ach_html = ""
    if achievements:
        ach_html = "<ul class=\"resume-list\">" + "".join(f"<li>{_escape_md(str(a))}</li>" for a in achievements if a) + "</ul>"

    other = data.get("other_activities") or []
    other_html = ""
    if other:
        other_html = "<ul class=\"resume-list\">" + "".join(f"<li>{_escape_md(str(o))}</li>" for o in other if o) + "</ul>"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Resume - {name}</title>
  <style>
{css_content}
  </style>
</head>
<body>
  <header class="resume-header">
    <h1 class="name">{name}</h1>
    {f'<p class="role-line">{role_line}</p>' if role_line else ''}
    <p class="contact">{contact_html}</p>
  </header>

  {f'<h2 class="section-title">Professional Summary</h2>{summary_html}' if summary else ''}

  {f'<h2 class="section-title">Core Technical Skills</h2>{skills_html}' if (skills_by_category or skills) else ''}

  {f'<h2 class="section-title">Experience</h2>{exp_html}' if exp else ''}

  {f'<h2 class="section-title">Education</h2>{edu_html}' if edu else ''}

  {f'<h2 class="section-title">Projects</h2>{proj_html}' if projects else ''}

  {f'<h2 class="section-title">Achievements</h2>{ach_html}' if achievements else ''}

  {f'<h2 class="section-title">Other Activities</h2>{other_html}' if other else ''}
</body>
</html>"""
