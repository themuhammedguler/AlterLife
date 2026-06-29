"use client";

const RESOURCES = [
  {
    id: "res_001",
    title: "AWS VPC Tutorial for Beginners",
    platform: "YouTube",
    typeLabel: "Video",
    tags: ["AWS", "Cloud", "VPC"],
    saved: "2026-06-28",
    done: false,
  },
  {
    id: "res_002",
    title: "Docker & Kubernetes: The Complete Guide",
    platform: "Udemy",
    typeLabel: "Kurs",
    tags: ["Docker", "Kubernetes", "DevOps"],
    saved: "2026-06-27",
    done: true,
  },
  {
    id: "res_003",
    title: "FastAPI – Official Documentation",
    platform: "Docs",
    typeLabel: "Dokuman",
    tags: ["Python", "FastAPI", "Backend"],
    saved: "2026-06-26",
    done: false,
  },
];

export default function LibraryPage() {
  return (
    <div className="page-container">
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end" }}>
        <div>
          <h1 className="page-title">
            <span className="text-gradient">Kutuphanem</span>
          </h1>
          <p className="page-subtitle">AI onerileri ve kaydettigin kaynaklar</p>
        </div>
        <button
          id="btn-add-resource"
          className="btn-primary"
          onClick={() => alert("Manuel kaynak ekleme – Hafta 3'te aktif")}
        >
          + Kaynak Ekle
        </button>
      </div>

      {/* Stats row */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "16px", marginBottom: "32px" }}>
        {[
          { label: "Toplam Kaynak", value: "3", badge: "Kutuphane" },
          { label: "Tamamlanan", value: "1", badge: "Tamamlandi" },
          { label: "Bekleyen", value: "2", badge: "Bekliyor" },
        ].map((s) => (
          <div key={s.label} className="glass-card" style={{ padding: "20px", display: "flex", alignItems: "center", gap: "16px" }}>
            <div>
              <div style={{ fontFamily: "'Outfit', sans-serif", fontSize: "1.6rem", fontWeight: 800, color: "var(--accent-cyan)" }}>
                {s.value}
              </div>
              <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: "4px" }}>{s.label}</div>
              <span className="badge badge-violet" style={{ fontSize: "0.65rem" }}>{s.badge}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Resources list */}
      <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
        {RESOURCES.map((res) => (
          <div
            key={res.id}
            id={`resource-${res.id}`}
            className="glass-card glass-card-hover"
            style={{
              padding: "20px 24px",
              display: "flex",
              alignItems: "center",
              gap: "20px",
              opacity: res.done ? 0.7 : 1,
            }}
          >
            <div
              style={{
                width: "48px",
                height: "48px",
                borderRadius: "var(--radius-sm)",
                background: "rgba(255,255,255,0.04)",
                border: "1px solid var(--glass-border)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "0.75rem",
                fontWeight: 600,
                color: "var(--text-secondary)",
                flexShrink: 0,
              }}
            >
              {res.typeLabel.toUpperCase()}
            </div>
            <div style={{ flex: 1 }}>
              <h3
                style={{
                  fontWeight: 600,
                  fontSize: "0.95rem",
                  marginBottom: "6px",
                  textDecoration: res.done ? "line-through" : "none",
                  color: res.done ? "var(--text-muted)" : "var(--text-primary)",
                }}
              >
                {res.title}
              </h3>
              <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
                <span className="badge badge-violet" style={{ fontSize: "0.7rem" }}>{res.platform}</span>
                {res.tags.map((t) => (
                  <span key={t} className="badge badge-cyan" style={{ fontSize: "0.7rem" }}>{t}</span>
                ))}
              </div>
            </div>
            <div style={{ textAlign: "right", flexShrink: 0 }}>
              <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginBottom: "8px" }}>{res.saved}</p>
              <span className={`badge ${res.done ? "badge-green" : "badge-violet"}`} style={{ fontSize: "0.75rem" }}>
                {res.done ? "Tamamlandi" : "Bekliyor"}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
