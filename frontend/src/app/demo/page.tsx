import Link from "next/link";

const steps = [
  {
    title: "1. Hedefini seç",
    text: "Onboarding ile rolünü, ritmini ve ana hedefini yaz. AlterLife ilk karar ağacını kurar.",
    href: "/onboarding",
  },
  {
    title: "2. Geleceği dallandır",
    text: "Simülasyon sayfasında farklı yolları dene; bir dalı ana hedef yap.",
    href: "/simulations",
  },
  {
    title: "3. Gününü planla",
    text: "Dashboard'da gününün yoğunluğuna göre questleri kısa, gerçekçi ve eğlenceli bloklara böl.",
    href: "/dashboard",
  },
  {
    title: "4. Toplulukla ilerle",
    text: "Benzer rotalara katıl, insanların nerede olduğunu gör, arkadaşına davet kodu gönder.",
    href: "/community",
  },
  {
    title: "5. Coach ile kalibre et",
    text: "Risk radar, weekly review, mentor chat ve karar günlüğüyle hedefini haftadan haftaya ayarla.",
    href: "/coach",
  },
];

export default function DemoPage() {
  return (
    <div className="page-container" style={{ maxWidth: "1040px", padding: "48px 24px" }}>
      <div className="page-header" style={{ marginBottom: "32px" }}>
        <h1 className="page-title" style={{ fontSize: "2.3rem", fontWeight: 900 }}>
          <span className="text-gradient">AlterLife Demo Tour</span>
        </h1>
        <p className="page-subtitle" style={{ color: "var(--text-secondary)", fontSize: "1rem" }}>
          Beş adımda ürün akışı: hedef, simülasyon, günlük quest, topluluk ve koçluk.
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: "16px" }}>
        {steps.map((step) => (
          <Link key={step.title} href={step.href} className="glass-card glass-card-hover" style={{ padding: "22px", textDecoration: "none" }}>
            <h2 style={{ color: "var(--accent-cyan)", fontSize: "1rem", marginBottom: "10px" }}>{step.title}</h2>
            <p style={{ color: "var(--text-secondary)", fontSize: "0.88rem", lineHeight: 1.55 }}>{step.text}</p>
            <span style={{ display: "inline-block", marginTop: "16px", color: "var(--accent-green)", fontSize: "0.82rem", fontWeight: 700 }}>
              Aç →
            </span>
          </Link>
        ))}
      </div>
    </div>
  );
}
