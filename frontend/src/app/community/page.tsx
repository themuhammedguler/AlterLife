import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Topluluk – AlterLife",
  description: "Benzer kararları veren kullanıcıların anonim deneyimleri ve istatistikleri.",
};

const COMMUNITY_STORIES = [
  {
    id: "comm_001",
    category: "Almanya Tasinma",
    title: "Senior Cloud Engineer – Berlin'e Tasindim",
    journey: "2 yil",
    salary: "€72.000 / yil",
    tips: ["AWS + German B1 kilit", "LinkedIn Job Alerts kur", "Relocation paketi pazarlik et"],
    pitfalls: ["Anmeldung randevusunu ertelemek", "Almanca olmadan sosyal izolasyon"],
    upvotes: 47,
  },
  {
    id: "comm_002",
    category: "Remote Kariyer",
    title: "Turkiye'den Remote Full-Stack Developer",
    journey: "8 ay",
    salary: "$4.200 / ay",
    tips: ["Toptal/Turing platformlari dene", "Portfolio > CV", "USD bazli sozlesme sart"],
    pitfalls: ["Vergi planlamasi onemli", "Timezone yonetimi"],
    upvotes: 38,
  },
  {
    id: "comm_003",
    category: "Startup",
    title: "B2B SaaS Kurucusu – 6. Ayda Ilk Gelir",
    journey: "6 ay",
    salary: "Degisken",
    tips: ["Validate before build", "Ilk 10 musteriyi tani", "Co-founder bulunca basla"],
    pitfalls: ["Runway hesaplama eksikligi", "Urun-pazar uyumsuzlugu"],
    upvotes: 29,
  },
];

export default function CommunityPage() {
  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">
          <span className="text-gradient">Topluluk Bilgi Bankasi</span>
        </h1>
        <p className="page-subtitle">
          Benzer kararlari veren kullanicilarin anonim deneyimleri ve basari yollari
        </p>
      </div>

      {/* Stats */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "16px", marginBottom: "32px" }}>
        {[
          { label: "Anonim Hikaye", value: "1.2K+", desc: "Toplam Paylasim" },
          { label: "Kariyer Yolu", value: "48", desc: "Farkli Senaryo" },
          { label: "Ortalama Sure", value: "18 ay", desc: "Hedefe Ulasim" },
        ].map((s) => (
          <div key={s.label} className="glass-card" style={{ padding: "20px", display: "flex", flexDirection: "column", gap: "6px" }}>
            <div style={{ fontFamily: "'Outfit', sans-serif", fontSize: "1.6rem", fontWeight: 800, color: "var(--accent-cyan)" }}>
              {s.value}
            </div>
            <div>
              <div style={{ fontSize: "0.85rem", fontWeight: 600, color: "var(--text-primary)" }}>{s.label}</div>
              <div style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>{s.desc}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Stories */}
      <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
        {COMMUNITY_STORIES.map((story) => (
          <div key={story.id} id={`story-${story.id}`} className="glass-card glass-card-hover" style={{ padding: "28px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start", marginBottom: "16px" }}>
              <div>
                <span className="badge badge-violet" style={{ marginBottom: "10px", display: "inline-block" }}>
                  {story.category}
                </span>
                <h2 style={{ fontFamily: "'Outfit', sans-serif", fontWeight: 700, fontSize: "1.05rem" }}>
                  {story.title}
                </h2>
              </div>
              <div style={{ textAlign: "right" }}>
                <div style={{ color: "var(--accent-green)", fontWeight: 700, fontFamily: "'Outfit', sans-serif" }}>
                  {story.salary}
                </div>
                <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>{story.journey} icinde</div>
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
              <div>
                <p style={{ fontSize: "0.8rem", color: "var(--accent-green)", fontWeight: 600, marginBottom: "8px" }}>
                  Kilit Adimlar
                </p>
                {story.tips.map((tip) => (
                  <p key={tip} style={{ fontSize: "0.82rem", color: "var(--text-secondary)", marginBottom: "4px" }}>
                    • {tip}
                  </p>
                ))}
              </div>
              <div>
                <p style={{ fontSize: "0.8rem", color: "var(--accent-pink)", fontWeight: 600, marginBottom: "8px" }}>
                  Dikkat Edilecekler
                </p>
                {story.pitfalls.map((p) => (
                  <p key={p} style={{ fontSize: "0.82rem", color: "var(--text-secondary)", marginBottom: "4px" }}>
                    • {p}
                  </p>
                ))}
              </div>
            </div>

            <div style={{ marginTop: "16px", display: "flex", alignItems: "center", gap: "8px" }}>
              <button
                id={`upvote-${story.id}`}
                style={{
                  padding: "6px 14px",
                  background: "rgba(16,185,129,0.08)",
                  border: "1px solid rgba(16,185,129,0.2)",
                  borderRadius: "999px",
                  color: "var(--accent-green)",
                  cursor: "pointer",
                  fontSize: "0.8rem",
                  fontFamily: "'Inter', sans-serif",
                }}
              >
                Destekle ({story.upvotes})
              </button>
              <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Faydali buldu</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
