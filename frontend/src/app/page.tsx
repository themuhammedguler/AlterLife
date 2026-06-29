import Link from "next/link";

export default function LandingPage() {
  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "24px",
        textAlign: "center",
        position: "relative",
        zIndex: 1,
      }}
    >
      <div className="animate-fade-up">
        <h1
          className="text-gradient"
          style={{
            fontFamily: "'Outfit', sans-serif",
            fontSize: "clamp(2.8rem, 6vw, 5.5rem)",
            fontWeight: 900,
            lineHeight: 1.1,
            marginBottom: "20px",
            letterSpacing: "-0.02em",
          }}
        >
          AlterLife
        </h1>
        <p
          style={{
            fontSize: "1.25rem",
            color: "var(--text-secondary)",
            maxWidth: "480px",
            marginBottom: "10px",
            lineHeight: 1.65,
            fontWeight: 300,
          }}
        >
          Dijital Ikizinle Geleceğini Sekilllendir
        </p>
        <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", marginBottom: "52px" }}>
          &ldquo;Almanya&apos;ya gidersem ne olur?&rdquo; — AI ile cevapla.
        </p>

        <div style={{ display: "flex", gap: "16px", justifyContent: "center", flexWrap: "wrap" }}>
          <Link href="/login">
            <button className="btn-primary" id="cta-enter-simulation">
              Simülasyona Gir
            </button>
          </Link>
          <Link href="/dashboard">
            <button className="btn-ghost" id="cta-demo">
              Demo
            </button>
          </Link>
        </div>
      </div>

      {/* Feature tags */}
      <div
        style={{
          display: "flex",
          gap: "10px",
          marginTop: "72px",
          flexWrap: "wrap",
          justifyContent: "center",
        }}
      >
        {[
          "What If Simulatoru",
          "RPG Karakter",
          "Yetenek Agaci",
          "Black Swan Testi",
          "Calendar Entegrasyon",
          "GitHub Baglantisi",
        ].map((feat) => (
          <span key={feat} className="badge badge-violet" style={{ fontSize: "0.82rem", padding: "5px 14px" }}>
            {feat}
          </span>
        ))}
      </div>
    </div>
  );
}
