"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface OnboardingData {
  status: string;
  age: string;
  city: string;
  field: string;
  workPrefs: string[];
  freeGoal: string;
}

const FIELD_LABELS: Record<string, string> = {
  software: "Yazılım / Teknoloji",
  design: "Tasarım / Sanat",
  finance: "Finans / İş Dünyası",
  health: "Sağlık / Tıp",
  engineering: "Mühendislik",
  startup: "Girişimcilik / Kendi işim",
  unknown: "Belirsiz / Keşif Aşaması",
};

export default function DashboardPage() {
  const [profile, setProfile] = useState<OnboardingData | null>(null);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const data = localStorage.getItem("alterlife_onboarding");
      if (data) {
        try {
          setProfile(JSON.parse(data));
        } catch (e) {
          console.error("Onboarding verisi yuklenemedi", e);
        }
      }
    }
  }, []);

  // Varsayılan / Dinamik Hedef Tanımı
  const activeGoal = profile?.freeGoal || (
    profile?.field === "software"
      ? "2 yıl içinde yurt dışında Senior Geliştirici olmak"
      : profile?.field === "design"
      ? "Uluslararası tasarım portfolyosu oluşturup freelance çalışmak"
      : profile?.field === "startup"
      ? "Kendi SaaS girişimimi kurup ilk gelirimi elde etmek"
      : "Kariyer hedeflerimi netleştirip yeni yetenekler kazanmak"
  );

  // Önerilen Dallanmalar (Emerging paths)
  const getEmergingPaths = () => {
    if (!profile) {
      return [
        { title: "Kariyer Yönü Belirleme", type: "Keşif", difficulty: "Kolay" },
        { title: "Temel Yetenek Analizi", type: "Eğitim", difficulty: "Orta" },
      ];
    }
    const paths = [];
    if (profile.field === "software") {
      paths.push({ title: "Yurt Dışı İş Başvuruları", type: "Kariyer", difficulty: "Zor" });
      paths.push({ title: "Cloud & DevOps Eğitimi", type: "Teknik", difficulty: "Orta" });
    } else if (profile.field === "design") {
      paths.push({ title: "Behance & Dribbble Portfolyo Yapımı", type: "Portfolyo", difficulty: "Orta" });
      paths.push({ title: "Freelance Müşteri Edinme", type: "İş Dünyası", difficulty: "Kolay" });
    } else if (profile.field === "startup") {
      paths.push({ title: "No-Code ile Hızlı MVP Üretimi", type: "Girişim", difficulty: "Orta" });
      paths.push({ title: "Kurucu Ortak (Co-Founder) Arama", type: "Ağ Kurma", difficulty: "Zor" });
    } else {
      paths.push({ title: "Sektörel Keşif ve Araştırma", type: "Analiz", difficulty: "Kolay" });
    }

    if (profile.workPrefs.includes("abroad") || profile.workPrefs.includes("remote")) {
      paths.push({ title: "Profesyonel İngilizce / Almanca Hazırlığı", type: "Dil", difficulty: "Orta" });
    }
    return paths;
  };

  const dailyQuests = [
    {
      id: "qst_001",
      title: profile?.field === "software" ? "AWS VPC Modülünü Çalış" : "Sektörel Eğitim Videosu İzle",
      xp: 150,
      done: false,
    },
    {
      id: "qst_002",
      title: profile?.field === "software" ? "Docker ile test ortamı oluştur" : "Günlük Planlama Yap",
      xp: 200,
      done: true,
    },
    {
      id: "qst_003",
      title: "Yabancı dil çalışması - 15 dakika",
      xp: 100,
      done: false,
    },
  ];

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">
          <span className="text-gradient">Dashboard</span>
        </h1>
        <p className="page-subtitle">Karakterinizin güncel durumu ve önerilen hedefleri</p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "300px 1fr", gap: "24px" }}>

        {/* Left Card: Profile & Stats */}
        <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
          <div
            className="glass-card"
            style={{
              padding: "28px",
              background: "linear-gradient(135deg, rgba(124,58,237,0.12), rgba(79,70,229,0.08))",
              textAlign: "center",
            }}
          >
            {/* Avatar */}
            <div
              style={{
                width: "88px",
                height: "88px",
                borderRadius: "50%",
                background: "var(--gradient-cyan-violet)",
                margin: "0 auto 16px",
                boxShadow: "var(--shadow-glow-violet)",
                border: "3px solid rgba(0, 229, 255, 0.25)",
              }}
            />

            <h2 style={{ fontFamily: "'Outfit', sans-serif", fontWeight: 700, fontSize: "1.15rem", marginBottom: "4px" }}>
              Sedef K.
            </h2>
            <span className="badge badge-cyan" style={{ marginBottom: "16px", display: "inline-block" }}>
              {profile ? FIELD_LABELS[profile.field] || "Kaşif" : "Novice Seeker"}
            </span>

            {/* Age & City */}
            <p style={{ fontSize: "0.8rem", color: "var(--text-secondary)", marginBottom: "16px" }}>
              Yaş: {profile?.age || "Belirtilmedi"} | Konum: {profile?.city || "Belirtilmedi"}
            </p>

            {/* Stat grid */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "10px", marginBottom: "20px" }}>
              {[
                { label: "Seviye", value: "1" },
                { label: "XP", value: "200" },
                { label: "Görev", value: "1/3" },
              ].map((s) => (
                <div key={s.label} style={{ background: "var(--glass-bg)", borderRadius: "var(--radius-sm)", padding: "10px 6px" }}>
                  <div style={{ fontSize: "1.1rem", fontWeight: 700, fontFamily: "'Outfit', sans-serif", color: "var(--accent-cyan)" }}>
                    {s.value}
                  </div>
                  <div style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>{s.label}</div>
                </div>
              ))}
            </div>

            <div style={{ marginBottom: "8px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.73rem", color: "var(--text-muted)", marginBottom: "6px" }}>
                <span>200 XP</span>
                <span>1000 XP</span>
              </div>
              <div className="xp-bar">
                <div className="xp-bar-fill" style={{ width: "20%" }} />
              </div>
            </div>
            <p style={{ fontSize: "0.73rem", color: "var(--text-muted)" }}>800 XP daha — Seviye 2</p>
          </div>

          {/* Integrations */}
          <div className="glass-card" style={{ padding: "20px" }}>
            <h3 style={{ fontSize: "0.88rem", fontWeight: 600, marginBottom: "14px", color: "var(--text-secondary)" }}>
              Entegrasyonlar
            </h3>
            {[
              { name: "Google Calendar", connected: false },
              { name: "GitHub", connected: false },
            ].map((int) => (
              <div
                key={int.name}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "12px",
                  background: "var(--glass-bg)",
                  borderRadius: "var(--radius-sm)",
                  marginBottom: "8px",
                  border: "1px solid var(--glass-border)",
                }}
              >
                <span style={{ fontSize: "0.85rem", fontWeight: 500 }}>{int.name}</span>
                <Link href="/settings">
                  <button
                    style={{
                      padding: "4px 10px",
                      background: "rgba(0, 229, 255, 0.08)",
                      border: "1px solid rgba(0, 229, 255, 0.2)",
                      borderRadius: "999px",
                      color: "var(--accent-cyan)",
                      fontSize: "0.75rem",
                      cursor: "pointer",
                      fontFamily: "'Inter', sans-serif",
                    }}
                  >
                    Bağla
                  </button>
                </Link>
              </div>
            ))}
          </div>
        </div>

        {/* Right Content */}
        <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>

          {/* Active Simulation */}
          <div className="glass-card" style={{ padding: "28px" }}>
            <h2 style={{ fontFamily: "'Outfit', sans-serif", fontWeight: 700, fontSize: "1.05rem", marginBottom: "8px" }}>
              Aktif Hedef ve Simülasyon
            </h2>
            <p style={{ color: "var(--text-primary)", fontSize: "0.95rem", fontWeight: 500, marginBottom: "20px", lineHeight: 1.55 }}>
              &ldquo;{activeGoal}&rdquo;
            </p>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "12px", marginBottom: "20px" }}>
              {[
                { label: "Stres Seviyesi", value: "30%", color: "var(--accent-green)" },
                { label: "Mutluluk Oranı", value: "70%", color: "var(--accent-cyan)" },
                { label: "Kariyer Skoru", value: "20%", color: "var(--accent-violet)" },
              ].map((m) => (
                <div key={m.label} style={{ background: "var(--glass-bg)", borderRadius: "var(--radius-md)", padding: "14px", textAlign: "center" }}>
                  <div style={{ fontSize: "1.3rem", fontWeight: 700, color: m.color, fontFamily: "'Outfit', sans-serif" }}>
                    {m.value}
                  </div>
                  <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "2px" }}>{m.label}</div>
                </div>
              ))}
            </div>
            <Link href="/simulations">
              <button className="btn-primary" id="btn-view-simulations">
                Simülasyona Git
              </button>
            </Link>
          </div>

          {/* Emerging paths based on AI Analysis */}
          <div className="glass-card" style={{ padding: "28px" }}>
            <h2 style={{ fontFamily: "'Outfit', sans-serif", fontWeight: 700, fontSize: "1.05rem", marginBottom: "16px" }}>
              Hedefinizden Oluşabilecek Gelecek Dalları
            </h2>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
              {getEmergingPaths().map((p, idx) => (
                <div
                  key={idx}
                  style={{
                    padding: "16px",
                    background: "rgba(255,255,255,0.03)",
                    border: "1px solid var(--glass-border)",
                    borderRadius: "var(--radius-md)",
                    display: "flex",
                    flexDirection: "column",
                    justifyContent: "space-between",
                  }}
                >
                  <div>
                    <span className="badge badge-violet" style={{ fontSize: "0.68rem", marginBottom: "8px" }}>
                      {p.type}
                    </span>
                    <h3 style={{ fontSize: "0.9rem", fontWeight: 600, color: "var(--text-primary)", marginBottom: "4px" }}>
                      {p.title}
                    </h3>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "12px" }}>
                    <span style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>Zorluk: {p.difficulty}</span>
                    <Link href="/simulations" style={{ fontSize: "0.75rem", color: "var(--accent-cyan)", textDecoration: "none", fontWeight: 600 }}>
                      Simüle Et →
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Daily Quests */}
          <div className="glass-card" style={{ padding: "28px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
              <h2 style={{ fontFamily: "'Outfit', sans-serif", fontWeight: 700, fontSize: "1.05rem" }}>
                Günlük Görevler
              </h2>
              <span className="badge badge-cyan">3 Görev</span>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              {dailyQuests.map((quest) => (
                <div
                  key={quest.id}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "14px",
                    padding: "14px 16px",
                    background: quest.done ? "rgba(16, 185, 129, 0.05)" : "var(--glass-bg)",
                    border: `1px solid ${quest.done ? "rgba(16, 185, 129, 0.18)" : "var(--glass-border)"}`,
                    borderRadius: "var(--radius-md)",
                  }}
                >
                  <div style={{ flex: 1 }}>
                    <p style={{
                      fontWeight: 500,
                      fontSize: "0.9rem",
                      textDecoration: quest.done ? "line-through" : "none",
                      color: quest.done ? "var(--text-muted)" : "var(--text-primary)",
                    }}>
                      {quest.title}
                    </p>
                  </div>
                  <span className={`badge ${quest.done ? "badge-green" : "badge-violet"}`} style={{ whiteSpace: "nowrap" }}>
                    +{quest.xp} XP
                  </span>
                </div>
              ))}
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
