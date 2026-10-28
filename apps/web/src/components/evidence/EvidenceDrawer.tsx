import { useEffect } from "react";

interface EvidenceDrawerProps {
  evidenceId: string;
  onClose: () => void;
}

// Synthetic evidence catalog for T01 preview
const SYNTHETIC_EVIDENCE_CATALOG: Record<string, {
  title: string;
  documentType: string;
  company: string;
  date: string;
  pdfPage: number;
  excerpt: string;
  sourceUrl: string;
}> = {
  "ev-preview-101": {
    title: "Infosys Limited Earnings Conference Call Transcript Q4 FY24",
    documentType: "Earnings Call Transcript",
    company: "Infosys Limited (INFY)",
    date: "April 18, 2024",
    pdfPage: 4,
    excerpt: "With that, our revenue growth guidance for FY '25 is 1% to 3% growth in constant currency. Our operating margin guidance for FY '25 is 20% to 22%.",
    sourceUrl: "https://www.infosys.com/investors/reports-filings/quarterly-results/2023-2024/q4/documents/transcripts/earningscall.pdf",
  },
  "ev-preview-102": {
    title: "HCL Technologies Financial Results Q2 FY26 Earnings Transcript",
    documentType: "Earnings Call Transcript",
    company: "HCL Technologies Limited (HCLTECH)",
    date: "October 14, 2026",
    pdfPage: 3,
    excerpt: "Our services business delivered 1.6% quarter-on-quarter constant currency growth, led by telecommunications and media verticals.",
    sourceUrl: "https://www.hcltech.com/investors/results-reports",
  },
  "ev-preview-103": {
    title: "TCS Corporate Announcement: Outcome of Board Meeting",
    documentType: "Exchange Filing",
    company: "Tata Consultancy Services Limited (TCS)",
    date: "October 27, 2026",
    pdfPage: 1,
    excerpt: "The Board of Directors at its meeting held today has declared an interim dividend of Rs. 10 per equity share of Re. 1 each.",
    sourceUrl: "https://www.nseindia.com/companies-listing/corporate-filings-announcements",
  },
  "ev-preview-104": {
    title: "Infosys Q1 FY25 Press Release & Fact Sheet",
    documentType: "Quarterly Results",
    company: "Infosys Limited (INFY)",
    date: "July 18, 2024",
    pdfPage: 2,
    excerpt: "FY25 revenue guidance revised to 3.0%-4.0% in constant currency. Operating margin guidance maintained at 20.0%-22.0%.",
    sourceUrl: "https://www.infosys.com/investors/reports-filings/quarterly-results/2024-2025/q1.html",
  },
  "ev-preview-105": {
    title: "Infosys Q2 FY25 Press Release & Fact Sheet",
    documentType: "Quarterly Results",
    company: "Infosys Limited (INFY)",
    date: "October 17, 2024",
    pdfPage: 2,
    excerpt: "FY25 revenue guidance revised to 3.75%-4.50% in constant currency.",
    sourceUrl: "https://www.infosys.com/investors/reports-filings/quarterly-results/2024-2025/q2.html",
  },
  "ev-preview-106": {
    title: "Infosys Q3 FY25 Earnings Call Transcript",
    documentType: "Earnings Call Transcript",
    company: "Infosys Limited (INFY)",
    date: "January 16, 2025",
    pdfPage: 5,
    excerpt: "FY25 revenue growth guidance narrowed to 4.5%-5.0% in constant currency. Margin guidance unchanged at 21.0%-22.0%.",
    sourceUrl: "https://www.infosys.com/investors/reports-filings/quarterly-results/2024-2025/q3.html",
  },
};

