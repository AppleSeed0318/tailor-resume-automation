"""Convert HTML to PDF using Playwright (headless Chromium)."""

from __future__ import annotations

import tempfile
from pathlib import Path

try:
    from playwright.async_api import async_playwright
except ImportError:
    async_playwright = None  # type: ignore


async def html_to_pdf(html: str) -> bytes:
    """Render HTML and return PDF bytes. Requires: pip install playwright && playwright install chromium."""
    if async_playwright is None:
        raise RuntimeError("Install playwright: pip install playwright && playwright install chromium")

    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    pdf_path = Path(tmp.name)
    tmp.close()

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.set_content(html, wait_until="networkidle")
            await page.pdf(
                path=str(pdf_path),
                format="A4",
                margin={"top": "0.5in", "bottom": "0.5in", "left": "0.5in", "right": "0.5in"},
                print_background=True,
            )
            await browser.close()
        return pdf_path.read_bytes()
    finally:
        pdf_path.unlink(missing_ok=True)
