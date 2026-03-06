"use client";

import { useState, useRef } from "react";
import Link from "next/link";
import { THEMES, getThemedResumeHtml } from "@/lib/resume-themes";
import { getResumePdfFilename, parseResumeNameAndRole } from "@/lib/resume-utils";
import { type SavedItem, getSavedItems, setSavedItems } from "@/lib/resume-storage";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Status = "idle" | "loading" | "success" | "error";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [companyName, setCompanyName] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [status, setStatus] = useState<Status>("idle");
  const [error, setError] = useState<string | null>(null);
  const [resumeHtml, setResumeHtml] = useState<string | null>(null);
  const [selectedThemeId, setSelectedThemeId] = useState<string | null>(null);
  const [pdfLoading, setPdfLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const iframeRef = useRef<HTMLIFrameElement>(null);

  async function handleDownloadPdf() {
    if (!resumeHtml) return;
    setPdfLoading(true);
    try {
      const themedHtml = getThemedResumeHtml(resumeHtml, selectedThemeId);
      const res = await fetch(`${API_URL}/to-pdf`, {
        method: "POST",
        headers: { "Content-Type": "text/html; charset=utf-8" },
        body: themedHtml,
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || "PDF generation failed");
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = getResumePdfFilename(themedHtml);
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate PDF");
    } finally {
      setPdfLoading(false);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!file || !jobDescription.trim()) {
      setError("Please upload a PDF and enter the job description.");
      return;
    }
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setError("Please upload a PDF file.");
      return;
    }

    setError(null);
    setStatus("loading");
    setResumeHtml(null);

    const formData = new FormData();
    formData.append("resume", file);
    formData.append("job_description", jobDescription.trim());

    try {
      const res = await fetch(`${API_URL}/tailor`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `Request failed: ${res.status}`);
      }
      const html = await res.text();
      setResumeHtml(html);
      setSelectedThemeId(null);
      setStatus("success");

      const { role } = parseResumeNameAndRole(html);
      const newItem: SavedItem = {
        id: String(Date.now()),
        companyName: companyName.trim() || "—",
        jobDescription: jobDescription.trim(),
        resumeHtml: html,
        roleLine: role,
        createdAt: new Date().toISOString(),
      };
      setSavedItems([newItem, ...getSavedItems()]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
      setStatus("error");
    }
  }

  function handlePrint() {
    if (!resumeHtml) return;
    const themedHtml = getThemedResumeHtml(resumeHtml, selectedThemeId);
    const printScript =
      '<script>window.onload=function(){window.print();window.onafterprint=function(){window.close();}}</script>';
    const htmlWithPrint = /<\/body\s*>/i.test(themedHtml)
      ? themedHtml.replace(/<\/body\s*>/i, printScript + "</body>")
      : themedHtml + printScript;
    const blob = new Blob([htmlWithPrint], { type: "text/html; charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const w = window.open(url, "_blank", "noopener,noreferrer");
    if (!w) {
      URL.revokeObjectURL(url);
      // Fallback: iframe print
      const iframe = iframeRef.current;
      if (iframe?.contentWindow) {
        iframe.contentWindow.focus();
        iframe.contentWindow.print();
      }
      return;
    }
    // Revoke when the new window has loaded (it keeps a copy)
    w.onload = () => URL.revokeObjectURL(url);
    setTimeout(() => URL.revokeObjectURL(url), 10000);
  }

  return (
    <main className="page">
      <nav className="nav">
        <Link href="/" className="active">Resume Tailor AI</Link>
        <Link href="/history">History</Link>
      </nav>
      <div className="container">
        <header className="header">
          <h1>Resume Tailor AI</h1>
          <p className="tagline">
            Upload your resume (PDF) and paste the job description. We&apos;ll tailor your resume for a 100% match.
          </p>
        </header>

        <form onSubmit={handleSubmit} className="form">
          <label className="label">
            Resume (PDF)
          </label>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            className="fileInput"
          />

          <label className="label">
            Company name (optional)
          </label>
          <input
            type="text"
            value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
            placeholder="e.g. Acme Inc."
            className="textInput"
          />

          <label className="label">
            Job description
          </label>
          <textarea
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            placeholder="Paste the full job description here..."
            required
            className="textarea"
            rows={10}
          />
          <p className="hint">
            Key skills, responsibilities, and qualifications will be extracted and matched to your profile.
          </p>

          {error && <p className="error">{error}</p>}

          <button type="submit" disabled={status === "loading"} className="button">
            {status === "loading" ? "Generating…" : "Generate tailored resume"}
          </button>
        </form>

        {status === "success" && resumeHtml && (
          <section className="result">
            <div className="resultHeader">
              <h2>Your tailored resume</h2>
              <div className="resultActions">
                <label className="themeLabel">
                  Theme:
                  <select
                    value={selectedThemeId ?? ""}
                    onChange={(e) => setSelectedThemeId(e.target.value || null)}
                    className="themeSelect"
                  >
                    <option value="">Default</option>
                    {THEMES.map((t) => (
                      <option key={t.id} value={t.id}>
                        {t.name}
                      </option>
                    ))}
                  </select>
                </label>
                <button
                  type="button"
                  onClick={handleDownloadPdf}
                  disabled={pdfLoading}
                  className="button buttonPrimary"
                >
                  {pdfLoading ? "Generating PDF…" : "Download PDF"}
                </button>
                <button type="button" onClick={handlePrint} className="button buttonSecondary">
                  Open print view
                </button>
              </div>
            </div>
            <iframe
              ref={iframeRef}
              title="Tailored resume"
              srcDoc={getThemedResumeHtml(resumeHtml, selectedThemeId)}
              className="resumeIframe"
              sandbox="allow-same-origin"
            />
          </section>
        )}
      </div>

      <style jsx>{`
        .page {
          padding: 2rem 1rem;
          min-height: 100vh;
        }
        .nav {
          max-width: 720px;
          margin: 0 auto 1.5rem;
          display: flex;
          gap: 1rem;
        }
        .nav a {
          color: var(--color-midnight);
          font-weight: 600;
          text-decoration: none;
        }
        .nav a:hover {
          text-decoration: underline;
        }
        .nav a.active {
          text-decoration: underline;
        }
        .container {
          max-width: 720px;
          margin: 0 auto;
        }
        .header {
          margin-bottom: 2rem;
        }
        .header h1 {
          color: var(--color-midnight);
          font-size: 1.75rem;
          margin: 0 0 0.5rem 0;
        }
        .tagline {
          color: #444;
          margin: 0;
          font-size: 1rem;
        }
        .form {
          background: #fff;
          padding: 1.5rem;
          border-radius: 8px;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
        }
        .label {
          display: block;
          font-weight: bold;
          margin-top: 1rem;
          color: #333;
        }
        .label:first-of-type {
          margin-top: 0;
        }
        .fileInput {
          margin-top: 0.25rem;
          display: block;
          font-size: 0.95rem;
        }
        .textInput {
          width: 100%;
          margin-top: 0.25rem;
          padding: 0.65rem 0.75rem;
          font-size: 0.95rem;
          border: 1px solid #ccc;
          border-radius: 6px;
        }
        .textInput:focus {
          outline: none;
          border-color: var(--color-midnight);
        }
        .textarea {
          width: 100%;
          margin-top: 0.25rem;
          padding: 0.75rem;
          font-family: inherit;
          font-size: 0.95rem;
          border: 1px solid #ccc;
          border-radius: 6px;
          resize: vertical;
        }
        .textarea:focus {
          outline: none;
          border-color: var(--color-midnight);
          box-shadow: 0 0 0 2px rgba(25, 25, 112, 0.15);
        }
        .hint {
          font-size: 0.8rem;
          color: #666;
          margin: 0.25rem 0 0 0;
        }
        .error {
          color: #c00;
          margin: 1rem 0 0 0;
          font-size: 0.9rem;
        }
        .button {
          margin-top: 1.25rem;
          padding: 0.65rem 1.25rem;
          background: var(--color-midnight);
          color: #fff;
          border: none;
          border-radius: 6px;
          font-size: 1rem;
          font-weight: 600;
          cursor: pointer;
        }
        .button:hover:not(:disabled) {
          opacity: 0.92;
        }
        .button:disabled {
          opacity: 0.7;
          cursor: not-allowed;
        }
        .result {
          margin-top: 2rem;
          background: #fff;
          border-radius: 8px;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
          overflow: hidden;
        }
        .resultHeader {
          display: flex;
          align-items: center;
          justify-content: space-between;
          flex-wrap: wrap;
          gap: 0.75rem;
          padding: 1rem 1.5rem;
          border-bottom: 1px solid #eee;
        }
        .resultHeader h2 {
          margin: 0;
          font-size: 1.15rem;
          color: #333;
        }
        .resultActions {
          display: flex;
          gap: 0.5rem;
          flex-wrap: wrap;
          align-items: center;
        }
        .themeLabel {
          display: inline-flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 0.9rem;
          font-weight: 600;
          color: #333;
        }
        .themeSelect {
          padding: 0.4rem 0.6rem;
          font-size: 0.9rem;
          border: 1px solid #ccc;
          border-radius: 6px;
          background: #fff;
          min-width: 180px;
        }
        .buttonPrimary {
          background: var(--color-midnight);
        }
        .buttonSecondary {
          background: #444;
        }
        .resumeIframe {
          display: block;
          width: 100%;
          min-height: 900px;
          border: none;
          background: #fff;
        }
      `}</style>
    </main>
  );
}
