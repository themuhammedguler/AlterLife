"use client";

import { useEffect, useState } from "react";
import { getCommunityPaths, searchCommunityPaths, getCommunityStats } from "@/lib/api";

interface CommunityPath {
  id: string;
  goal: string;
  role: string;
  duration_months: number;
  steps: string[];
  outcome: string;
  tags: string[];
  success: boolean;
  country_to?: string;
}

interface CommunityStats {
  total_paths: number;
  success_rate: number;
  avg_duration_months: number;
  top_destinations: { country: string; count: number }[];
}

const TAG_COLORS: Record<string, string> = {
  "almanya": "var(--accent-cyan)",
  "kanada": "var(--accent-violet)",
  "hollanda": "var(--accent-green)",
  "abd": "var(--accent-amber)",
  "freelance": "var(--accent-pink)",
  "startup": "var(--accent-pink)",
  "aws": "var(--accent-amber)",
  "remote": "var(--accent-green)",
};

export default function CommunityPage() {
  const [paths, setPaths] = useState<CommunityPath[]>([]);
  const [stats, setStats] = useState<CommunityStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [searching, setSearching] = useState(false);
  const [searchMode, setSearchMode] = useState(false);

  useEffect(() => {
    Promise.all([
      getCommunityPaths(20),
      getCommunityStats(),
    ])
      .then(([pathsData, statsData]) => {
        setPaths(pathsData.paths || []);
        setStats(statsData);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      // Reset to all paths
      setSearchMode(false);
      const data = await getCommunityPaths(20);
      setPaths(data.paths || []);
      return;
    }
    setSearching(true);
    setSearchMode(true);
    try {
      const data = await searchCommunityPaths(searchQuery, 6);
      setPaths(data.paths || []);
    } catch (e) {
      console.error(e);
    } finally {
      setSearching(false);
    }
  };

  return (
    <div className="page-container" style={{ maxWidth: "1200px", padding: "40px 24px" }}>
      <div className="page-header" style={{ marginBottom: "32px" }}>
        <h1 className="page-title" style={{ fontSize: "2rem", fontWeight: 800 }}>
          <span className="text-gradient">Topluluk Başarı Yolları</span>
        </h1>
        <p className="page-subtitle" style={{ color: "var(--text-secondary)", fontSize: "0.95rem" }}>
          Benzer kararları veren kullanıcıların anonim deneyimleri — yapay zeka ile eşleştirme (RAG)
        </p>
      </div>

      {/* Stats Row */}
      {stats && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "14px", marginBottom: "32px" }}>
          {[
            { label: "Toplam Yol", value: stats.total_paths, color: "var(--accent-cyan)" },
            { label: "Başarı Oranı", value: `${stats.success_rate}%`, color: "var(--accent-green)" },
            { label: "Ort. Süre", value: `${stats.avg_duration_months} ay`, color: "var(--accent-violet)" },
            { label: "Aktif Üye", value: `${stats.total_paths * 3}+`, color: "var(--accent-amber)" },
          ].map((s) => (
            <div key={s.label} className="glass-card" style={{ padding: "18px", textAlign: "center" }}>
              <div style={{ fontFamily: "'Outfit', sans-serif", fontWeight: 800, fontSize: "1.6rem", color: s.color }}>
                {s.value}
              </div>
              <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "4px" }}>{s.label}</div>
            </div>
          ))}
        </div>
      )}

      {/* RAG Search */}
      <div
        className="glass-card"
        style={{ padding: "24px", marginBottom: "28px" }}
      >
        <h2 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: "6px", color: "var(--accent-cyan)" }}>
          🔍 Hedefe Göre Benzer Yolları Bul (AI Eşleştirme)
        </h2>
        <p style={{ fontSize: "0.82rem", color: "var(--text-muted)", marginBottom: "16px" }}>
          Hedefini yaz, yapay zeka toplulukta en benzer başarı yollarını bulup sıralar.
        </p>
        <div style={{ display: "flex", gap: "10px" }}>
          <input
            id="input-community-search"
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            placeholder={`Örn: "Almanya'da yazılım mühendisi olmak" veya "freelance kariyer"`}
            style={{
              flex: 1,
              padding: "10px 14px",
              background: "rgba(255,255,255,0.04)",
              border: "1px solid var(--glass-border)",
              borderRadius: "var(--radius-md)",
              color: "var(--text-primary)",
              fontSize: "0.85rem",
              outline: "none",
              fontFamily: "'Inter', sans-serif",
            }}
          />
          <button
            id="btn-community-search"
            className="btn-primary"
            onClick={handleSearch}
            disabled={searching}
            style={{ padding: "10px 20px", whiteSpace: "nowrap", fontSize: "0.85rem" }}
          >
            {searching ? "Aranıyor..." : "Eşleştir"}
          </button>
          {searchMode && (
            <button
              className="btn-ghost"
              onClick={async () => {
                setSearchQuery("");
                setSearchMode(false);
                const data = await getCommunityPaths(20);
                setPaths(data.paths || []);
              }}
              style={{ padding: "10px 16px", fontSize: "0.82rem" }}
            >
              Temizle
            </button>
          )}
        </div>
        {searchMode && (
          <p style={{ fontSize: "0.78rem", color: "var(--accent-cyan)", marginTop: "10px" }}>
            🤖 AI benzerlik analizi ile en ilgili {paths.length} yol bulundu: &ldquo;{searchQuery}&rdquo;
          </p>
        )}
      </div>

      {/* Paths Grid */}
      {loading ? (
        <div style={{ textAlign: "center", padding: "60px", color: "var(--text-muted)" }}>
          <div style={{ fontSize: "2rem", marginBottom: "12px" }}>🌍</div>
          <p>Topluluk yolları yükleniyor...</p>
        </div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))", gap: "18px" }}>
          {paths.map((path) => (
            <div key={path.id} className="glass-card glass-card-hover" style={{ padding: "24px" }}>
              {/* Header */}
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "12px" }}>
                <div>
                  <span style={{
                    fontSize: "0.68rem", fontWeight: 600, textTransform: "uppercase",
                    color: "var(--accent-cyan)", letterSpacing: "0.05em"
                  }}>
                    {path.role}
                  </span>
                  {path.country_to && (
                    <span style={{
                      marginLeft: "8px", fontSize: "0.68rem", color: "var(--text-muted)",
                    }}>
                      → {path.country_to}
                    </span>
                  )}
                </div>
                <span style={{
                  padding: "3px 10px", borderRadius: "999px",
                  background: "rgba(16,185,129,0.1)", border: "1px solid rgba(16,185,129,0.2)",
                  color: "var(--accent-green)", fontSize: "0.7rem", fontWeight: 600,
                }}>
                  ✓ Başarılı
                </span>
              </div>

              <h3 style={{ fontFamily: "'Outfit', sans-serif", fontWeight: 700, fontSize: "0.95rem", marginBottom: "8px" }}>
                {path.goal}
              </h3>
              <p style={{ fontSize: "0.8rem", color: "var(--text-secondary)", marginBottom: "14px", lineHeight: 1.55 }}>
                {path.outcome}
              </p>

              {/* Steps */}
              <div style={{ marginBottom: "14px" }}>
                {path.steps.slice(0, 3).map((step, i) => (
                  <div key={i} style={{ display: "flex", gap: "8px", alignItems: "flex-start", marginBottom: "5px" }}>
                    <span style={{ color: "var(--accent-cyan)", fontSize: "0.7rem", marginTop: "2px", flexShrink: 0 }}>→</span>
                    <span style={{ fontSize: "0.78rem", color: "var(--text-muted)" }}>{step}</span>
                  </div>
                ))}
              </div>

              {/* Tags */}
              <div style={{ display: "flex", gap: "6px", flexWrap: "wrap", marginBottom: "12px" }}>
                {path.tags.slice(0, 4).map((tag) => (
                  <span key={tag} style={{
                    padding: "2px 8px", borderRadius: "999px", fontSize: "0.65rem", fontWeight: 600,
                    background: `${TAG_COLORS[tag] || "var(--accent-violet)"}15`,
                    color: TAG_COLORS[tag] || "var(--accent-violet)",
                    border: `1px solid ${TAG_COLORS[tag] || "var(--accent-violet)"}30`,
                  }}>
                    #{tag}
                  </span>
                ))}
              </div>

              {/* Duration */}
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>
                  ⏱ {path.duration_months} ay
                </span>
                <a
                  href={`/simulations?base_goal=${encodeURIComponent(path.goal)}`}
                  style={{
                    fontSize: "0.75rem", color: "var(--accent-cyan)",
                    textDecoration: "none", fontWeight: 600,
                  }}
                >
                  Bu yolu simüle et →
                </a>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
