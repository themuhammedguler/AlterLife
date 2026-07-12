"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { submitOnboarding } from "@/lib/api";

// ── Veri Yapıları ─────────────────────────────────────────────────────────────

const STEPS = [
  { id: 1, title: "Temel Bilgiler", subtitle: "Şu an hayatının hangi aşamasındasın?" },
  { id: 2, title: "Gelecek Planın", subtitle: "Hangi alanda ve nasıl çalışmak istersin?" },
  { id: 3, title: "İlk Serüvenin", subtitle: "Hayalindeki hedefini bizimle paylaş" },
];

const CURRENT_STATUS = [
  { id: "working", label: "Çalışıyorum" },
  { id: "seeking", label: "İş arıyorum" },
  { id: "student", label: "Öğrenciyim" },
  { id: "freelance", label: "Freelance / Bağımsız çalışıyorum" },
  { id: "career_change", label: "Kariyer değişikliği düşünüyorum" },
  { id: "unknown", label: "Kararsızım / Bilmiyorum" },
];

const FIELDS = [
  { id: "software", label: "Yazılım / Teknoloji" },
  { id: "design", label: "Tasarım / Sanat" },
  { id: "finance", label: "Finans / İş Dünyası" },
  { id: "health", label: "Sağlık / Tıp" },
  { id: "engineering", label: "Mühendislik" },
  { id: "startup", label: "Girişimcilik / Kendi işim" },
  { id: "unknown", label: "Henüz bilmiyorum" },
];

const WORK_PREFS = [
  { id: "remote", label: "Uzaktan (Remote) çalışmak" },
  { id: "travel", label: "Sık seyahat etmek / Dijital göçebe olmak" },
  { id: "abroad", label: "Başka bir ülkeye taşınmak" },
  { id: "own_biz", label: "Kendi şirketimi / işimi kurmak" },
];

