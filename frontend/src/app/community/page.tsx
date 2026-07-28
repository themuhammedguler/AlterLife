"use client";

import { useEffect, useState } from "react";
import type { CSSProperties } from "react";
import {
  createCommunityInvite,
  getCommunityCohort,
  getCommunityOverview,
  getCommunityPaths,
  getCommunityStats,
  getMyCommunityPaths,
  joinCommunityPath,
  searchCommunityPaths,
} from "@/lib/api";

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
  members_count?: number;
  avg_progress?: number;
  branches?: { name: string; members_count: number; avg_progress: number }[];
  common_until_step?: number;
}

interface CommunityStats {
  total_paths: number;
  success_rate: number;
  avg_duration_months: number;
  top_destinations: { country: string; count: number }[];
}

interface Cohort {
  path_id: string;
  goal: string;
  members_count: number;
  avg_progress: number;
  completion_rate: number;
  stuck_count: number;
  common_until: string[];
  branches: { name: string; members_count: number; avg_progress: number }[];
  members: {
    alias: string;
    branch: string;
    completed_steps: number;
    total_steps: number;
    progress_percent: number;
    current_step: number;
    status: "on_track" | "stuck" | "ahead";
  }[];
}

interface Membership {
  path_id: string;
  goal: string;
  branch: string;
  progress_percent: number;
  current_step: number;
  total_steps: number;
  peer_rank: number;
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
  const [selectedPath, setSelectedPath] = useState<CommunityPath | null>(null);
  const [cohort, setCohort] = useState<Cohort | null>(null);
  const [memberships, setMemberships] = useState<Membership[]>([]);
  const [joining, setJoining] = useState(false);
  const [inviteCode, setInviteCode] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      getCommunityPaths(20),
      getCommunityStats(),
      getCommunityOverview(),
      getMyCommunityPaths(),
    ])
      .then(([pathsData, statsData, _overviewData, myPathsData]) => {
        setPaths(pathsData.paths || []);
        setStats(statsData);
        setMemberships(myPathsData.memberships || []);
        const firstPath = pathsData.paths?.[0];
        if (firstPath) {
          setSelectedPath(firstPath);
          return getCommunityCohort(firstPath.id).then((data) => setCohort(data));
        }
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

  const selectPath = async (path: CommunityPath) => {
    setSelectedPath(path);
    try {
      const data = await getCommunityCohort(path.id);
      setCohort(data);
    } catch (e) {
      console.error(e);
    }
  };

  const handleJoin = async (branch?: string) => {
    if (!selectedPath) return;
    setJoining(true);
    try {
      await joinCommunityPath(selectedPath.id, branch);
      const myPathsData = await getMyCommunityPaths();
      const cohortData = await getCommunityCohort(selectedPath.id);
      setMemberships(myPathsData.memberships || []);
      setCohort(cohortData);
    } catch (e) {
      console.error(e);
    } finally {
      setJoining(false);
    }
  };

  const handleInvite = async (branch?: string) => {
    if (!selectedPath) return;
    try {
      const invite = await createCommunityInvite(selectedPath.id, branch);
      setInviteCode(invite.code);
    } catch (e) {
      console.error(e);
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

      <div style={{ display: "grid", gridTemplateColumns: "1fr 380px", gap: "22px", marginBottom: "28px" }}>
        <div className="glass-card" style={{ padding: "24px" }}>
          <h2 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: "6px", color: "var(--accent-cyan)" }}>
            Rota Radarı
          </h2>
          <p style={{ fontSize: "0.82rem", color: "var(--text-muted)", marginBottom: "16px" }}>
            Bir topluluk rotası seç; kimler ne kadar ilerlemiş, nerede takılmış, hangi noktada dallanmış gör.
          </p>
          <div style={{ display: "grid", gap: "10px" }}>
            {paths.slice(0, 5).map((path) => {
              const active = selectedPath?.id === path.id;
              return (
                <button
                  key={path.id}
                  type="button"
                  onClick={() => selectPath(path)}
                  style={{
                    ...routeButtonStyle,
                    borderColor: active ? "var(--accent-cyan)" : "var(--glass-border)",
                    background: active ? "rgba(0, 229, 255, 0.06)" : "rgba(255,255,255,0.02)",
                  }}
                >
                  <span style={{ fontWeight: 700, color: "var(--text-primary)" }}>{path.goal}</span>
                  <span style={{ color: "var(--text-muted)", fontSize: "0.76rem" }}>
                    {path.members_count || 0} kişi · ort. %{path.avg_progress || 0} ilerleme
                  </span>
                  <ProgressBar value={path.avg_progress || 0} />
                </button>
              );
            })}
          </div>
        </div>

        <div className="glass-card" style={{ padding: "24px" }}>
          <h2 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: "6px", color: "var(--accent-green)" }}>
            Benim Topluluk Yollarım
          </h2>
          {memberships.length === 0 ? (
            <p style={{ fontSize: "0.82rem", color: "var(--text-muted)", lineHeight: 1.55 }}>
              Henüz bir rotaya katılmadın. Bir rota seçip aşağıdan dala katılınca burada kendi ilerlemen görünecek.
            </p>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              {memberships.map((item) => (
                <div key={item.path_id} style={miniPanelStyle}>
                  <strong style={{ fontSize: "0.82rem" }}>{item.goal}</strong>
                  <div style={{ fontSize: "0.74rem", color: "var(--text-muted)", margin: "5px 0" }}>
                    {item.branch} · Adım {item.current_step}/{item.total_steps} · ilk {item.peer_rank}
                  </div>
                  <ProgressBar value={item.progress_percent} />
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {cohort && selectedPath && (
        <div className="glass-card" style={{ padding: "24px", marginBottom: "28px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "16px", marginBottom: "18px" }}>
            <div>
              <h2 style={{ fontSize: "1.05rem", fontWeight: 800, marginBottom: "6px" }}>{cohort.goal}</h2>
              <p style={{ fontSize: "0.82rem", color: "var(--text-muted)", lineHeight: 1.5 }}>
                {cohort.members_count} anonim üye · ortalama %{cohort.avg_progress} ilerleme · %{cohort.completion_rate} tamamlanma
              </p>
            </div>
            <button
              type="button"
              className="btn-primary"
              disabled={joining}
              onClick={() => handleJoin(cohort.branches[0]?.name)}
              style={{ whiteSpace: "nowrap", fontSize: "0.84rem" }}
            >
              {joining ? "Katılıyor..." : "Bu Rotaya Katıl"}
            </button>
            <button
              type="button"
              className="btn-ghost"
              onClick={() => handleInvite(cohort.branches[0]?.name)}
              style={{ whiteSpace: "nowrap", fontSize: "0.84rem" }}
            >
              Davet Kodu
            </button>
          </div>
          {inviteCode && (
            <div style={{ ...miniPanelStyle, marginBottom: "16px", display: "flex", justifyContent: "space-between", gap: "12px", alignItems: "center" }}>
              <span style={{ fontSize: "0.78rem", color: "var(--text-secondary)" }}>Arkadaşınla paylaşılacak rota kodu</span>
              <code style={{ color: "var(--accent-cyan)", fontWeight: 800 }}>{inviteCode}</code>
            </div>
          )}

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "14px" }}>
            <div style={miniPanelStyle}>
              <h3 style={panelTitleStyle}>Ortak Gidilen Kısım</h3>
              {cohort.common_until.map((step, idx) => (
                <div key={step} style={{ fontSize: "0.77rem", color: "var(--text-secondary)", marginTop: "7px" }}>
                  {idx + 1}. {step}
                </div>
              ))}
            </div>
            <div style={miniPanelStyle}>
              <h3 style={panelTitleStyle}>Dallanma Seçenekleri</h3>
              {cohort.branches.map((branch) => (
                <button
                  key={branch.name}
                  type="button"
                  disabled={joining}
                  onClick={() => handleJoin(branch.name)}
                  style={branchButtonStyle}
                >
                  <span>{branch.name}</span>
                  <small>{branch.members_count} kişi · %{branch.avg_progress}</small>
                </button>
              ))}
            </div>
            <div style={miniPanelStyle}>
              <h3 style={panelTitleStyle}>İnsanlar Nerede?</h3>
              {cohort.members.slice(0, 5).map((member) => (
                <div key={member.alias} style={{ marginTop: "8px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.74rem", color: "var(--text-secondary)" }}>
                    <span>{member.alias} · {member.branch}</span>
                    <span>{member.progress_percent}%</span>
                  </div>
                  <ProgressBar value={member.progress_percent} tone={member.status === "stuck" ? "pink" : member.status === "ahead" ? "green" : "cyan"} />
                </div>
              ))}
            </div>
          </div>
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

function ProgressBar({ value, tone = "cyan" }: { value: number; tone?: "cyan" | "green" | "pink" }) {
  const color = tone === "green" ? "var(--accent-green)" : tone === "pink" ? "var(--accent-pink)" : "var(--accent-cyan)";
  return (
    <div style={{ height: "6px", borderRadius: "999px", background: "rgba(255,255,255,0.08)", overflow: "hidden", marginTop: "7px" }}>
      <div style={{ width: `${Math.min(Math.max(value, 0), 100)}%`, height: "100%", background: color }} />
    </div>
  );
}

const routeButtonStyle: CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: "4px",
  textAlign: "left",
  padding: "13px",
  border: "1px solid var(--glass-border)",
  borderRadius: "var(--radius-md)",
  color: "var(--text-primary)",
  cursor: "pointer",
  fontFamily: "'Inter', sans-serif",
};

const miniPanelStyle: CSSProperties = {
  padding: "14px",
  background: "rgba(255,255,255,0.025)",
  border: "1px solid var(--glass-border)",
  borderRadius: "var(--radius-md)",
};

const panelTitleStyle: CSSProperties = {
  fontSize: "0.84rem",
  color: "var(--accent-cyan)",
  marginBottom: "8px",
};

const branchButtonStyle: CSSProperties = {
  width: "100%",
  display: "flex",
  justifyContent: "space-between",
  gap: "8px",
  alignItems: "center",
  padding: "9px 0",
  border: 0,
  borderBottom: "1px solid var(--glass-border)",
  background: "transparent",
  color: "var(--text-secondary)",
  cursor: "pointer",
  fontFamily: "'Inter', sans-serif",
  fontSize: "0.78rem",
  textAlign: "left",
};
