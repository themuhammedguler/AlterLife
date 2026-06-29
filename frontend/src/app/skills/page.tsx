"use client";

const SKILL_NODES = [
  { id: "python",           name: "Python",             category: "Backend",  level: 3, maxLevel: 5, unlocked: true,  xp: 650 },
  { id: "javascript",       name: "JavaScript",          category: "Frontend", level: 2, maxLevel: 5, unlocked: true,  xp: 400 },
  { id: "docker",           name: "Docker",              category: "DevOps",   level: 1, maxLevel: 5, unlocked: true,  xp: 200 },
  { id: "aws_fundamentals", name: "AWS Fundamentals",    category: "Cloud",    level: 1, maxLevel: 5, unlocked: true,  xp: 200 },
  { id: "aws_vpc",          name: "AWS VPC",             category: "Cloud",    level: 0, maxLevel: 5, unlocked: false, xp: 0 },
  { id: "kubernetes",       name: "Kubernetes",          category: "DevOps",   level: 0, maxLevel: 5, unlocked: false, xp: 0 },
  { id: "german_a1",        name: "Almanca A1",          category: "Dil",      level: 2, maxLevel: 5, unlocked: true,  xp: 350 },
  { id: "german_b1",        name: "Almanca B1",          category: "Dil",      level: 0, maxLevel: 5, unlocked: false, xp: 0 },
];

const CATEGORIES = ["Hepsi", "Cloud", "Backend", "Frontend", "DevOps", "Dil"];

export default function SkillsPage() {
  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">
          <span className="text-gradient">Yetenek Agaci</span>
        </h1>
        <p className="page-subtitle">Yeteneklerini gelistir, yeni dugumlerin kilidini ac</p>
      </div>

      {/* Category Filter */}
      <div style={{ display: "flex", gap: "8px", marginBottom: "32px", flexWrap: "wrap" }}>
        {CATEGORIES.map((cat) => (
          <button
            key={cat}
            id={`filter-${cat.toLowerCase()}`}
            style={{
              padding: "6px 16px",
              background: cat === "Hepsi" ? "rgba(0,229,255,0.08)" : "var(--glass-bg)",
              border: `1px solid ${cat === "Hepsi" ? "var(--accent-cyan)" : "var(--glass-border)"}`,
              borderRadius: "999px",
              color: cat === "Hepsi" ? "var(--accent-cyan)" : "var(--text-secondary)",
              cursor: "pointer",
              fontSize: "0.85rem",
              fontFamily: "'Inter', sans-serif",
              transition: "all 0.2s ease",
            }}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Skill Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))", gap: "16px" }}>
        {SKILL_NODES.map((skill) => (
          <div
            key={skill.id}
            id={`skill-${skill.id}`}
            className="glass-card glass-card-hover"
            style={{
              padding: "22px",
              opacity: skill.unlocked ? 1 : 0.5,
              cursor: skill.unlocked ? "pointer" : "not-allowed",
              border: skill.unlocked ? "1px solid var(--glass-border)" : "1px dashed rgba(255,255,255,0.06)",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start", marginBottom: "12px" }}>
              <div
                style={{
                  width: "36px",
                  height: "36px",
                  borderRadius: "var(--radius-sm)",
                  background: skill.unlocked ? "rgba(0,229,255,0.1)" : "rgba(255,255,255,0.04)",
                  border: "1px solid var(--glass-border)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "0.75rem",
                  fontWeight: 700,
                  color: skill.unlocked ? "var(--accent-cyan)" : "var(--text-muted)",
                  letterSpacing: "0.05em",
                }}
              >
                {skill.category.slice(0, 2).toUpperCase()}
              </div>
              <span className={`badge ${skill.unlocked ? "badge-cyan" : "badge-violet"}`} style={{ fontSize: "0.7rem" }}>
                {skill.category}
              </span>
            </div>

            <h3 style={{ fontFamily: "'Outfit', sans-serif", fontWeight: 600, fontSize: "0.95rem", marginBottom: "4px" }}>
              {skill.name}
            </h3>
            <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginBottom: "14px" }}>
              {skill.unlocked ? `${skill.xp} XP` : "Kilitli"}
            </p>

            {/* Level dots */}
            <div style={{ display: "flex", gap: "4px", marginBottom: "14px" }}>
              {Array.from({ length: skill.maxLevel }).map((_, i) => (
                <div
                  key={i}
                  style={{
                    flex: 1,
                    height: "5px",
                    borderRadius: "999px",
                    background: i < skill.level ? "var(--accent-cyan)" : "rgba(255,255,255,0.06)",
                    boxShadow: i < skill.level ? "0 0 5px rgba(0,229,255,0.35)" : "none",
                    transition: "all 0.3s ease",
                  }}
                />
              ))}
            </div>

            {skill.unlocked && (
              <button
                id={`btn-resources-${skill.id}`}
                style={{
                  width: "100%",
                  padding: "8px",
                  background: "rgba(0,229,255,0.05)",
                  border: "1px solid rgba(0,229,255,0.12)",
                  borderRadius: "var(--radius-sm)",
                  color: "var(--accent-cyan)",
                  fontSize: "0.78rem",
                  cursor: "pointer",
                  fontFamily: "'Inter', sans-serif",
                  transition: "all 0.2s ease",
                }}
                onClick={() => alert("YouTube/Udemy kaynaklari – Hafta 3'te aktif")}
              >
                Kaynaklari Gor
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
