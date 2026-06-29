import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Analitik – AlterLife",
  description: "Ilerleme analitigin, aktivite isi haritasi ve kariyer metriklerin.",
};

const WEEKS = ["Pzt", "Sal", "Car", "Per", "Cum", "Cmt", "Paz"];
const HEAT_MAP_DATA = [
  [2, 4, 1, 3, 5, 0, 0],
  [3, 2, 4, 1, 2, 1, 0],
  [1, 5, 2, 4, 3, 2, 1],
  [4, 1, 3, 5, 2, 0, 0],
];

function getHeatColor(val: number) {
  if (val === 0) return "rgba(255,255,255,0.04)";
  const opacity = 0.15 + (val / 5) * 0.7;
  return `rgba(0, 229, 255, ${opacity})`;
}

export default function AnalyticsPage() {
  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">
          <span className="text-gradient">Ilerleme Analitigi</span>
        </h1>
        <p className="page-subtitle">Aktivitelerini, kararlarini ve hedef uyumunu izle</p>
      </div>

      {/* KPI Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "16px", marginBottom: "32px" }}>
        {[
          { label: "Toplam XP",          value: "200",  delta: "+200 bu hafta",  color: "var(--accent-cyan)" },
          { label: "Tamamlanan Gorev",   value: "12",   delta: "+3 bu hafta",    color: "var(--accent-green)" },
          { label: "Aktif Gun",           value: "7",    delta: "Son 30 gun",     color: "var(--accent-violet)" },
          { label: "Hedef Uyumu",         value: "68%",  delta: "+5% bu hafta",  color: "var(--accent-amber)" },
        ].map((kpi) => (
          <div key={kpi.label} className="glass-card" style={{ padding: "22px" }}>
            <div style={{ fontFamily: "'Outfit', sans-serif", fontSize: "1.9rem", fontWeight: 800, color: kpi.color }}>
              {kpi.value}
            </div>
            <div style={{ fontSize: "0.8rem", color: "var(--text-secondary)", marginTop: "4px" }}>{kpi.label}</div>
            <div style={{ fontSize: "0.75rem", color: "var(--accent-green)", marginTop: "4px" }}>{kpi.delta}</div>
          </div>
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px" }}>

        {/* Activity Heatmap */}
        <div className="glass-card" style={{ padding: "28px" }}>
          <h2 style={{ fontFamily: "'Outfit', sans-serif", fontSize: "1rem", fontWeight: 600, marginBottom: "20px" }}>
            Aktivite Isi Haritasi (Son 4 Hafta)
          </h2>
          <div style={{ display: "flex", gap: "4px", marginBottom: "8px" }}>
            {WEEKS.map((d) => (
              <div key={d} style={{ flex: 1, textAlign: "center", fontSize: "0.7rem", color: "var(--text-muted)" }}>{d}</div>
            ))}
          </div>
          {HEAT_MAP_DATA.map((week, wi) => (
            <div key={wi} style={{ display: "flex", gap: "4px", marginBottom: "4px" }}>
              {week.map((val, di) => (
                <div
                  key={di}
                  title={`${val} gorev`}
                  style={{
                    flex: 1,
                    aspectRatio: "1",
                    background: getHeatColor(val),
                    borderRadius: "3px",
                    border: "1px solid rgba(255,255,255,0.04)",
                    cursor: "pointer",
                  }}
                />
              ))}
            </div>
          ))}
          <div style={{ display: "flex", gap: "6px", alignItems: "center", marginTop: "14px", justifyContent: "flex-end" }}>
            <span style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>Az</span>
            {[0, 1, 2, 4, 5].map((v) => (
              <div key={v} style={{ width: "12px", height: "12px", background: getHeatColor(v), borderRadius: "2px" }} />
            ))}
            <span style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>Cok</span>
          </div>
        </div>

        {/* Decision Impact Chart placeholder */}
        <div className="glass-card" style={{ padding: "28px" }}>
          <h2 style={{ fontFamily: "'Outfit', sans-serif", fontSize: "1rem", fontWeight: 600, marginBottom: "10px" }}>
            Karar Etki Analizi
          </h2>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem", marginBottom: "20px" }}>
            Kararlarinin hedeflere ulaşma yüzdeni nasil etkilediği
          </p>
          <div
            style={{
              height: "200px",
              background: "var(--glass-bg)",
              borderRadius: "var(--radius-md)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              border: "1px dashed var(--glass-border)",
              flexDirection: "column",
              gap: "8px",
            }}
          >
            <div
              style={{
                width: "40px",
                height: "40px",
                borderRadius: "var(--radius-sm)",
                background: "rgba(124,58,237,0.15)",
                border: "1px solid rgba(124,58,237,0.3)",
              }}
            />
            <p style={{ color: "var(--text-muted)", fontSize: "0.83rem", textAlign: "center" }}>
              Recharts grafikler<br />Hafta 5&apos;te eklenecek
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