// ── Component ─────────────────────────────────────────────────────────────────

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [status, setStatus] = useState("");
  const [age, setAge] = useState("");
  const [city, setCity] = useState("");
  const [field, setField] = useState("");
  const [workPrefs, setWorkPrefs] = useState<string[]>([]);
  const [freeGoal, setFreeGoal] = useState("");

  function toggleWorkPref(id: string) {
    setWorkPrefs((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  }

  async function handleFinish() {
    setLoading(true);
    setError(null);
    try {
      const profileData = {
        status,
        age,
        city,
        field,
        workPrefs,
        freeGoal,
      };

      // Tarayıcı hafızasına yedek olarak kaydedelim
      if (typeof window !== "undefined") {
        localStorage.setItem("alterlife_onboarding", JSON.stringify(profileData));
      }

      // Backend API Onboarding çağrısı (initial simulation'ı otomatik kurar)
      await submitOnboarding(profileData);

      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Simülasyon başlatılamadı. Lütfen tekrar deneyin.");
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div
        style={{
          minHeight: "100vh",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: "24px",
          position: "relative",
          zIndex: 1,
          textAlign: "center",
        }}
      >
        <style>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
        <div className="glass-card animate-fade-up" style={{ padding: "48px 40px", maxWidth: "460px" }}>
          <div style={{ marginBottom: "28px" }}>
            <div
              style={{
                width: "56px",
                height: "56px",
                borderRadius: "50%",
                border: "3px solid rgba(0, 229, 255, 0.1)",
                borderTopColor: "var(--accent-cyan)",
                animation: "spin 1s linear infinite",
                margin: "0 auto",
              }}
            />
          </div>
          <h2 style={{ fontSize: "1.4rem", fontWeight: 800, marginBottom: "12px", fontFamily: "'Outfit', sans-serif" }}>
            <span className="text-gradient">Simülasyon Yapılandırılıyor</span>
          </h2>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem", lineHeight: 1.6, marginBottom: "16px" }}>
            LangGraph Karar Motoru ağları kuruluyor ve Gemini ile ilk hedefinize yönelik RPG karar ağacınız oluşturuluyor.
          </p>
          <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", fontStyle: "italic" }}>
            &ldquo;Evren dallanıyor, veri yolları çiziliyor...&rdquo;
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "24px",
        position: "relative",
        zIndex: 1,
      }}
    >
      <div style={{ width: "100%", maxWidth: "580px" }}>

        {/* Progress Bar */}
        <div style={{ marginBottom: "36px" }}>
          <div style={{ display: "flex", gap: "8px", marginBottom: "12px" }}>
            {STEPS.map((s) => (
              <div
                key={s.id}
                style={{
                  flex: 1,
                  height: "4px",
                  borderRadius: "999px",
                  background: s.id <= step ? "var(--accent-cyan)" : "rgba(255,255,255,0.06)",
                  transition: "all-background 0.4s ease",
                }}
              />
            ))}
          </div>
          <p style={{ fontSize: "0.78rem", color: "var(--text-muted)", textAlign: "right" }}>
            Adım {step} / {STEPS.length}
          </p>
        </div>

        {/* Form Card */}
        <div className="glass-card" style={{ padding: "44px 40px" }}>
          <h1
            style={{
              fontFamily: "'Outfit', sans-serif",
              fontSize: "1.7rem",
              fontWeight: 800,
              marginBottom: "6px",
            }}
          >
            <span className="text-gradient">{STEPS[step - 1].title}</span>
          </h1>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem", marginBottom: "36px" }}>
            {STEPS[step - 1].subtitle}
          </p>

          {error && (
            <div
              style={{
                padding: "12px",
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

          {/* ── Step 1: Temel Bilgiler ────────────────────────────── */}
          {step === 1 && (
            <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
              {/* Mevcut Durum */}
              <div>
                <label style={labelStyle}>Şu anki durumunuz nedir?</label>
                <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                  {CURRENT_STATUS.map((opt) => (
                    <button
                      key={opt.id}
                      id={`status-${opt.id}`}
                      type="button"
                      onClick={() => setStatus(opt.id)}
                      style={choiceStyle(status === opt.id)}
                    >
                      <div style={radioCircle(status === opt.id)} />
                      {opt.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Yaş - Manuel Giriş */}
              <div>
                <label style={labelStyle}>Yaşınız</label>
                <input
                  id="input-age"
                  type="number"
                  min="1"
                  max="120"
                  value={age}
                  onChange={(e) => setAge(e.target.value)}
                  placeholder="Yaşınızı sayı olarak girin (Örn: 24)"
                  style={inputStyle}
                />
              </div>

              {/* Şehir */}
              <div>
                <label style={labelStyle}>Nerede yaşıyorsunuz?</label>
                <input
                  id="input-city"
                  type="text"
                  value={city}
                  onChange={(e) => setCity(e.target.value)}
                  placeholder="Yaşadığınız şehir ve ülke (Örn: İstanbul, Türkiye)"
                  style={inputStyle}
                />
              </div>
            </div>
          )}

          {/* ── Step 2: Gelecek Planı ─────────────────────────────── */}
          {step === 2 && (
            <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
              {/* İlgilenilen Alan */}
              <div>
                <label style={labelStyle}>Hangi alana yönelmek veya odaklanmak istersiniz?</label>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
                  {FIELDS.map((f) => (
                    <button
                      key={f.id}
                      id={`field-${f.id}`}
                      type="button"
                      onClick={() => setField(f.id)}
                      style={choiceStyle(field === f.id)}
                    >
                      <div style={radioCircle(field === f.id)} />
                      <span style={{ fontSize: "0.85rem" }}>{f.label}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Çalışma/Kariyer Tercihleri */}
              <div>
                <label style={labelStyle}>Çalışma veya kariyerle ilgili hayalleriniz nelerdir?</label>
                <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                  {WORK_PREFS.map((pref) => {
                    const selected = workPrefs.includes(pref.id);
                    return (
                      <button
                        key={pref.id}
                        id={`pref-${pref.id}`}
                        type="button"
                        onClick={() => toggleWorkPref(pref.id)}
                        style={choiceStyle(selected)}
                      >
                        <div
                          style={{
                            width: "16px",
                            height: "16px",
                            borderRadius: "4px",
                            border: `2px solid ${selected ? "var(--accent-cyan)" : "rgba(255,255,255,0.2)"}`,
                            background: selected ? "var(--accent-cyan)" : "transparent",
                            flexShrink: 0,
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            transition: "all 0.2s ease",
                          }}
                        >
                          {selected && (
                            <svg width="10" height="8" viewBox="0 0 10 8" fill="none">
                              <path d="M1 4L3.5 6.5L9 1" stroke="#07111e" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                            </svg>
                          )}
                        </div>
                        {pref.label}
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
          )}

          {/* ── Step 3: İlk Serüven ───────────────────────────────── */}
          {step === 3 && (
            <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
              <div>
                <label style={labelStyle}>Hayalinizdeki hedefinizi veya sormak istediğiniz ana soruyu buraya yazın:</label>
                <textarea
                  id="input-free-goal"
                  value={freeGoal}
                  onChange={(e) => setFreeGoal(e.target.value)}
                  placeholder="Örn: 2 yıl içinde Berlin'de yazılım geliştirici olarak çalışmak istiyorum, ne yapmalıyım?"
                  rows={5}
                  style={{ ...inputStyle, resize: "none" }}
                />
              </div>

              <div
                style={{
                  padding: "16px",
                  background: "rgba(0, 229, 255, 0.04)",
                  border: "1px solid rgba(0, 229, 255, 0.12)",
                  borderRadius: "var(--radius-md)",
                }}
              >
                <p style={{ fontSize: "0.82rem", color: "var(--text-secondary)", lineHeight: 1.55 }}>
                  Profilinizin geri kalan detaylarını (ilişki/evlilik hedefleri, ofis/ev tercihleri vb.) kayıt olduktan sonra Dashboard veya Ayarlar üzerinden dilerken doldurabilirsiniz.
                </p>
              </div>
            </div>
          )}

          {/* Navigasyon Tuşları */}
          <div
            style={{
              display: "flex",
              gap: "12px",
              marginTop: "40px",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            {step > 1 ? (
              <button className="btn-ghost" id="btn-prev" type="button" onClick={() => setStep(step - 1)}>
                Geri
              </button>
            ) : (
              <Link href="/login">
                <button className="btn-ghost" id="btn-back-login" type="button">Girişe Dön</button>
              </Link>
            )}

            {step < STEPS.length ? (
              <button
                className="btn-primary"
                id="btn-next"
                type="button"
                onClick={() => {
                  if (step === 1 && !status) {
                    alert("Lütfen durumunuzu seçin.");
                    return;
                  }
                  if (step === 2 && !field) {
                    alert("Lütfen bir alan seçin.");
                    return;
                  }
                  setStep(step + 1);
                }}
              >
                Devam Et
              </button>
            ) : (
              <button
                className="btn-primary"
                id="btn-finish"
                type="button"
                onClick={handleFinish}
              >
                Simülasyonu Başlat
              </button>
            )}
          </div>

        </div>

      </div>
    </div>
  );
}

// ── Yardımcı Stiller ──────────────────────────────────────────────────────────

function choiceStyle(selected: boolean): React.CSSProperties {
  return {
    display: "flex",
    alignItems: "center",
    gap: "12px",
    padding: "13px 16px",
    background: selected ? "rgba(0, 229, 255, 0.07)" : "var(--glass-bg)",
    border: `1px solid ${selected ? "var(--accent-cyan)" : "var(--glass-border)"}`,
    borderRadius: "var(--radius-md)",
    color: selected ? "var(--accent-cyan)" : "var(--text-primary)",
    cursor: "pointer",
    textAlign: "left",
    fontFamily: "'Inter', sans-serif",
    fontWeight: selected ? 600 : 400,
    fontSize: "0.9rem",
    transition: "all 0.2s ease",
    width: "100%",
  };
}

function radioCircle(selected: boolean): React.CSSProperties {
  return {
    width: "16px",
    height: "16px",
    borderRadius: "50%",
    border: `2px solid ${selected ? "var(--accent-cyan)" : "rgba(255,255,255,0.2)"}`,
    background: selected ? "var(--accent-cyan)" : "transparent",
    flexShrink: 0,
    transition: "all 0.2s ease",
    boxShadow: selected ? "0 0 8px rgba(0,229,255,0.5)" : "none",
  };
}

const labelStyle: React.CSSProperties = {
  fontSize: "0.85rem",
  color: "var(--text-secondary)",
  marginBottom: "10px",
  display: "block",
  fontWeight: 500,
};

const inputStyle: React.CSSProperties = {
  width: "100%",
  padding: "12px 16px",
  background: "rgba(255,255,255,0.04)",
  border: "1px solid var(--glass-border)",
  borderRadius: "var(--radius-md)",
  color: "var(--text-primary)",
  fontSize: "0.9rem",
  outline: "none",
  fontFamily: "'Inter', sans-serif",
};
