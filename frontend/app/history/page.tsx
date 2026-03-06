"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { getSavedItems, type SavedItem } from "@/lib/resume-storage";
import { getThemedResumeHtml } from "@/lib/resume-themes";
import { getResumePdfFilename, parseResumeNameAndRole } from "@/lib/resume-utils";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const PAGE_SIZE = 10;

export default function HistoryPage() {
  const [items, setItems] = useState<SavedItem[]>([]);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [pdfLoading, setPdfLoading] = useState(false);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  useEffect(() => {
    setItems(getSavedItems());
  }, []);

  const filtered = items.filter((item) =>
    item.companyName.toLowerCase().includes(search.trim().toLowerCase())
  );
  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const currentPage = Math.min(page, totalPages);
  const start = (currentPage - 1) * PAGE_SIZE;
  const pageItems = filtered.slice(start, start + PAGE_SIZE);
  const selectedItem = selectedId ? items.find((i) => i.id === selectedId) : null;

  async function handleDownloadPdf(item: SavedItem) {
    setDownloadError(null);
    setPdfLoading(true);
    try {
      const themedHtml = getThemedResumeHtml(item.resumeHtml, null);
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
      setDownloadError(err instanceof Error ? err.message : "Failed to generate PDF");
    } finally {
      setPdfLoading(false);
    }
  }

  return (
    <main className="page">
      <nav className="nav">
        <Link href="/">Resume Tailor AI</Link>
        <Link href="/history" className="active">History</Link>
      </nav>
      <div className="container">
        <header className="header">
          <h1>Saved resumes</h1>
          <p className="tagline">Search by company name and click a row to view details.</p>
        </header>

        <div className="toolbar">
          <input
            type="text"
            placeholder="Search by company name..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            className="searchInput"
          />
        </div>

        {filtered.length === 0 ? (
          <p className="empty">
            {items.length === 0
              ? "No saved resumes yet. Generate a tailored resume on the home page."
              : "No matches for that company name."}
          </p>
        ) : (
          <>
            <table className="table">
              <thead>
                <tr>
                  <th>Profile name</th>
                  <th>Company</th>
                  <th>Role</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {pageItems.map((item) => (
                  <tr
                    key={item.id}
                    className={selectedId === item.id ? "selected" : ""}
                    onClick={() => setSelectedId(selectedId === item.id ? null : item.id)}
                  >
                    <td>{parseResumeNameAndRole(item.resumeHtml).name}</td>
                    <td>{item.companyName}</td>
                    <td>{item.roleLine}</td>
                    <td>{new Date(item.createdAt).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>

            {totalPages > 1 && (
              <div className="pagination">
                <button
                  type="button"
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={currentPage <= 1}
                  className="pageBtn"
                >
                  Previous
                </button>
                <span className="pageInfo">
                  Page {currentPage} of {totalPages} ({filtered.length} total)
                </span>
                <button
                  type="button"
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={currentPage >= totalPages}
                  className="pageBtn"
                >
                  Next
                </button>
              </div>
            )}

            {selectedItem && (
              <div className="detail">
                <div className="detailActions">
                  <button type="button" className="closeBtn" onClick={() => setSelectedId(null)}>
                    Close
                  </button>
                  <button
                    type="button"
                    className="downloadBtn"
                    onClick={() => handleDownloadPdf(selectedItem)}
                    disabled={pdfLoading}
                  >
                    {pdfLoading ? "Generating PDF…" : "Download PDF"}
                  </button>
                </div>
                {downloadError && <p className="downloadError">{downloadError}</p>}
                <h3>Company</h3>
                <p className="detailCompany">{selectedItem.companyName}</p>
                <h3>Job description</h3>
                <pre className="detailJd">{selectedItem.jobDescription}</pre>
                <h3>Resume</h3>
                <iframe
                  title="Saved resume"
                  srcDoc={selectedItem.resumeHtml}
                  className="detailIframe"
                  sandbox="allow-same-origin"
                />
              </div>
            )}
          </>
        )}
      </div>

      <style jsx>{`
        .page {
          padding: 2rem 1rem;
          min-height: 100vh;
          background: #f5f5f5;
        }
        .nav {
          max-width: 900px;
          margin: 0 auto 1.5rem;
          display: flex;
          gap: 1rem;
        }
        .nav a {
          color: var(--color-midnight, #191970);
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
          max-width: 900px;
          margin: 0 auto;
        }
        .header {
          margin-bottom: 1.5rem;
        }
        .header h1 {
          color: var(--color-midnight, #191970);
          font-size: 1.75rem;
          margin: 0 0 0.5rem 0;
        }
        .tagline {
          color: #444;
          margin: 0;
          font-size: 1rem;
        }
        .toolbar {
          margin-bottom: 1rem;
        }
        .searchInput {
          width: 100%;
          max-width: 320px;
          padding: 0.6rem 0.75rem;
          font-size: 1rem;
          border: 1px solid #ccc;
          border-radius: 6px;
        }
        .searchInput:focus {
          outline: none;
          border-color: var(--color-midnight, #191970);
        }
        .empty {
          background: #fff;
          padding: 2rem;
          border-radius: 8px;
          color: #666;
          margin: 0;
        }
        .table {
          width: 100%;
          border-collapse: collapse;
          background: #fff;
          border-radius: 8px;
          overflow: hidden;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
        }
        .table th,
        .table td {
          text-align: left;
          padding: 0.75rem 1rem;
          border-bottom: 1px solid #eee;
        }
        .table th {
          font-weight: 600;
          color: #555;
          background: #fafafa;
        }
        .table tbody tr {
          cursor: pointer;
        }
        .table tbody tr:hover {
          background: #f8f8f8;
        }
        .table tbody tr.selected {
          background: #e8eeff;
        }
        .pagination {
          display: flex;
          align-items: center;
          gap: 1rem;
          margin-top: 1rem;
          flex-wrap: wrap;
        }
        .pageBtn {
          padding: 0.5rem 1rem;
          font-size: 0.9rem;
          border: 1px solid #ccc;
          border-radius: 6px;
          background: #fff;
          cursor: pointer;
        }
        .pageBtn:hover:not(:disabled) {
          background: #f0f0f0;
        }
        .pageBtn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
        .pageInfo {
          font-size: 0.9rem;
          color: #666;
        }
        .detail {
          margin-top: 1.5rem;
          padding: 1.5rem;
          background: #fff;
          border-radius: 8px;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
        }
        .detail h3 {
          margin: 1rem 0 0.5rem 0;
          font-size: 1rem;
          color: #333;
        }
        .detail h3:first-of-type {
          margin-top: 0;
        }
        .detailActions {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          flex-wrap: wrap;
          margin-bottom: 0.5rem;
        }
        .downloadBtn {
          padding: 0.4rem 0.75rem;
          font-size: 0.9rem;
          background: var(--color-midnight, #191970);
          color: #fff;
          border: none;
          border-radius: 6px;
          cursor: pointer;
        }
        .downloadBtn:hover:not(:disabled) {
          opacity: 0.9;
        }
        .downloadBtn:disabled {
          opacity: 0.7;
          cursor: not-allowed;
        }
        .downloadError {
          color: #c00;
          font-size: 0.9rem;
          margin: 0 0 0.5rem 0;
        }
        .closeBtn {
          padding: 0.4rem 0.75rem;
          font-size: 0.9rem;
          background: #eee;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          margin-bottom: 0.5rem;
        }
        .closeBtn:hover {
          background: #ddd;
        }
        .detailCompany {
          margin: 0;
          font-size: 0.95rem;
        }
        .detailJd {
          margin: 0;
          padding: 0.75rem;
          background: #f5f5f5;
          border-radius: 6px;
          font-size: 0.85rem;
          white-space: pre-wrap;
          word-break: break-word;
          max-height: 200px;
          overflow: auto;
        }
        .detailIframe {
          width: 100%;
          min-height: 700px;
          border: 1px solid #eee;
          border-radius: 6px;
          margin-top: 0.5rem;
        }
      `}</style>
    </main>
  );
}