export default function EvidenceDrawer({ evidenceId, onClose }: EvidenceDrawerProps) {
  const item = SYNTHETIC_EVIDENCE_CATALOG[evidenceId] || {
    title: "Primary Document Citation",
    documentType: "Filing",
    company: "Portfolio Holding",
    date: "2026",
    pdfPage: 1,
    excerpt: "Document evidence excerpt reference.",
    sourceUrl: "#",
  };

  // Close on Escape key press
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 100,
        display: "flex",
        justifyContent: "flex-end",
        backgroundColor: "rgba(23, 43, 58, 0.4)",
        backdropFilter: "blur(2px)",
      }}
      onClick={onClose}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="evidence-drawer-title"
        style={{
          width: "100%",
          maxWidth: "480px",
          height: "100%",
          backgroundColor: "var(--surface)",
          boxShadow: "-4px 0 24px rgba(0, 0, 0, 0.15)",
          display: "flex",
          flexDirection: "column",
          padding: "var(--space-4)",
          overflowY: "auto",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Drawer Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "var(--space-3)", borderBottom: "1px solid var(--line)", paddingBottom: "var(--space-3)" }}>
          <div>
            <span className="badge" style={{ background: "var(--accent-soft)", color: "var(--accent)", marginBottom: "4px" }}>
              PRIMARY EVIDENCE
            </span>
            <h2 id="evidence-drawer-title" style={{ fontSize: "1.0625rem", fontWeight: 700, color: "var(--ink)", marginTop: "4px" }}>
              Source Verification
            </h2>
          </div>
          <button
            onClick={onClose}
            aria-label="Close evidence drawer"
            style={{
              background: "none",
              border: "1px solid var(--line)",
              borderRadius: "var(--radius-control)",
              padding: "6px 12px",
              fontSize: "0.875rem",
              fontWeight: 600,
              cursor: "pointer",
              minHeight: "36px",
            }}
          >
            Close &times;
          </button>
        </div>

        {/* Document Metadata */}
        <div style={{ marginBottom: "var(--space-4)", fontSize: "0.8125rem", color: "var(--muted)", lineHeight: 1.6 }}>
          <div><strong>Document:</strong> {item.title}</div>
          <div><strong>Issuer:</strong> {item.company}</div>
          <div><strong>Type:</strong> {item.documentType} &bull; <strong>Date:</strong> {item.date}</div>
          <div><strong>PDF Page:</strong> Page {item.pdfPage} (1-based index)</div>
        </div>

        {/* Verbatim Excerpt */}
        <div style={{ marginBottom: "var(--space-4)" }}>
          <label style={{ display: "block", fontSize: "0.75rem", fontWeight: 600, color: "var(--muted)", textTransform: "uppercase", marginBottom: "6px" }}>
            Verbatim Primary Source Excerpt
          </label>
          <blockquote
            style={{
              borderLeft: "3px solid var(--accent)",
              padding: "var(--space-3)",
              background: "var(--surface-muted)",
              borderRadius: "0 var(--radius-control) var(--radius-control) 0",
              fontStyle: "italic",
              fontSize: "0.875rem",
              color: "var(--ink)",
              lineHeight: 1.6,
            }}
          >
            &ldquo;{item.excerpt}&rdquo;
          </blockquote>
        </div>

        {/* Actions */}
        <div style={{ marginTop: "auto", paddingTop: "var(--space-4)", borderTop: "1px solid var(--line)", display: "flex", flexDirection: "column", gap: "var(--space-2)" }}>
          <a
            href={item.sourceUrl}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              display: "block",
              textAlign: "center",
              background: "var(--accent)",
              color: "#FFF",
              padding: "10px",
              borderRadius: "var(--radius-control)",
              fontSize: "0.875rem",
              fontWeight: 600,
              textDecoration: "none",
              minHeight: "var(--min-touch-target)",
              lineHeight: "24px",
            }}
          >
            Open Original Primary PDF &rarr;
          </a>
          <button
            onClick={onClose}
            style={{
              background: "none",
              border: "1px solid var(--line)",
              color: "var(--muted)",
              padding: "10px",
              borderRadius: "var(--radius-control)",
              fontSize: "0.875rem",
              cursor: "pointer",
            }}
          >
            Back to Review
          </button>
        </div>
      </div>
    </div>
  );
}
