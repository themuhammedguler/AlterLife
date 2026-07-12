"use client";

import { useEffect, useState, useMemo } from "react";
import { getSkillTree, getSkillResources, addSkillXP } from "@/lib/api";
import SkillTreeEditor from "./components/SkillTreeEditor";

type SkillNode = {
  skill_id: string;
  name: string;
  category: string;
  level: number;
  max_level: number;
  xp: number;
  is_unlocked: boolean;
  prerequisites: string[];
  description?: string;
};

type SkillResource = {
  title: string;
  platform: string;
  url: string;
  duration?: string;
  level?: string;
};

const CATEGORY_COLORS: Record<string, string> = {
  Cloud: "var(--accent-cyan)",
  Backend: "var(--accent-violet)",
  Frontend: "var(--accent-pink)",
  DevOps: "var(--accent-green)",
  Dil: "var(--accent-amber)",
  Soft: "#a78bfa",
};

const CATEGORIES = ["Hepsi", "Cloud", "Backend", "Frontend", "DevOps", "Dil", "Soft"];

const PLATFORM_ICON: Record<string, string> = {
  YouTube: "▶",
  Udemy: "🎓",
  Docs: "📄",
  Article: "📝",
};

// Hardcoded coordinates for the interactive tree layout
const SKILL_COORDS: Record<string, { x: number; y: number }> = {
  // Column 1 (x = 30) - Core Skills
  python: { x: 30, y: 30 },
  javascript: { x: 30, y: 140 },
  docker: { x: 30, y: 250 },
  aws_fundamentals: { x: 30, y: 360 },
  german_a1: { x: 30, y: 470 },
  english_professional: { x: 30, y: 580 },

  // Column 2 (x = 390) - Specialized Skills
  fastapi: { x: 390, y: 30 },
  react: { x: 390, y: 140 },
  kubernetes: { x: 390, y: 250 },
  system_design: { x: 390, y: 340 },
  aws_vpc: { x: 390, y: 430 },
  german_b1: { x: 390, y: 520 },
};

