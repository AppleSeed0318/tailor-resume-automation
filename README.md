# Resume Tailor AI

Tailor your resume to any job description for a **100% match score**. The app:

1. **Extracts** your profile from an uploaded resume PDF (name, contact, education, skills, experience, projects, achievements) using OpenAI.
2. **Extracts** key skills, qualifications, and keywords from the job description.
3. **Tailors** the resume by:
   - **Adding** relevant skills from the JD.
   - **Updating** the professional summary.
   - **Rewriting** work experience bullets to match the role (with measurable results where possible).
   - **Preserving** employment history (company names and periods) and education (institution names and periods)—no removal or modification of those.

Output: **Markdown** and **styled HTML** (Arial/Helvetica, MidnightBlue headings, clean layout). Open the HTML in a browser and use **Print → Save as PDF** to get a PDF.

---

## Setup

```bash
cd E:\Hobby\TailorAI\cursor
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
copy .env.example .env
# Edit .env and set OPENAI_API_KEY=your_key
```

Optional: set `OPENAI_MODEL=gpt-4o` in `.env` for higher quality (default is `gpt-4o-mini`).

**PDF download (backend-generated PDF):**  
Install Playwright and Chromium so the backend can generate PDFs:

```bash
pip install playwright
playwright install chromium
```

---

## Usage

### Next.js frontend (recommended)

1. **Start the backend** (from project root):

```bash
.venv\Scripts\activate
python app.py
# Backend runs at http://localhost:8000
```

2. **Start the Next.js frontend**:

```bash
cd frontend
cp .env.local.example .env.local   # optional; default API URL is http://localhost:8000
npm install
npm run dev
# Frontend runs at http://localhost:3000
```

3. Open **http://localhost:3000** → upload your resume (PDF) and paste the job description → **Generate tailored resume**. Use **Download PDF** to get a server-generated PDF, or **Open print view** to use the browser’s print dialog.

### Legacy web app (FastAPI only)

```bash
python app.py
# or: uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Open http://localhost:8000 → upload your resume PDF and paste the job description → **Generate tailored resume**. You get styled HTML; use the browser’s **Print → Save as PDF** to export.

- **Markdown**: POST to `/tailor/markdown` with form fields `resume` (file) and `job_description` (text).

### CLI (local PDF + JD file or stdin)

```bash
# JD in a file
python cli.py path/to/resume.pdf path/to/job_description.txt

# JD from stdin (paste, then Ctrl+Z + Enter on Windows or Ctrl+D on Unix)
python cli.py path/to/resume.pdf --stdin

# JD as a single string argument
python cli.py path/to/resume.pdf "Job description text here..."
```

Writes `resume_tailored.md` and `resume_tailored.html` in the current directory.

---

## Project layout

| Path | Purpose |
|------|--------|
| `frontend/` | **Next.js** app: upload PDF, enter JD, view/print tailored resume |
| `app.py` | FastAPI backend: PDF + JD → tailored HTML/Markdown |
| `cli.py` | CLI: local PDF + JD file/stdin → `.md` + `.html` |
| `resume_tailor/` | Core library |
| `resume_tailor/pdf_extract.py` | Extract text from PDF |
| `resume_tailor/html_to_pdf.py` | HTML → PDF via Playwright (Chromium) |
| `resume_tailor/llm_extract.py` | OpenAI: resume → profile, JD → keywords |
| `resume_tailor/tailor.py` | OpenAI: tailor content (preserve companies/periods/institutions) |
| `resume_tailor/render.py` | Build Markdown and HTML from tailored data |
| `resume_tailor/pipeline.py` | End-to-end: PDF + JD → MD + HTML |
| `styles/resume.css` | Resume styling (Arial, MidnightBlue headings, print-friendly) |

---

## CSS styling (resume output)

- **Font**: Arial, Helvetica
- **Header**: Name and contact in large, bold, centered text
- **Headings**: MidnightBlue, uppercase, with bottom border
- **Sections**: Clear titles (Education, Experience, Skills, etc.) and bullet points with padding/margins

The same styling is used in the generated HTML so that printing to PDF looks professional.
