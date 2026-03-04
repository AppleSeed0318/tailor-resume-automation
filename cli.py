"""
CLI: Generate tailored resume from a local PDF and job description (file or stdin).
Usage:
  python cli.py path/to/resume.pdf path/to/job_description.txt
  python cli.py path/to/resume.pdf --stdin   # paste JD, then Ctrl+Z Enter (Windows) or Ctrl+D (Unix)
  python cli.py path/to/resume.pdf "Paste job description here as one string"
Output: writes resume_tailored.md and resume_tailored.html to current directory.
"""

import sys
from pathlib import Path

# Run from project root so resume_tailor is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))

from resume_tailor.pipeline import run


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python cli.py <resume.pdf> [job_description.txt or --stdin or \"JD text\"]", file=sys.stderr)
        sys.exit(1)

    pdf_path = Path(sys.argv[1])
    if not pdf_path.exists():
        print(f"Error: PDF not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    if len(sys.argv) == 2:
        print("Enter job description (end with Ctrl+Z then Enter on Windows, Ctrl+D on Unix):", file=sys.stderr)
        jd = sys.stdin.read()
    elif sys.argv[2] == "--stdin":
        jd = sys.stdin.read()
    elif len(sys.argv) == 3 and Path(sys.argv[2]).exists():
        jd = Path(sys.argv[2]).read_text(encoding="utf-8")
    else:
        jd = " ".join(sys.argv[2:])

    jd = jd.strip()
    if not jd:
        print("Error: Job description is empty.", file=sys.stderr)
        sys.exit(1)

    out_dir = Path.cwd()
    md_path = out_dir / "resume_tailored.md"
    html_path = out_dir / "resume_tailored.html"

    print("Extracting from PDF...", file=sys.stderr)
    print("Extracting JD requirements...", file=sys.stderr)
    print("Tailoring resume...", file=sys.stderr)
    md, html = run(pdf_path, jd, output_md_path=md_path, output_html_path=html_path)
    print(f"Wrote {md_path}", file=sys.stderr)
    print(f"Wrote {html_path} (open in browser and Print to PDF)", file=sys.stderr)


if __name__ == "__main__":
    main()