export default function SkillsPage() {
  const [nodes, setNodes] = useState<SkillNode[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeCategory, setActiveCategory] = useState("Hepsi");
  const [editorMode, setEditorMode] = useState(false);

  const [drawerSkill, setDrawerSkill] = useState<SkillNode | null>(null);
  const [resources, setResources] = useState<SkillResource[]>([]);
  const [resourcesLoading, setResourcesLoading] = useState(false);
  const [xpFeedback, setXpFeedback] = useState<string | null>(null);

  useEffect(() => {
    getSkillTree()
      .then((data) => setNodes(data.nodes || []))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const openDrawer = async (skill: SkillNode) => {
    if (!skill.is_unlocked) return;
    setDrawerSkill(skill);
    setResources([]);
    setResourcesLoading(true);
    try {
      const data = await getSkillResources(skill.skill_id);
      setResources(data);
    } catch (e) {
      console.error(e);
    } finally {
      setResourcesLoading(false);
    }
  };

  const handleAddXP = async (skillId: string) => {
    try {
      const result = await addSkillXP(skillId, 100);
      setXpFeedback(result.message);
      
      // Refresh tree
      const data = await getSkillTree();
      setNodes(data.nodes || []);
      
      if (drawerSkill?.skill_id === skillId) {
        const updated = data.nodes.find((n: SkillNode) => n.skill_id === skillId);
        if (updated) setDrawerSkill(updated);
      }
      setTimeout(() => setXpFeedback(null), 3000);
    } catch (e: any) {
      setXpFeedback(e.message);
      setTimeout(() => setXpFeedback(null), 3000);
    }
  };

  // Find prerequisite connection lines
  const connections = useMemo(() => {
    const list: { from: string; to: string; color: string; isUnlocked: boolean }[] = [];
    nodes.forEach((node) => {
      node.prerequisites.forEach((prereqId) => {
        const prereqNode = nodes.find((n) => n.skill_id === prereqId);
        const color = CATEGORY_COLORS[node.category] || "var(--accent-cyan)";
        list.push({
          from: prereqId,
          to: node.skill_id,
          color,
          isUnlocked: node.is_unlocked && (prereqNode ? prereqNode.is_unlocked : false),
        });
      });
    });
    return list;
  }, [nodes]);

  return (
    <div className="page-container" style={{ maxWidth: "1200px", padding: "40px 24px" }}>
      <div className="page-header" style={{ marginBottom: "32px" }}>
        <h1 className="page-title" style={{ fontSize: "2rem", fontWeight: 800 }}>
          <span className="text-gradient">Yetenek Ağacı</span>
        </h1>
        <p className="page-subtitle" style={{ color: "var(--text-secondary)", fontSize: "0.95rem" }}>
          Yeteneklerini geliştir, yeni düğümlerin kilidini aç ve eğitim kaynaklarına ulaş
        </p>
      </div>

      {/* XP Feedback Toast */}
      {xpFeedback && (
        <div style={{
          position: "fixed", top: "24px", right: "24px", zIndex: 9999,
          background: "rgba(0,229,255,0.12)", border: "1px solid rgba(0,229,255,0.3)",
          backdropFilter: "blur(16px)", borderRadius: "12px", padding: "14px 20px",
          color: "var(--accent-cyan)", fontSize: "0.9rem", fontWeight: 600,
          boxShadow: "0 8px 32px rgba(0,229,255,0.15)", maxWidth: "360px",
          animation: "fadeIn 0.3s ease",
        }}>
          {xpFeedback}
        </div>
      )}

      {/* Category Filter */}
      <div style={{ display: "flex", gap: "8px", marginBottom: "32px", flexWrap: "wrap", alignItems: "center" }}>
        {CATEGORIES.map((cat) => {
          const active = cat === activeCategory;
          return (
            <button
              key={cat}
              id={`filter-${cat.toLowerCase()}`}
              onClick={() => setActiveCategory(cat)}
              style={{
                padding: "7px 18px",
                background: active ? "rgba(0,229,255,0.1)" : "var(--glass-bg)",
                border: `1px solid ${active ? "var(--accent-cyan)" : "var(--glass-border)"}`,
                borderRadius: "999px",
                color: active ? "var(--accent-cyan)" : "var(--text-secondary)",
                cursor: "pointer", fontSize: "0.85rem",
                fontFamily: "'Inter', sans-serif",
                transition: "all 0.2s ease",
                fontWeight: active ? 600 : 400,
              }}
            >
              {cat}
            </button>
          );
        })}
        {/* Editor Mode Toggle */}
        <div style={{ marginLeft: "auto" }}>
          <button
            id="btn-editor-mode"
            onClick={() => setEditorMode((v) => !v)}
            style={{
              padding: "7px 16px",
              background: editorMode ? "rgba(124,58,237,0.12)" : "var(--glass-bg)",
              border: `1px solid ${editorMode ? "var(--accent-violet)" : "var(--glass-border)"}`,
              borderRadius: "999px",
              color: editorMode ? "var(--accent-violet)" : "var(--text-secondary)",
              cursor: "pointer", fontSize: "0.82rem",
              fontFamily: "'Inter', sans-serif", fontWeight: 600,
              transition: "all 0.2s ease",
            }}
          >
            {editorMode ? "🔒 Düzenleme Modu (Aktif)" : "🛠️ Düzenle"}
          </button>
        </div>
      </div>

      {/* Skill Tree Editor */}
      {editorMode && (
        <SkillTreeEditor
          nodes={nodes}
          onRefresh={() => getSkillTree().then((data) => setNodes(data.nodes || []))}
        />
      )}

      {loading ? (
        <div style={{ textAlign: "center", padding: "60px", color: "var(--text-muted)" }}>
          <div style={{ fontSize: "2rem", marginBottom: "12px" }}>🔮</div>
          <p>Yetenek ağacı yükleniyor...</p>
        </div>
      ) : (
        <div 
          className="glass-card"
          style={{ 
            position: "relative", 
            padding: "40px 32px", 
            overflowX: "auto", 
            minHeight: "680px"
          }}
        >
          <div style={{ position: "relative", width: "680px", height: "660px" }}>
            
            {/* SVG Connector Lines Layer */}
            <svg 
              style={{ 
                position: "absolute", 
                top: 0, 
                left: 0, 
                width: "100%", 
                height: "100%", 
                pointerEvents: "none", 
                zIndex: 1 
              }}
            >
              {connections.map((conn, idx) => {
                const fromCoord = SKILL_COORDS[conn.from];
                const toCoord = SKILL_COORDS[conn.to];
                if (!fromCoord || !toCoord) return null;

                const fromNode = nodes.find(n => n.skill_id === conn.from);
                const toNode = nodes.find(n => n.skill_id === conn.to);
                
                // Dim lines if active category filters them out
                const fromVisible = activeCategory === "Hepsi" || (fromNode && fromNode.category === activeCategory);
                const toVisible = activeCategory === "Hepsi" || (toNode && toNode.category === activeCategory);
                const opacity = fromVisible && toVisible ? (conn.isUnlocked ? 0.8 : 0.2) : 0.05;

                const x1 = fromCoord.x + 240;
                const y1 = fromCoord.y + 22;
                const x2 = toCoord.x;
                const y2 = toCoord.y + 22;
                const midX = (x1 + x2) / 2;
                const d = `M ${x1} ${y1} C ${midX} ${y1}, ${midX} ${y2}, ${x2} ${y2}`;

                return (
                  <path
                    key={idx}
                    d={d}
                    fill="none"
                    stroke={conn.isUnlocked ? conn.color : "rgba(255, 255, 255, 0.2)"}
                    strokeWidth={conn.isUnlocked ? 2.5 : 1.2}
                    opacity={opacity}
                    style={{
                      transition: "all 0.3s ease",
                      filter: conn.isUnlocked ? `drop-shadow(0 0 3px ${conn.color}80)` : "none"
                    }}
                  />
                );
              })}
            </svg>

            {/* HTML Nodes Layer */}
            <div style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%", zIndex: 2 }}>
              {nodes.map((skill) => {
                const coords = SKILL_COORDS[skill.skill_id];
                if (!coords) return null;

                const color = CATEGORY_COLORS[skill.category] || "var(--accent-cyan)";
                const prereqNames = skill.prerequisites
                  .map((p) => nodes.find((n) => n.skill_id === p)?.name || p)
                  .join(", ");
                  
                const isFilteredOut = activeCategory !== "Hepsi" && skill.category !== activeCategory;
                const opacity = isFilteredOut ? 0.15 : (skill.is_unlocked ? 1 : 0.55);

                return (
                  <div
                    key={skill.skill_id}
                    id={`skill-${skill.skill_id}`}
                    onClick={() => skill.is_unlocked && openDrawer(skill)}
                    style={{
                      position: "absolute",
                      left: `${coords.x}px`,
                      top: `${coords.y}px`,
                      width: "240px",
                      padding: "12px 14px",
                      opacity,
                      cursor: skill.is_unlocked ? "pointer" : "not-allowed",
                      background: "var(--glass-bg)",
                      border: skill.is_unlocked ? `1px solid rgba(255,255,255,0.08)` : "1px dashed rgba(255,255,255,0.05)",
                      borderRadius: "var(--radius-md)",
                      transition: "all 0.3s ease",
                      pointerEvents: isFilteredOut ? "none" : "auto",
                      boxShadow: skill.is_unlocked ? `inset 0 1px 0 rgba(255,255,255,0.05)` : "none"
                    }}
                  >
                    {!skill.is_unlocked && (
                      <div style={{ position: "absolute", top: "10px", right: "12px", fontSize: "0.75rem" }}>🔒</div>
                    )}
                    
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
                      <span style={{
                        padding: "1px 8px", borderRadius: "999px", fontSize: "0.62rem", fontWeight: 600,
                        background: `${color}15`, color, border: `1px solid ${color}30`,
                      }}>
                        {skill.category}
                      </span>
                    </div>

                    <h3 style={{ fontFamily: "'Outfit', sans-serif", fontWeight: 600, fontSize: "0.85rem", marginBottom: "2px", color: skill.is_unlocked ? "var(--text-primary)" : "var(--text-muted)" }}>
                      {skill.name}
                    </h3>
                    <p style={{ fontSize: "0.7rem", color: "var(--text-muted)", marginBottom: "8px" }}>
                      {skill.is_unlocked ? `${skill.xp} XP • Lvl ${skill.level}/${skill.max_level}` : prereqNames ? `Gerekli: ${prereqNames}` : "Kilitli"}
                    </p>

                    {/* Progress indicator */}
                    {skill.is_unlocked ? (
                      <div style={{ display: "flex", gap: "3px", marginBottom: "8px" }}>
                        {Array.from({ length: skill.max_level }).map((_, i) => (
                          <div key={i} style={{
                            flex: 1, height: "3px", borderRadius: "999px",
                            background: i < skill.level ? color : "rgba(255,255,255,0.05)",
                            boxShadow: i < skill.level ? `0 0 4px ${color}60` : "none",
                          }} />
                        ))}
                      </div>
                    ) : (
                      <div style={{ height: "3px" }} />
                    )}

                    {skill.is_unlocked && (
                      <div style={{ display: "flex", gap: "6px" }}>
                        <button
                          id={`btn-resources-${skill.skill_id}`}
                          style={{
                            flex: 1, padding: "4px 8px", background: `${color}0c`,
                            border: `1px solid ${color}20`, borderRadius: "var(--radius-sm)",
                            color, fontSize: "0.72rem", cursor: "pointer",
                            fontFamily: "'Inter', sans-serif", transition: "all 0.2s ease",
                          }}
                          onClick={(e) => { e.stopPropagation(); openDrawer(skill); }}
                        >
                          Kaynaklar
                        </button>
                        <button
                          id={`btn-xp-${skill.skill_id}`}
                          style={{
                            padding: "4px 8px", background: "rgba(16,185,129,0.08)",
                            border: "1px solid rgba(16,185,129,0.2)", borderRadius: "var(--radius-sm)",
                            color: "var(--accent-green)", fontSize: "0.72rem", cursor: "pointer",
                            fontFamily: "'Inter', sans-serif", transition: "all 0.2s ease",
                          }}
                          onClick={(e) => { e.stopPropagation(); handleAddXP(skill.skill_id); }}
                        >
                          +XP
                        </button>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Resource Drawer */}
      {drawerSkill && (
        <>
          <div
            onClick={() => setDrawerSkill(null)}
            style={{
              position: "fixed", inset: 0, background: "rgba(0,0,0,0.5)",
              backdropFilter: "blur(4px)", zIndex: 9000,
            }}
          />
          <div style={{
            position: "fixed", right: 0, top: 0, bottom: 0, width: "min(460px, 90vw)",
            background: "var(--surface-primary)", borderLeft: "1px solid var(--glass-border)",
            zIndex: 9001, overflowY: "auto", padding: "32px",
            display: "flex", flexDirection: "column", gap: "24px",
            animation: "slideInRight 0.3s cubic-bezier(0.16, 1, 0.3, 1)",
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start" }}>
              <div>
                <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginBottom: "4px" }}>
                  {drawerSkill.category}
                </p>
                <h2 style={{ fontFamily: "'Outfit', sans-serif", fontSize: "1.3rem", fontWeight: 700 }}>
                  {drawerSkill.name}
                </h2>
              </div>
              <button
                onClick={() => setDrawerSkill(null)}
                style={{
                  padding: "8px 12px", background: "var(--glass-bg)", border: "1px solid var(--glass-border)",
                  borderRadius: "var(--radius-sm)", color: "var(--text-muted)", cursor: "pointer",
                  fontFamily: "'Inter', sans-serif", fontSize: "0.85rem",
                }}
              >
                ✕
              </button>
            </div>

            {/* Stats */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "12px" }}>
              {[
                { label: "Seviye", value: `${drawerSkill.level}/${drawerSkill.max_level}`, color: CATEGORY_COLORS[drawerSkill.category] },
                { label: "XP", value: drawerSkill.xp.toString(), color: "var(--accent-violet)" },
                { label: "Durum", value: drawerSkill.is_unlocked ? "Aktif" : "Kilitli", color: drawerSkill.is_unlocked ? "var(--accent-green)" : "var(--text-muted)" },
              ].map((s) => (
                <div key={s.label} className="glass-card" style={{ padding: "14px", textAlign: "center" }}>
                  <div style={{ fontFamily: "'Outfit', sans-serif", fontWeight: 700, fontSize: "1rem", color: s.color }}>{s.value}</div>
                  <div style={{ fontSize: "0.7rem", color: "var(--text-muted)", marginTop: "4px" }}>{s.label}</div>
                </div>
              ))}
            </div>

            {drawerSkill.description && (
              <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", lineHeight: 1.6 }}>
                {drawerSkill.description}
              </p>
            )}

            <button
              onClick={() => handleAddXP(drawerSkill.skill_id)}
              style={{
                padding: "12px", background: "rgba(16,185,129,0.08)", border: "1px solid rgba(16,185,129,0.25)",
                borderRadius: "var(--radius-md)", color: "var(--accent-green)", fontFamily: "'Inter', sans-serif",
                fontSize: "0.9rem", fontWeight: 600, cursor: "pointer", transition: "all 0.2s ease",
              }}
            >
              ⚡ +100 XP Kazan
            </button>

            <div>
              <h3 style={{ fontFamily: "'Outfit', sans-serif", fontSize: "0.95rem", fontWeight: 600, marginBottom: "16px" }}>
                Önerilen Kaynaklar
              </h3>
              {resourcesLoading ? (
                <div style={{ textAlign: "center", padding: "24px", color: "var(--text-muted)" }}>
                  Kaynaklar yükleniyor...
                </div>
              ) : resources.length === 0 ? (
                <p style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>Kaynak bulunamadı.</p>
              ) : (
                <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                  {resources.map((res, i) => (
                    <a
                      key={i}
                      href={res.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="glass-card glass-card-hover"
                      style={{
                        padding: "14px 16px", display: "flex", gap: "12px", alignItems: "center",
                        textDecoration: "none", color: "var(--text-primary)",
                      }}
                    >
                      <span style={{ fontSize: "1.1rem" }}>{PLATFORM_ICON[res.platform] || "🔗"}</span>
                      <div style={{ flex: 1 }}>
                        <p style={{ fontWeight: 500, fontSize: "0.85rem", marginBottom: "4px" }}>{res.title}</p>
                        <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
                          <span style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>{res.platform}</span>
                          {res.duration && <span style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>⏱ {res.duration}</span>}
                          {res.level && <span style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>📊 {res.level}</span>}
                        </div>
                      </div>
                      <span style={{ fontSize: "0.8rem", color: "var(--accent-cyan)" }}>↗</span>
                    </a>
                  ))}
                </div>
              )}
            </div>
          </div>
        </>
      )}

      <style>{`
        @keyframes slideInRight {
          from { transform: translateX(100%); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(-8px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
}
