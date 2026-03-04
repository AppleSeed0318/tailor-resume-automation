"""
FastAPI app: upload resume PDF, paste job description, get tailored Markdown + HTML.
"""

import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, PlainTextResponse, Response

from resume_tailor.llm_extract import extract_job_description, extract_resume_profile
from resume_tailor.html_to_pdf import html_to_pdf
from resume_tailor.pdf_extract import extract_text_from_pdf
from resume_tailor.pipeline import load_css
from resume_tailor.render import render_html, render_markdown
from resume_tailor.tailor import tailor_resume

app = FastAPI(title="Resume Tailor AI", description="Tailor your resume to any job description.")

# CORS: allow any origin by default so anyone can access from their PC.
# To restrict to specific origins, set CORS_ORIGINS=http://localhost:3000,https://yoursite.com
_origins = os.environ.get("CORS_ORIGINS", "").strip()
if _origins == "" or _origins == "*":
    _app_origins = ["*"]
    _allow_credentials = False
else:
    _app_origins = [o.strip() for o in _origins.split(",") if o.strip()]
    _allow_credentials = True
    if not _app_origins:
        _app_origins = ["*"]
        _allow_credentials = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=_app_origins,
    allow_credentials=_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.get("/")
def home() -> HTMLResponse:
    """Simple upload form."""
    return HTMLResponse(
        """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <title>Resume Tailor AI</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 640px; margin: 40px auto; padding: 20px; }
    h1 { color: MidnightBlue; }
    label { display: block; margin-top: 12px; font-weight: bold; }
    textarea { width: 100%; height: 200px; margin-top: 4px; padding: 8px; }
    input[type=file] { margin-top: 4px; }
    button { margin-top: 16px; padding: 10px 20px; background: MidnightBlue; color: white; border: none; cursor: pointer; }
    button:hover { opacity: 0.9; }
    .hint { font-size: 12px; color: #666; margin-top: 4px; }
  </style>
</head>
<body>
  <h1>Resume Tailor AI</h1>
  <p>Upload your resume (PDF) and paste the job description. We'll tailor your resume for a 100% match.</p>
  <form action="/tailor" method="post" enctype="multipart/form-data">
    <label>Resume (PDF)</label>
    <input type="file" name="resume" accept=".pdf" required />
    <label>Job description</label>
    <textarea name="job_description" required placeholder="Paste the full job description here..."></textarea>
    <p class="hint">Key skills, responsibilities, and qualifications will be extracted and matched to your profile.</p>
    <button type="submit">Generate tailored resume</button>
  </form>
</body>
</html>
"""
    )


@app.post("/tailor")
async def tailor(
    resume: UploadFile = File(..., description="Resume PDF"),
    job_description: str = Form(..., description="Job description text"),
) -> HTMLResponse:
    """Process upload + JD, return tailored resume as styled HTML (print to PDF)."""
    if not resume.filename or not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Please upload a PDF file.")

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        content = await resume.read()
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        resume_text = extract_text_from_pdf(tmp_path)
    except Exception as e:
        raise HTTPException(400, f"Could not read PDF: {e}") from e
    finally:
        tmp_path.unlink(missing_ok=True)

    profile = extract_resume_profile(resume_text)
    jd_extract = extract_job_description(job_description)
    tailored = tailor_resume(profile, jd_extract)
    html = render_html(tailored, load_css())
    return HTMLResponse(html)


@app.post("/tailor/markdown")
async def tailor_markdown(
    resume: UploadFile = File(..., description="Resume PDF"),
    job_description: str = Form(..., description="Job description text"),
) -> PlainTextResponse:
    """Same as /tailor but returns Markdown only."""
    if not resume.filename or not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Please upload a PDF file.")

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        content = await resume.read()
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        resume_text = extract_text_from_pdf(tmp_path)
    except Exception as e:
        raise HTTPException(400, f"Could not read PDF: {e}") from e
    finally:
        tmp_path.unlink(missing_ok=True)

    profile = extract_resume_profile(resume_text)
    jd_extract = extract_job_description(job_description)
    tailored = tailor_resume(profile, jd_extract)
    md = render_markdown(tailored)
    return PlainTextResponse(md, media_type="text/markdown")


@app.post("/to-pdf")
async def to_pdf(request: Request) -> Response:
    """Convert HTML to PDF. Body: raw HTML (Content-Type: text/html). Returns PDF file."""
    body = await request.body()
    html = body.decode("utf-8")
    if not html.strip():
        raise HTTPException(400, "Empty HTML")
    try:
        pdf_bytes = await html_to_pdf(html)
    except RuntimeError as e:
        raise HTTPException(503, str(e)) from e
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="resume_tailored.pdf"'},
    )


def main() -> None:
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
