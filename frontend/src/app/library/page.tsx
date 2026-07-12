"use client";

import { useEffect, useState } from "react";
import { getLibrary, saveLibraryResource, completeLibraryResource, deleteLibraryResource } from "@/lib/api";

type LibraryResource = {
  resource_id: string;
  title: string;
  platform: string;
  url: string;
  skill_tags: string[];
  saved_at: string;
  is_completed: boolean;
  completed_at?: string;
  xp_reward: number;
};

const PLATFORM_COLORS: Record<string, string> = {
  YouTube: "var(--accent-pink)",
  Udemy: "var(--accent-amber)",
  Docs: "var(--accent-cyan)",
  Article: "var(--accent-violet)",
};

const PLATFORM_ICON: Record<string, string> = {
  YouTube: "▶",
  Udemy: "🎓",
  Docs: "📄",
  Article: "📝",
};

export default function LibraryPage() {
  const [resources, setResources] = useState<LibraryResource[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const [form, setForm] = useState({ title: "", platform: "YouTube", url: "", skill_tags: "" });
  const [submitting, setSubmitting] = useState(false);

  const showToast = (msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(null), 3500);
  };

  const loadLibrary = async () => {
    try {
      const data = await getLibrary();
      setResources(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadLibrary(); }, []);

  const handleComplete = async (resourceId: string) => {
    try {
      const result = await completeLibraryResource(resourceId);
      showToast(`✅ ${result.message}`);
      loadLibrary();
    } catch (e: any) {
      showToast(`❌ ${e.message}`);
    }
  };

  const handleDelete = async (resourceId: string) => {
    try {
      await deleteLibraryResource(resourceId);
      showToast("🗑️ Kaynak silindi.");
      loadLibrary();
    } catch (e: any) {
      showToast(`❌ ${e.message}`);
    }
  };

  const handleAdd = async () => {
    if (!form.title || !form.url) { showToast("Başlık ve URL zorunludur."); return; }
    setSubmitting(true);
    try {
      await saveLibraryResource({
        title: form.title,
        platform: form.platform,
        url: form.url,
        skill_tags: form.skill_tags.split(",").map((t) => t.trim()).filter(Boolean),
      });
      showToast("📚 Kaynak kütüphaneye eklendi!");
      setShowAddModal(false);
      setForm({ title: "", platform: "YouTube", url: "", skill_tags: "" });
      loadLibrary();
    } catch (e: any) {
      showToast(`❌ ${e.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  const total = resources.length;
  const completed = resources.filter((r) => r.is_completed).length;
  const pending = total - completed;

  return (
    <div className="page-container">
      {toast && (
        <div style={{
          position: "fixed", top: "24px", right: "24px", zIndex: 9999,
          background: "rgba(0,229,255,0.1)", border: "1px solid rgba(0,229,255,0.25)",
          backdropFilter: "blur(16px)", borderRadius: "12px", padding: "14px 20px",
          color: "var(--accent-cyan)", fontSize: "0.9rem", fontWeight: 600,
          boxShadow: "0 8px 32px rgba(0,0,0,0.3)", maxWidth: "360px",
          animation: "fadeInDown 0.3s ease",
        }}>
          {toast}
        </div>
      )}

      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end" }}>
        <div>
          <h1 className="page-title">
            <span className="text-gradient">Kütüphanem</span>
          </h1>
          <p className="page-subtitle">AI önerileri ve kaydettiğin kaynaklar</p>
        </div>
        <button
          id="btn-add-resource"
          className="btn-primary"
          onClick={() => setShowAddModal(true)}
        >
          + Kaynak Ekle
        </button>
      </div>

      {/* Stats */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "16px", marginBottom: "32px" }}>
        {[
          { label: "Toplam Kaynak", value: String(total), color: "var(--accent-cyan)" },
          { label: "Tamamlanan", value: String(completed), color: "var(--accent-green)" },
          { label: "Bekleyen", value: String(pending), color: "var(--accent-amber)" },
        ].map((s) => (
          <div key={s.label} className="glass-card" style={{ padding: "20px", display: "flex", alignItems: "center", gap: "16px" }}>
            <div>
              <div style={{ fontFamily: "'Outfit', sans-serif", fontSize: "1.8rem", fontWeight: 800, color: s.color }}>{s.value}</div>
              <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginTop: "4px" }}>{s.label}</div>
            </div>
          </div>
        ))}
      </div>

      {loading ? (
        <div style={{ textAlign: "center", padding: "60px", color: "var(--text-muted)" }}>
          <div style={{ fontSize: "2rem", marginBottom: "12px" }}>📚</div>
          <p>Kütüphane yükleniyor...</p>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
          {resources.map((res) => {
            const platformColor = PLATFORM_COLORS[res.platform] || "var(--accent-cyan)";
            return (
              <div
                key={res.resource_id}
                id={`resource-${res.resource_id}`}
                className="glass-card"
                style={{
                  padding: "20px 24px", display: "flex", alignItems: "center", gap: "20px",
                  opacity: res.is_completed ? 0.7 : 1,
                  borderLeft: res.is_completed ? "2px solid var(--accent-green)" : "2px solid transparent",
                  transition: "all 0.25s ease",
                }}
              >
                <div style={{
                  width: "48px", height: "48px", borderRadius: "var(--radius-sm)",
                  background: `${platformColor}12`, border: `1px solid ${platformColor}30`,
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: "1.1rem", flexShrink: 0,
                }}>
                  {PLATFORM_ICON[res.platform] || "🔗"}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <a
                    href={res.url} target="_blank" rel="noopener noreferrer"
                    style={{
                      fontWeight: 600, fontSize: "0.95rem", display: "block", marginBottom: "6px",
                      textDecoration: res.is_completed ? "line-through" : "none",
                      color: res.is_completed ? "var(--text-muted)" : "var(--text-primary)",
                      overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap",
                    }}
                  >
                    {res.title} ↗
                  </a>
                  <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
                    <span style={{ padding: "2px 10px", borderRadius: "999px", fontSize: "0.7rem", background: `${platformColor}15`, color: platformColor, border: `1px solid ${platformColor}30` }}>
                      {res.platform}
                    </span>
                    {res.skill_tags.map((t) => (
                      <span key={t} style={{ padding: "2px 10px", borderRadius: "999px", fontSize: "0.7rem", background: "rgba(124,58,237,0.1)", color: "var(--accent-violet)", border: "1px solid rgba(124,58,237,0.2)" }}>
                        {t}
                      </span>
                    ))}
                  </div>
                </div>
                <div style={{ textAlign: "right", flexShrink: 0, display: "flex", flexDirection: "column", gap: "8px", alignItems: "flex-end" }}>
                  <p style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>{res.saved_at}</p>
                  {res.is_completed ? (
                    <span style={{ padding: "4px 12px", borderRadius: "999px", fontSize: "0.75rem", background: "rgba(16,185,129,0.1)", color: "var(--accent-green)", border: "1px solid rgba(16,185,129,0.2)" }}>
                      ✓ Tamamlandı
                    </span>
                  ) : (
                    <button
                      onClick={() => handleComplete(res.resource_id)}
                      style={{
                        padding: "5px 12px", background: "rgba(16,185,129,0.06)",
                        border: "1px solid rgba(16,185,129,0.2)", borderRadius: "999px",
                        color: "var(--accent-green)", cursor: "pointer", fontSize: "0.75rem",
                        fontFamily: "'Inter', sans-serif", transition: "all 0.2s ease",
                      }}
                    >
                      +{res.xp_reward} XP Tamamla
                    </button>
                  )}
                  <button
                    onClick={() => handleDelete(res.resource_id)}
                    style={{
                      padding: "4px 10px", background: "rgba(239,68,68,0.05)",
                      border: "1px solid rgba(239,68,68,0.15)", borderRadius: "999px",
                      color: "#ef4444", cursor: "pointer", fontSize: "0.72rem",
                      fontFamily: "'Inter', sans-serif", transition: "all 0.2s ease",
                    }}
                  >
                    Sil
                  </button>
                </div>
              </div>
            );
          })}
          {resources.length === 0 && (
            <div style={{ textAlign: "center", padding: "60px", color: "var(--text-muted)" }}>
              <div style={{ fontSize: "2rem", marginBottom: "8px" }}>📭</div>
              <p>Henüz kaynak eklenmedi. İlk kaynağını ekle!</p>
            </div>
          )}
        </div>
      )}

      {/* Add Resource Modal */}
      {showAddModal && (
        <>
          <div onClick={() => setShowAddModal(false)} style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.6)", backdropFilter: "blur(6px)", zIndex: 9000 }} />
          <div style={{
            position: "fixed", top: "50%", left: "50%", transform: "translate(-50%,-50%)",
            width: "min(480px, 90vw)", background: "var(--surface-primary)",
            border: "1px solid var(--glass-border)", borderRadius: "20px",
            padding: "32px", zIndex: 9001, display: "flex", flexDirection: "column", gap: "20px",
            boxShadow: "0 32px 80px rgba(0,0,0,0.5)",
            animation: "scaleIn 0.25s cubic-bezier(0.16, 1, 0.3, 1)",
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <h2 style={{ fontFamily: "'Outfit', sans-serif", fontSize: "1.2rem", fontWeight: 700 }}>Kaynak Ekle</h2>
              <button onClick={() => setShowAddModal(false)} style={{ background: "none", border: "none", color: "var(--text-muted)", cursor: "pointer", fontSize: "1.1rem" }}>✕</button>
            </div>
            {[
              { label: "Başlık *", key: "title", type: "text", placeholder: "AWS VPC Tutorial..." },
              { label: "URL *", key: "url", type: "url", placeholder: "https://..." },
              { label: "Etiketler (virgülle ayır)", key: "skill_tags", type: "text", placeholder: "AWS, Cloud, VPC" },
            ].map((field) => (
              <div key={field.key}>
                <label style={{ display: "block", fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: "6px" }}>{field.label}</label>
                <input
                  type={field.type}
                  placeholder={field.placeholder}
                  value={form[field.key as keyof typeof form]}
                  onChange={(e) => setForm((prev) => ({ ...prev, [field.key]: e.target.value }))}
                  style={{
                    width: "100%", padding: "10px 14px", background: "var(--glass-bg)",
                    border: "1px solid var(--glass-border)", borderRadius: "var(--radius-sm)",
                    color: "var(--text-primary)", fontFamily: "'Inter', sans-serif", fontSize: "0.9rem",
                    outline: "none", boxSizing: "border-box",
                  }}
                />
              </div>
            ))}
            <div>
              <label style={{ display: "block", fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: "6px" }}>Platform</label>
              <select
                value={form.platform}
                onChange={(e) => setForm((prev) => ({ ...prev, platform: e.target.value }))}
                style={{
                  width: "100%", padding: "10px 14px", background: "var(--glass-bg)",
                  border: "1px solid var(--glass-border)", borderRadius: "var(--radius-sm)",
                  color: "var(--text-primary)", fontFamily: "'Inter', sans-serif", fontSize: "0.9rem", outline: "none",
                }}
              >
                {["YouTube", "Udemy", "Docs", "Article"].map((p) => <option key={p} value={p}>{p}</option>)}
              </select>
            </div>
            <button
              onClick={handleAdd}
              disabled={submitting}
              style={{
                padding: "12px", background: "linear-gradient(135deg, rgba(0,229,255,0.15), rgba(124,58,237,0.15))",
                border: "1px solid var(--accent-cyan)", borderRadius: "var(--radius-md)",
                color: "var(--accent-cyan)", fontFamily: "'Inter', sans-serif", fontSize: "0.95rem",
                fontWeight: 600, cursor: submitting ? "not-allowed" : "pointer", opacity: submitting ? 0.7 : 1,
                transition: "all 0.2s ease",
              }}
            >
              {submitting ? "Ekleniyor..." : "Kütüphaneye Ekle"}
            </button>
          </div>
        </>
      )}

      <style>{`
        @keyframes fadeInDown { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes scaleIn { from { opacity: 0; transform: translate(-50%,-50%) scale(0.92); } to { opacity: 1; transform: translate(-50%,-50%) scale(1); } }
      `}</style>
    </div>
  );
}
