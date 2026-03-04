"""
Pipeline: PDF + Job Description -> Tailored Markdown + HTML (with CSS).
Run from project root with OPENAI_API_KEY set.
"""

from pathlib import Path

from resume_tailor.llm_extract import extract_job_description, extract_resume_profile
from resume_tailor.pdf_extract import extract_text_from_pdf
from resume_tailor.render import render_html, render_markdown
from resume_tailor.tailor import tailor_resume


def load_css() -> str:
    path = Path(__file__).resolve().parent.parent / "styles" / "resume.css"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def run(
    pdf_path: str | Path,
    job_description: str,
    *,
    output_md_path: str | Path | None = None,
    output_html_path: str | Path | None = None,
) -> tuple[str, str]:
    """
    Extract profile from PDF, tailor to job description, return (markdown, html).
    Optionally write output_md_path and output_html_path.
    """
    # 1. Extract text from PDF
    resume_text = extract_text_from_pdf(pdf_path)

    # 2. Extract structured profile and JD requirements
    profile = extract_resume_profile(resume_text)
    jd_extract = extract_job_description(job_description)

    # 3. Tailor resume (preserve companies, periods, institutions)
    tailored = tailor_resume(profile, jd_extract)

    # 4. Render Markdown and HTML
    md = render_markdown(tailored)
    css = load_css()
    html = render_html(tailored, css)

    if output_md_path:
        Path(output_md_path).write_text(md, encoding="utf-8")
    if output_html_path:
        Path(output_html_path).write_text(html, encoding="utf-8")

    return md, html
