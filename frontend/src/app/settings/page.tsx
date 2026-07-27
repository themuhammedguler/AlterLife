"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import {
  deleteAccount,
  disconnectCalendar,
  disconnectGithub,
  generateAvatar,
  getCalendarStatus,
  getGithubStatus,
  getProfile,
  logout,
  updateProfile,
} from "@/lib/api";

export default function SettingsPage() {
  const router = useRouter();
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [avatarLoading, setAvatarLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [calendarStatus, setCalendarStatus] = useState<{ is_connected: boolean; username?: string; last_synced?: string } | null>(null);
  const [githubStatus, setGithubStatus] = useState<{ is_connected: boolean; username?: string; last_synced?: string } | null>(null);
  const [notifQuestComplete, setNotifQuestComplete] = useState(true);
  const [notifLevelUp, setNotifLevelUp] = useState(true);
  const [notifWeeklyReport, setNotifWeeklyReport] = useState(false);
  const [dayType, setDayType] = useState<"light" | "normal" | "busy">("normal");
  const [focusTime, setFocusTime] = useState<"morning" | "afternoon" | "evening" | "night">("evening");
  const [mood, setMood] = useState<"low" | "steady" | "playful" | "high">("playful");
  const [availableMinutes, setAvailableMinutes] = useState(60);

  // Profile fields state
  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("");
  const [exp, setExp] = useState("1");
  const [description, setDescription] = useState("");
  const photoInputRef = useRef<HTMLInputElement>(null);

  const loadUserProfile = async () => {
    setLoading(true);
    try {
      const data = await getProfile();
      setProfile(data);
      setDisplayName(data.display_name || "");
      setEmail(data.email || "");
      setRole(data.role || "");
      setDayType(data.daily_preferences?.day_type || "normal");
      setFocusTime(data.daily_preferences?.best_focus_time || "evening");
      setMood(data.daily_preferences?.mood || "playful");
      setAvailableMinutes(data.daily_preferences?.available_minutes || 60);
      // Fetch details from local storage if not available on profile API directly
      const local = localStorage.getItem("alterlife_onboarding");
      if (local) {
        const parsed = JSON.parse(local);
        setExp(parsed.age || "1");
      }
    } catch (err: any) {
      setError(err.message || "Profil yüklenirken bir hata oluştu.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUserProfile();
    // Load integration statuses
    getCalendarStatus().then(setCalendarStatus).catch(console.error);
    getGithubStatus().then(setGithubStatus).catch(console.error);
  }, []);

  const handleSaveProfile = async () => {
    setSuccess(null);
    setError(null);
    try {
      const updated = await updateProfile({
        display_name: displayName,
        role,
        experience_years: Number(exp) || 0,
        daily_preferences: {
          day_type: dayType,
          best_focus_time: focusTime,
          mood,
          available_minutes: availableMinutes,
          include_social: true,
        },
      });
      setProfile(updated);
      const local = localStorage.getItem("alterlife_onboarding");
      const current = local ? JSON.parse(local) : {};
      current.age = exp;
      localStorage.setItem("alterlife_onboarding", JSON.stringify(current));
      
      setSuccess("Profil başarıyla kaydedildi.");
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Profil kaydedilemedi.");
    }
  };

  const handleRegenerateAvatar = async () => {
    setAvatarLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const targetDesc = description || `Cyberpunk style avatar for ${role || "explorer"}`;
      const data = await generateAvatar(targetDesc);
      if (data.avatar_url) {
        setProfile((prev: any) => ({ ...prev, avatar_url: data.avatar_url }));
        setSuccess("Yeni avatar başarıyla üretildi!");
        setTimeout(() => setSuccess(null), 3000);
      }
    } catch (err: any) {
      setError(err.message || "Avatar üretilirken bir hata oluştu.");
    } finally {
      setAvatarLoading(false);
    }
  };

  const handlePhotoUpload = () => {
    photoInputRef.current?.click();
  };

  const handlePhotoSelected = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    if (!["image/jpeg", "image/png", "image/webp"].includes(file.type)) {
      setError("Yalnızca JPEG, PNG veya WebP fotoğraf yükleyebilirsiniz.");
      return;
    }
    if (file.size > 3 * 1024 * 1024) {
      setError("Fotoğraf en fazla 3 MB olabilir.");
      return;
    }

    setAvatarLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const photoBase64 = await new Promise<string>((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(String(reader.result));
        reader.onerror = () => reject(new Error("Fotoğraf okunamadı."));
        reader.readAsDataURL(file);
      });
      const data = await generateAvatar(description, photoBase64, file.type);
      if (data.avatar_url) {
        setProfile((prev: any) => ({ ...prev, avatar_url: data.avatar_url }));
        setSuccess(data.message || "Fotoğraftan avatar oluşturuldu.");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Fotoğraftan avatar oluşturulamadı.");
    } finally {
      setAvatarLoading(false);
    }
  };

  const startOAuth = (provider: "google-calendar" | "github") => {
    const state = crypto.randomUUID();
    sessionStorage.setItem(`alterlife_oauth_state_${provider}`, state);
    const callbackProvider = provider === "google-calendar" ? "google" : "github";
    const redirectUri = `${window.location.origin}/settings/oauth/${callbackProvider}`;

    if (provider === "google-calendar") {
      const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;
      if (!clientId) {
        setError("Google OAuth istemci kimliği yapılandırılmamış.");
        return;
      }
      const params = new URLSearchParams({
        client_id: clientId,
        redirect_uri: redirectUri,
        response_type: "code",
        scope: "openid email https://www.googleapis.com/auth/calendar.events",
        access_type: "offline",
        prompt: "consent",
        state,
      });
      window.location.assign(`https://accounts.google.com/o/oauth2/v2/auth?${params}`);
      return;
    }

    const clientId = process.env.NEXT_PUBLIC_GITHUB_CLIENT_ID;
    if (!clientId) {
      setError("GitHub OAuth istemci kimliği yapılandırılmamış.");
      return;
    }
    const params = new URLSearchParams({
      client_id: clientId,
      redirect_uri: redirectUri,
      scope: "read:user",
      state,
    });
    window.location.assign(`https://github.com/login/oauth/authorize?${params}`);
  };

  return (
    <div className="page-container" style={{ maxWidth: "800px", padding: "40px 24px" }}>
      <div className="page-header" style={{ marginBottom: "32px" }}>
        <h1 className="page-title" style={{ fontSize: "2rem", fontWeight: 800 }}>
          <span className="text-gradient">Ayarlar & Entegrasyonlar</span>
        </h1>
        <p className="page-subtitle" style={{ color: "var(--text-secondary)", fontSize: "0.95rem" }}>
          Profil, API bağlantıları ve hesap yönetimi
        </p>
      </div>

      {error && (
        <div
          style={{
            padding: "12px 16px",
            background: "rgba(255, 61, 0, 0.1)",
            border: "1px solid rgba(255, 61, 0, 0.3)",
            borderRadius: "var(--radius-md)",
            color: "#ff3d00",
            fontSize: "0.85rem",
            marginBottom: "20px",
          }}
        >
          {error}
        </div>
      )}

      {success && (
        <div
          style={{
            padding: "12px 16px",
            background: "rgba(16, 185, 129, 0.1)",
            border: "1px solid rgba(16, 185, 129, 0.3)",
            borderRadius: "var(--radius-md)",
            color: "var(--accent-green)",
            fontSize: "0.85rem",
            marginBottom: "20px",
          }}
        >
          {success}
        </div>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>

        {/* Profile Section */}
        <div className="glass-card" style={{ padding: "28px" }}>
          <h2 style={{ fontFamily: "'Outfit', sans-serif", fontSize: "1.1rem", fontWeight: 700, marginBottom: "20px" }}>
            Profil Bilgileri
          </h2>
          {loading ? (
            <p style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>Yükleniyor...</p>
          ) : (
            <>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
                <div>
                  <label style={{ fontSize: "0.8rem", color: "var(--text-secondary)", marginBottom: "6px", display: "block" }}>
                    Görünen İsim
                  </label>
                  <input
                    id="input-display-name"
                    type="text"
                    value={displayName}
                    onChange={(e) => setDisplayName(e.target.value)}
                    style={inputStyle}
                  />
                </div>
                <div>
                  <label style={{ fontSize: "0.8rem", color: "var(--text-secondary)", marginBottom: "6px", display: "block" }}>
                    E-posta
                  </label>
                  <input
                    id="input-email"
                    type="email"
                    value={email}
                    disabled
                    style={{ ...inputStyle, opacity: 0.6, cursor: "not-allowed" }}
                  />
                </div>
                <div>
                  <label style={{ fontSize: "0.8rem", color: "var(--text-secondary)", marginBottom: "6px", display: "block" }}>
                    Mevcut Rol
                  </label>
                  <input
                    id="input-role"
                    type="text"
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                    style={inputStyle}
                  />
                </div>
                <div>
                  <label style={{ fontSize: "0.8rem", color: "var(--text-secondary)", marginBottom: "6px", display: "block" }}>
                    Yaş / Deneyim (Yıl)
                  </label>
                  <input
                    id="input-exp"
                    type="number"
                    value={exp}
                    onChange={(e) => setExp(e.target.value)}
                    style={inputStyle}
                  />
                </div>
              </div>
              <button
                id="btn-save-profile"
                className="btn-primary"
                style={{ marginTop: "20px" }}
                onClick={handleSaveProfile}
              >
                Kaydet
              </button>
            </>
          )}
        </div>

        <div className="glass-card" style={{ padding: "28px" }}>
          <h2 style={{ fontFamily: "'Outfit', sans-serif", fontSize: "1.1rem", fontWeight: 700, marginBottom: "10px" }}>
            Günlük Ritim
          </h2>
          <p style={{ fontSize: "0.82rem", color: "var(--text-muted)", marginBottom: "18px" }}>
            Dashboard görevleri bu tercihlere göre otomatik daha gerçekçi ve eğlenceli planlanır.
          </p>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "14px" }}>
            <select value={dayType} onChange={(event) => setDayType(event.target.value as any)} style={selectStyle}>
              <option value="busy">Yoğun günlerim olur</option>
              <option value="normal">Dengeli giderim</option>
              <option value="light">Rahat bloklarım var</option>
            </select>
            <select value={focusTime} onChange={(event) => setFocusTime(event.target.value as any)} style={selectStyle}>
              <option value="morning">Sabah odaklanırım</option>
              <option value="afternoon">Öğlen açılırım</option>
              <option value="evening">Akşam güçlenirim</option>
              <option value="night">Gece üretirim</option>
            </select>
            <select value={mood} onChange={(event) => setMood(event.target.value as any)} style={selectStyle}>
              <option value="low">Düşük enerji modu</option>
              <option value="steady">Sakin ve stabil</option>
              <option value="playful">Eğlenceli quest modu</option>
              <option value="high">Boss fight modu</option>
            </select>
            <select value={availableMinutes} onChange={(event) => setAvailableMinutes(Number(event.target.value))} style={selectStyle}>
              <option value={30}>Günde 30 dk</option>
              <option value={60}>Günde 60 dk</option>
              <option value={90}>Günde 90 dk</option>
              <option value={120}>Günde 120 dk</option>
            </select>
          </div>
          <button className="btn-primary" style={{ marginTop: "18px" }} onClick={handleSaveProfile}>
            Ritim Tercihlerini Kaydet
          </button>
        </div>

        {/* Avatar Section */}
        <div className="glass-card" style={{ padding: "28px" }}>
          <h2 style={{ fontFamily: "'Outfit', sans-serif", fontSize: "1.1rem", fontWeight: 700, marginBottom: "16px" }}>
            RPG Avatarı
          </h2>
          <div style={{ display: "flex", alignItems: "center", gap: "24px" }}>
            <div
              style={{
                width: "80px",
                height: "80px",
                borderRadius: "50%",
                background: "var(--gradient-cyan-violet)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
                boxShadow: "var(--shadow-glow-violet)",
                overflow: "hidden",
                border: "2px solid rgba(0, 229, 255, 0.3)",
              }}
            >
              {profile?.avatar_url ? (
                <img
                  src={profile.avatar_url}
                  alt="RPG Avatar"
                  style={{ width: "100%", height: "100%", objectFit: "cover" }}
                />
              ) : (
                <div style={{ fontSize: "1.2rem", fontWeight: 800, color: "var(--bg-primary)" }}>
                  {displayName ? displayName.substring(0, 2).toUpperCase() : "AL"}
                </div>
              )}
            </div>
            <div style={{ flex: 1 }}>
              <p style={{ fontSize: "0.9rem", color: "var(--text-secondary)", marginBottom: "12px" }}>
                Karakter görünümünü betimle, yapay zeka ile yeniden avatar üret.
              </p>
              
              <input
                type="text"
                placeholder="Örn: Cyberpunk hacker, neon glasses, dark background"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                style={{ ...inputStyle, marginBottom: "12px" }}
              />

              <div style={{ display: "flex", gap: "10px" }}>
                <button
                  id="btn-regenerate-avatar"
                  className="btn-ghost"
                  disabled={avatarLoading}
                  onClick={handleRegenerateAvatar}
                >
                  {avatarLoading ? "Üretiliyor..." : "Yeniden Üret"}
                </button>
                <button
                  id="btn-upload-photo"
                  className="btn-ghost"
                  onClick={handlePhotoUpload}
                >
                  Görsel Özelleştir
                </button>
                <input
                  ref={photoInputRef}
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  onChange={handlePhotoSelected}
                  style={{ display: "none" }}
                  aria-label="Avatar fotoğrafı seç"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Integrations */}
        <div className="glass-card" style={{ padding: "28px" }}>
          <h2 style={{ fontFamily: "'Outfit', sans-serif", fontSize: "1.1rem", fontWeight: 700, marginBottom: "6px" }}>
            API Entegrasyonları
          </h2>
          <p style={{ fontSize: "0.82rem", color: "var(--text-muted)", marginBottom: "20px" }}>
            Dış hizmetlere bağlanarak görev doğrulamasını otomatikleştir
          </p>

          {/* Google Calendar */}
          {[
            {
              id: "google-calendar",
              name: "Google Calendar",
              desc: "Çalışma sürelerini otomatik takip et",
              label: "CAL",
              status: calendarStatus,
              labelColor: "var(--accent-cyan)",
            },
            {
              id: "github",
              name: "GitHub",
              desc: "Commit'lerini görev tamamlama olarak say",
              label: "GIT",
              status: githubStatus,
              labelColor: "var(--accent-violet)",
            },
            {
              id: "youtube",
              name: "YouTube API",
              desc: "Kişisel öğrenme video önerileri",
              label: "YT",
              status: null,
              labelColor: "var(--accent-pink)",
              comingSoon: true,
            },
          ].map((int) => {
            const isConnected = int.status?.is_connected ?? false;
            return (
              <div
                key={int.id}
                style={{
                  display: "flex", alignItems: "center", justifyContent: "space-between",
                  padding: "16px",
                  background: isConnected ? "rgba(16,185,129,0.06)" : "var(--glass-bg)",
                  border: `1px solid ${isConnected ? "rgba(16,185,129,0.2)" : "var(--glass-border)"}`,
                  borderRadius: "var(--radius-md)", marginBottom: "12px",
                  transition: "all 0.25s ease",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
                  <div style={{
                    width: "36px", height: "36px", borderRadius: "var(--radius-sm)",
                    background: `${int.labelColor}10`, border: `1px solid ${int.labelColor}30`,
                    display: "flex", alignItems: "center", justifyContent: "center",
                    fontSize: "0.72rem", fontWeight: 700, color: int.labelColor,
                  }}>
                    {int.label}
                  </div>
                  <div>
                    <p style={{ fontWeight: 600, fontSize: "0.9rem" }}>{int.name}</p>
                    <p style={{ fontSize: "0.78rem", color: "var(--text-muted)" }}>{int.desc}</p>
                    {isConnected && int.status?.username && (
                      <p style={{ fontSize: "0.72rem", color: "var(--accent-green)", marginTop: "2px" }}>@{int.status.username}</p>
                    )}
                  </div>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                  {isConnected ? (
                    <>
                      <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "var(--accent-green)", display: "inline-block", boxShadow: "0 0 6px var(--accent-green)" }} />
                      <span style={{ fontSize: "0.8rem", color: "var(--accent-green)", fontWeight: 500 }}>Bağlı</span>
                      <button
                        type="button"
                        className="btn-ghost"
                        onClick={async () => {
                          if (int.id === "google-calendar") {
                            await disconnectCalendar();
                            setCalendarStatus({ is_connected: false });
                          } else {
                            await disconnectGithub();
                            setGithubStatus({ is_connected: false });
                          }
                        }}
                      >
                        Ayır
                      </button>
                    </>
                  ) : (int as any).comingSoon ? (
                    <span style={{ fontSize: "0.78rem", color: "var(--text-muted)", padding: "6px 12px", border: "1px solid var(--glass-border)", borderRadius: "999px" }}>Yakında</span>
                  ) : (
                    <button
                      id={`btn-connect-${int.id}`}
                      style={{
                        padding: "8px 16px", fontSize: "0.8rem",
                        background: "rgba(0,229,255,0.08)", border: "1px solid rgba(0,229,255,0.25)",
                        borderRadius: "var(--radius-md)", color: "var(--accent-cyan)", cursor: "pointer",
                        fontFamily: "'Inter', sans-serif", fontWeight: 500, transition: "all 0.2s ease",
                      }}
                      onClick={() => startOAuth(int.id as "google-calendar" | "github")}
                    >
                      Bağla
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Notifications */}
        <div className="glass-card" style={{ padding: "28px" }}>
          <h2 style={{ fontFamily: "'Outfit', sans-serif", fontSize: "1.1rem", fontWeight: 700, marginBottom: "6px" }}>
            Bildirim Tercihleri
          </h2>
          <p style={{ fontSize: "0.82rem", color: "var(--text-muted)", marginBottom: "20px" }}>
            Hangi durumlarda bildirim almak istediğini seç
          </p>
          {[
            { label: "Görev tamamlandı bildirimi", value: notifQuestComplete, setter: setNotifQuestComplete },
            { label: "Seviye atlama bildirimi", value: notifLevelUp, setter: setNotifLevelUp },
            { label: "Haftalık ilerleme raporu", value: notifWeeklyReport, setter: setNotifWeeklyReport },
          ].map((notif) => (
            <div key={notif.label} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
              <span style={{ fontSize: "0.9rem", color: "var(--text-secondary)" }}>{notif.label}</span>
              <button
                onClick={() => {
                  notif.setter(!notif.value);
                  setSuccess("Bildirim tercihi güncellendi.");
                  setTimeout(() => setSuccess(null), 2000);
                }}
                style={{
                  width: "44px", height: "24px", borderRadius: "999px", border: "none", cursor: "pointer",
                  background: notif.value ? "var(--accent-cyan)" : "rgba(255,255,255,0.1)",
                  position: "relative", transition: "background 0.3s ease",
                }}
              >
                <span style={{
                  position: "absolute", top: "3px",
                  left: notif.value ? "22px" : "3px",
                  width: "18px", height: "18px", borderRadius: "50%",
                  background: "white", transition: "left 0.3s ease",
                  boxShadow: "0 1px 4px rgba(0,0,0,0.3)",
                }} />
              </button>
            </div>
          ))}
        </div>

        {/* Danger Zone */}
        <div
          className="glass-card"
          style={{ padding: "28px", border: "1px solid rgba(239, 68, 68, 0.2)" }}
        >
          <h2 style={{ fontFamily: "'Outfit', sans-serif", fontSize: "1.1rem", fontWeight: 700, marginBottom: "8px", color: "#ef4444" }}>
            Tehlikeli Bölge
          </h2>
          <p style={{ fontSize: "0.85rem", color: "var(--text-muted)", marginBottom: "16px" }}>
            Hesabı sil veya tüm simülasyonları sıfırla
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
            onClick={async () => {
              if (!window.confirm("Hesabınız ve tüm AlterLife verileriniz kalıcı olarak silinecek. Devam edilsin mi?")) return;
              try {
                await deleteAccount();
                logout();
                router.replace("/");
              } catch (err) {
                setError(err instanceof Error ? err.message : "Hesap silinemedi.");
              }
            }}
          >
            Hesabı Sil
          </button>
        </div>

      </div>
    </div>
  );
}

const inputStyle: React.CSSProperties = {
  width: "100%",
  padding: "10px 14px",
  background: "rgba(255,255,255,0.04)",
  border: "1px solid var(--glass-border)",
  borderRadius: "var(--radius-md)",
  color: "var(--text-primary)",
  fontSize: "0.9rem",
  outline: "none",
  fontFamily: "'Inter', sans-serif",
};

const selectStyle: React.CSSProperties = {
  ...inputStyle,
  cursor: "pointer",
};
