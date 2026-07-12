"use client";

import { useState } from "react";
import { addCustomSkill, updateSkillPosition, deleteCustomSkill } from "@/lib/api";

interface SkillNode {
  skill_id: string;
  name: string;
  category: string;
  level: number;
  max_level: number;
  xp: number;
  is_unlocked: boolean;
  prerequisites: string[];
  description?: string;
  is_custom?: boolean;
  canvas_x?: number;
  canvas_y?: number;
}

interface Props {
  nodes: SkillNode[];
  onRefresh: () => void;
}

const CATEGORIES = ["Cloud", "Backend", "Frontend", "DevOps", "Dil", "Soft", "Custom"];
const CATEGORY_COLORS: Record<string, string> = {
  Cloud: "var(--accent-cyan)",
  Backend: "var(--accent-violet)",
  Frontend: "var(--accent-pink)",
  DevOps: "var(--accent-green)",
  Dil: "var(--accent-amber)",
  Soft: "#a78bfa",
  Custom: "var(--accent-cyan)",
};

export default function SkillTreeEditor({ nodes, onRefresh }: Props) {
  const [showAddModal, setShowAddModal] = useState(false);
  const [newName, setNewName] = useState("");
  const [newCategory, setNewCategory] = useState("Custom");
  const [newDesc, setNewDesc] = useState("");
  const [newPrereqs, setNewPrereqs] = useState<string[]>([]);
  const [saving, setSaving] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [draggingId, setDraggingId] = useState<string | null>(null);

  const handleAddNode = async () => {
    if (!newName.trim()) return;
    setSaving(true);
    try {
      await addCustomSkill({
        name: newName.trim(),
        category: newCategory,
        description: newDesc.trim() || undefined,
        prerequisites: newPrereqs,
      });
      setFeedback(`✅ "${newName}" yeteneği ağaca eklendi!`);
      setShowAddModal(false);
      setNewName("");
      setNewCategory("Custom");
      setNewDesc("");
      setNewPrereqs([]);
      onRefresh();
      setTimeout(() => setFeedback(null), 3000);
    } catch (e: any) {
      setFeedback(`❌ ${e.message}`);
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteNode = async (skillId: string, name: string) => {
    if (!confirm(`"${name}" yeteneğini silmek istediğinize emin misiniz?`)) return;
    try {
      await deleteCustomSkill(skillId);
      setFeedback(`🗑️ "${name}" silindi.`);
      onRefresh();
      setTimeout(() => setFeedback(null), 3000);
    } catch (e: any) {
      setFeedback(`❌ ${e.message}`);
    }
  };

  const customNodes = nodes.filter((n) => n.is_custom);

  return (
    <div>
      {/* Feedback Toast */}
      {feedback && (
        <div style={{
          position: "fixed", top: "24px", right: "24px", zIndex: 9999,
          background: "rgba(0,229,255,0.1)", border: "1px solid rgba(0,229,255,0.3)",
          backdropFilter: "blur(16px)", borderRadius: "12px", padding: "12px 18px",
          color: "var(--accent-cyan)", fontSize: "0.85rem", fontWeight: 600,
          boxShadow: "0 8px 32px rgba(0,229,255,0.12)",
        }}>
          {feedback}
        </div>
      )}

      {/* Editor Toolbar */}
      <div
        style={{
          padding: "16px 20px",
          background: "rgba(124,58,237,0.05)",
          border: "1px solid rgba(124,58,237,0.15)",
          borderRadius: "var(--radius-md)",
          marginBottom: "20px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div>
          <h3 style={{ fontSize: "0.9rem", fontWeight: 700, color: "var(--accent-violet)", marginBottom: "2px" }}>
            🛠️ Yetenek Ağacı Düzenleyici
          </h3>
          <p style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
            Kendi yeteneklerini ekle, önkoşullarını ayarla ve ağacı özelleştir
          </p>
        </div>
        <button
          id="btn-add-custom-skill"
          onClick={() => setShowAddModal(true)}
          className="btn-primary"
          style={{ fontSize: "0.82rem", padding: "8px 16px" }}
        >
          + Yetenek Ekle
        </button>
      </div>

      {/* Custom Nodes List */}
      {customNodes.length > 0 && (
        <div style={{ marginBottom: "20px" }}>
          <h4 style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: "10px", textTransform: "uppercase", letterSpacing: "0.05em" }}>
            Kendi Eklediğin Yetenekler ({customNodes.length})
          </h4>
          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            {customNodes.map((node) => {
              const color = CATEGORY_COLORS[node.category] || "var(--accent-cyan)";
              return (
                <div
                  key={node.skill_id}
                  style={{
                    padding: "12px 16px",
                    background: "var(--glass-bg)",
                    border: `1px solid ${color}30`,
                    borderRadius: "var(--radius-md)",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <div>
                    <span style={{ fontSize: "0.82rem", fontWeight: 600, color: "var(--text-primary)", marginRight: "8px" }}>
                      {node.name}
                    </span>
                    <span style={{
                      padding: "1px 8px", borderRadius: "999px", fontSize: "0.62rem",
                      background: `${color}15`, color, border: `1px solid ${color}30`,
                    }}>
                      {node.category}
                    </span>
                  </div>
                  <button
                    onClick={() => handleDeleteNode(node.skill_id, node.name)}
                    style={{
                      padding: "4px 10px",
                      background: "rgba(236,72,153,0.08)",
                      border: "1px solid rgba(236,72,153,0.2)",
                      borderRadius: "var(--radius-sm)",
                      color: "var(--accent-pink)",
                      fontSize: "0.72rem",
                      cursor: "pointer",
                      fontFamily: "'Inter', sans-serif",
                    }}
                  >
                    Sil
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {customNodes.length === 0 && (
        <div style={{
          padding: "20px", textAlign: "center",
          background: "rgba(255,255,255,0.02)", border: "1px dashed var(--glass-border)",
          borderRadius: "var(--radius-md)", marginBottom: "20px",
        }}>
          <p style={{ fontSize: "0.82rem", color: "var(--text-muted)" }}>
            Henüz özel yetenek eklemediniz. Yukarıdaki butonu kullanarak başlayın.
          </p>
        </div>
      )}

      {/* Add Node Modal */}
      {showAddModal && (
        <>
          <div
            onClick={() => setShowAddModal(false)}
            style={{
              position: "fixed", inset: 0, background: "rgba(0,0,0,0.6)",
              backdropFilter: "blur(6px)", zIndex: 9000,
            }}
          />
          <div style={{
            position: "fixed",
            top: "50%", left: "50%",
            transform: "translate(-50%, -50%)",
            width: "min(480px, 90vw)",
            background: "var(--surface-primary)",
            border: "1px solid var(--glass-border)",
            borderRadius: "var(--radius-lg)",
            padding: "32px",
            zIndex: 9001,
            animation: "fadeIn 0.2s ease",
          }}>
            <h3 style={{ fontFamily: "'Outfit', sans-serif", fontWeight: 700, fontSize: "1.1rem", marginBottom: "20px" }}>
              Yeni Yetenek Ekle
            </h3>

            <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
              <div>
                <label style={{ fontSize: "0.78rem", color: "var(--text-muted)", display: "block", marginBottom: "6px" }}>
                  Yetenek Adı *
                </label>
                <input
                  id="input-skill-name"
                  type="text"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  placeholder="Örn: Terraform, Kotlin, Japonca"
                  style={{
                    width: "100%", padding: "10px 12px",
                    background: "rgba(255,255,255,0.04)",
                    border: "1px solid var(--glass-border)",
                    borderRadius: "var(--radius-md)",
                    color: "var(--text-primary)", fontSize: "0.85rem",
                    fontFamily: "'Inter', sans-serif", outline: "none",
                    boxSizing: "border-box",
                  }}
                />
              </div>

              <div>
                <label style={{ fontSize: "0.78rem", color: "var(--text-muted)", display: "block", marginBottom: "6px" }}>
                  Kategori
                </label>
                <select
                  value={newCategory}
                  onChange={(e) => setNewCategory(e.target.value)}
                  style={{
                    width: "100%", padding: "10px 12px",
                    background: "rgba(255,255,255,0.04)",
                    border: "1px solid var(--glass-border)",
                    borderRadius: "var(--radius-md)",
                    color: "var(--text-primary)", fontSize: "0.85rem",
                    fontFamily: "'Inter', sans-serif", outline: "none",
                  }}
                >
                  {CATEGORIES.map((c) => (
                    <option key={c} value={c} style={{ background: "#0a0a14" }}>{c}</option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{ fontSize: "0.78rem", color: "var(--text-muted)", display: "block", marginBottom: "6px" }}>
                  Açıklama (isteğe bağlı)
                </label>
                <textarea
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  placeholder="Bu yeteneğin ne işe yaradığını kısaca açıklayın"
                  rows={2}
                  style={{
                    width: "100%", padding: "10px 12px",
                    background: "rgba(255,255,255,0.04)",
                    border: "1px solid var(--glass-border)",
                    borderRadius: "var(--radius-md)",
                    color: "var(--text-primary)", fontSize: "0.85rem",
                    fontFamily: "'Inter', sans-serif", outline: "none",
                    resize: "vertical", boxSizing: "border-box",
                  }}
                />
              </div>

              <div>
                <label style={{ fontSize: "0.78rem", color: "var(--text-muted)", display: "block", marginBottom: "8px" }}>
                  Önkoşullar (tıklayarak seç)
                </label>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                  {nodes.filter(n => !n.is_custom).slice(0, 8).map((n) => {
                    const selected = newPrereqs.includes(n.skill_id);
                    return (
                      <button
                        key={n.skill_id}
                        type="button"
                        onClick={() =>
                          setNewPrereqs((prev) =>
                            selected ? prev.filter((p) => p !== n.skill_id) : [...prev, n.skill_id]
                          )
                        }
                        style={{
                          padding: "3px 10px", borderRadius: "999px",
                          background: selected ? "rgba(0,229,255,0.12)" : "rgba(255,255,255,0.04)",
                          border: `1px solid ${selected ? "var(--accent-cyan)" : "var(--glass-border)"}`,
                          color: selected ? "var(--accent-cyan)" : "var(--text-muted)",
                          fontSize: "0.72rem", cursor: "pointer",
                          fontFamily: "'Inter', sans-serif",
                          transition: "all 0.2s ease",
                        }}
                      >
                        {n.name}
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>

            <div style={{ display: "flex", gap: "10px", marginTop: "24px" }}>
              <button
                className="btn-ghost"
                onClick={() => setShowAddModal(false)}
                style={{ flex: 1 }}
              >
                İptal
              </button>
              <button
                id="btn-save-custom-skill"
                className="btn-primary"
                onClick={handleAddNode}
                disabled={saving || !newName.trim()}
                style={{ flex: 1 }}
              >
                {saving ? "Ekleniyor..." : "Ağaca Ekle"}
              </button>
            </div>
          </div>
        </>
      )}

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translate(-50%, -48%); }
          to { opacity: 1; transform: translate(-50%, -50%); }
        }
      `}</style>
    </div>
  );
}
