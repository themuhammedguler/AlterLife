"use client";

export default function SettingsPage() {
  return (
    <div className="page-container" style={{ maxWidth: "800px" }}>
      <div className="page-header">
        <h1 className="page-title">
          <span className="text-gradient">Ayarlar & Entegrasyonlar</span>
        </h1>
        <p className="page-subtitle">Profil, API baglantilari ve hesap yonetimi</p>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>

        {/* Profile Section */}
        <div className="glass-card" style={{ padding: "28px" }}>
          <h2 style={{ fontFamily: "'Outfit', sans-serif", fontSize: "1rem", fontWeight: 700, marginBottom: "20px" }}>
            Profil Bilgileri
          </h2>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
            {[
              { id: "input-display-name", label: "Gorunen Isim", value: "Sedef Kazan", type: "text" },
              { id: "input-email", label: "E-posta", value: "sedef@alterlife.io", type: "email" },
              { id: "input-role", label: "Mevcut Rol", value: "Product Owner", type: "text" },
              { id: "input-exp", label: "Deneyim (Yil)", value: "3", type: "number" },
            ].map((f) => (
              <div key={f.id}>
                <label style={{ fontSize: "0.8rem", color: "var(--text-secondary)", marginBottom: "6px", display: "block" }}>
                  {f.label}
                </label>
                <input
                  id={f.id}
                  type={f.type}
                  defaultValue={f.value}
                  style={{
                    width: "100%", padding: "10px 14px",
                    background: "rgba(255,255,255,0.04)",
                    border: "1px solid var(--glass-border)",
                    borderRadius: "var(--radius-md)",
                    color: "var(--text-primary)", fontSize: "0.9rem", outline: "none",
                    fontFamily: "'Inter', sans-serif",
                  }}
                />
              </div>
            ))}
          </div>
          <button
            id="btn-save-profile"
            className="btn-primary"
            style={{ marginTop: "20px" }}
            onClick={() => alert("Profil kaydedildi (simülasyon)")}
          >
            Kaydet
          </button>
        </div>

        {/* Avatar Section */}
        <div className="glass-card" style={{ padding: "28px" }}>
          <h2 style={{ fontFamily: "'Outfit', sans-serif", fontSize: "1rem", fontWeight: 700, marginBottom: "16px" }}>
            RPG Avatari
          </h2>
          <div style={{ display: "flex", alignItems: "center", gap: "20px" }}>
            <div
              style={{
                width: "80px", height: "80px", borderRadius: "50%",
                background: "var(--gradient-cyan-violet)",
                display: "flex", alignItems: "center", justifyContent: "center",
                flexShrink: 0,
                boxShadow: "var(--shadow-glow-violet)",
              }}
            />
            <div style={{ flex: 1 }}>
              <p style={{ fontSize: "0.9rem", color: "var(--text-secondary)", marginBottom: "12px" }}>
                Avatarini yeniden uret veya fotograf yukle
              </p>
              <div style={{ display: "flex", gap: "10px" }}>
                <button
                  id="btn-regenerate-avatar"
                  className="btn-ghost"
                  onClick={() => alert("Avatar yeniden üretme – Hafta 2'de aktif")}
                >
                  Yeniden Uret
                </button>
                <button
                  id="btn-upload-photo"
                  className="btn-ghost"
                  onClick={() => alert("Fotoğraf yükleme – Hafta 2'de aktif")}
                >
                  Fotograf Yukle
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Integrations */}
        <div className="glass-card" style={{ padding: "28px" }}>
          <h2 style={{ fontFamily: "'Outfit', sans-serif", fontSize: "1rem", fontWeight: 700, marginBottom: "20px" }}>
            API Entegrasyonlari
          </h2>
          {[
            {
              id: "google-calendar",
              name: "Google Calendar",
              desc: "Calisma surelerini otomatik takip et",
              label: "CAL",
              connected: false,
              comingSoon: false,
            },
            {
              id: "github",
              name: "GitHub",
              desc: "Commit'lerini gorev tamamlama olarak say",
              label: "GIT",
              connected: false,
              comingSoon: false,
            },
            {
              id: "youtube",
              name: "YouTube API",
              desc: "Kisisel ogrenme video onerileri",
              label: "YT",
              connected: false,
              comingSoon: true,
            },
          ].map((int) => (
            <div
              key={int.id}
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                padding: "16px",
                background: int.connected ? "rgba(16,185,129,0.06)" : "var(--glass-bg)",
                border: `1px solid ${int.connected ? "rgba(16,185,129,0.2)" : "var(--glass-border)"}`,
                borderRadius: "var(--radius-md)",
                marginBottom: "12px",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
                <div
                  style={{
                    width: "36px",
                    height: "36px",
                    borderRadius: "var(--radius-sm)",
                    background: "rgba(255,255,255,0.04)",
                    border: "1px solid var(--glass-border)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: "0.75rem",
                    fontWeight: 700,
                    color: "var(--text-muted)",
                  }}
                >
                  {int.label}
                </div>
                <div>
                  <p style={{ fontWeight: 600, fontSize: "0.9rem" }}>{int.name}</p>
                  <p style={{ fontSize: "0.78rem", color: "var(--text-muted)" }}>{int.desc}</p>
                </div>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                {int.connected ? (
                  <>
                    <span className="status-dot active" />
                    <span style={{ fontSize: "0.8rem", color: "var(--accent-green)" }}>Bagli</span>
                  </>
                ) : (
                  <button
                    id={`btn-connect-${int.id}`}
                    className="btn-primary"
                    style={{ padding: "8px 16px", fontSize: "0.8rem" }}
                    onClick={() => alert(`${int.name} entegrasyonu Hafta 3'te aktif olacak`)}
                    disabled={int.comingSoon}
                  >
                    {int.comingSoon ? "Yakinda" : "Bagla"}
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Danger Zone */}
        <div
          className="glass-card"
          style={{ padding: "28px", border: "1px solid rgba(239, 68, 68, 0.2)" }}
        >
          <h2 style={{ fontFamily: "'Outfit', sans-serif", fontSize: "1rem", fontWeight: 700, marginBottom: "8px", color: "#ef4444" }}>
            Tehlikeli Bolge
          </h2>
          <p style={{ fontSize: "0.85rem", color: "var(--text-muted)", marginBottom: "16px" }}>
            Hesabi sil veya tum simulasyonlari sifirla
          </p>
          <button
            id="btn-delete-account"
            style={{
              padding: "10px 20px",
              background: "rgba(239, 68, 68, 0.08)",
              border: "1px solid rgba(239, 68, 68, 0.3)",
              borderRadius: "var(--radius-md)",
              color: "#ef4444",
              cursor: "pointer",
              fontSize: "0.85rem",
              fontFamily: "'Inter', sans-serif",
            }}
            onClick={() => alert("Bu islem geri alinamaz – Onay gerektirir")}
          >
            Hesabi Sil
          </button>
        </div>

      </div>
    </div>
  );
}
