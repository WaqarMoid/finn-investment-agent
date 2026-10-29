import { useState, useEffect } from "react";

interface EvidenceDrawerProps {
  evidenceId: string;
  onClose: () => void;
}

interface EvidenceData {
  evidence_id: string;
  excerpt: string;
  verification_state: string;
  pdf_page_1based: number;
  printed_label?: string;
  ocr_flag: boolean;
  document: {
    id: string;
    source_type: string;
    publisher: string;
    source_url: string;
    published_at_utc: string;
    fiscal_period?: string;
  };
  company: {
    id: string;
    legal_name: string;
    isin: string;
  };
}

export default function EvidenceDrawer({ evidenceId, onClose }: EvidenceDrawerProps) {
  const [data, setData] = useState<EvidenceData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    fetch(`/api/v1/evidence/${encodeURIComponent(evidenceId)}`)
      .then((res) => {
        if (!res.ok) {
          throw new Error(`Evidence ${evidenceId} not found (${res.status})`);
        }
        return res.json();
      })
      .then((json) => {
        if (!cancelled) {
          setData(json.data);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err.message);
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [evidenceId]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  return (
    <div
      className="drawer-backdrop"
      onClick={onClose}
    >
      <div
        className="drawer-sheet"
        role="dialog"
        aria-modal="true"
        aria-labelledby="evidence-drawer-title"
        style={{
          width: "min(100%, 560px)",
          margin: "0 auto",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="drawer-grab-handle" />

        {/* Drawer Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 4 }}>
              <span className="badge badge-positive">VERIFIED PRIMARY SOURCE</span>
              {data && <span className="badge badge-routine">Page {data.pdf_page_1based}</span>}
            </div>
            <h2 id="evidence-drawer-title" style={{ fontSize: 18, fontWeight: 800, color: "var(--ink)", letterSpacing: "-0.02em" }}>
              Citation Evidence
            </h2>
          </div>
          <button
            className="icon-button"
            onClick={onClose}
            aria-label="Close evidence drawer"
          >
            &times;
          </button>
        </div>

        {loading && (
          <div className="empty-state">
            <p>Retrieving verified primary source page and excerpt…</p>
          </div>
        )}

        {error && !data && (
          <div className="notice error-notice" role="alert">
            <strong>Evidence citation unavailable</strong>
            <p style={{ fontSize: 12.5, marginTop: 6 }}>{error}</p>
            <p style={{ fontSize: 12, marginTop: 6, color: "var(--muted)" }}>FINN never invents mock citations when a primary document span is absent.</p>
          </div>
        )}

        {data && (
          <>
            {/* Issuer Metadata Pill Group */}
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginBottom: 16 }}>
              <span className="chip">{data.company.legal_name}</span>
              <span className="chip">{data.document.publisher}</span>
              {data.document.fiscal_period && <span className="chip">{data.document.fiscal_period}</span>}
              <span className="chip">Page {data.pdf_page_1based}</span>
            </div>

            {/* Verbatim Excerpt Card */}
            <div className="module-card" style={{ marginBottom: 16 }}>
              <div className="module-card-title">
                <span>VERBATIM PRIMARY EXCERPT</span>
                <span className="badge badge-routine">Untransformed</span>
              </div>
              <blockquote
                style={{
                  margin: 0,
                  fontSize: 14.5,
                  lineHeight: 1.55,
                  color: "var(--ink)",
                  fontStyle: "italic",
                }}
              >
                &ldquo;{data.excerpt}&rdquo;
              </blockquote>
            </div>

            {/* Document Details */}
            <div style={{ padding: "0 4px", marginBottom: 20, fontSize: 12, color: "var(--muted)", lineHeight: 1.6 }}>
              <div><strong>Filing Identifier:</strong> {data.document.id}</div>
              <div><strong>ISIN:</strong> {data.company.isin}</div>
              {data.printed_label && <div><strong>Section:</strong> {data.printed_label}</div>}
            </div>

            {/* Actions */}
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {data.document.source_url && (
                <a
                  className="button accent"
                  href={data.document.source_url.endsWith(".pdf") || data.document.source_url.includes(".pdf?") ? `${data.document.source_url.split("#")[0]}#page=${data.pdf_page_1based}` : data.document.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ width: "100%", justifyContent: "center" }}
                >
                  Open Original Document ↗
                </a>
              )}
              <button
                className="button secondary"
                onClick={onClose}
                style={{ width: "100%", justifyContent: "center" }}
              >
                Done
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
