"use client";

import { useEffect, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  LineChart, Line, CartesianGrid, ReferenceLine, RadarChart, Radar, PolarGrid, PolarAngleAxis
} from "recharts";
import { getAnalyticsSummary } from "@/lib/api";

type KPI = {
  total_xp: number;
  level: number;
  completed_quests: number;
  active_days: number;
  goal_alignment: number;
  simulation_branches: number;
  library_resources_completed: number;
};

type XPDataPoint = { label: string; xp: number };

type DecisionImpact = {
  branch_id: string;
  decision_name: string;
  happiness_delta: number;
  savings_delta: number;
  stress_delta: number;
  career_score: number;
};

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: "rgba(10,10,20,0.9)", border: "1px solid rgba(0,229,255,0.2)",
      borderRadius: "10px", padding: "10px 14px", backdropFilter: "blur(12px)",
    }}>
      <p style={{ color: "var(--text-muted)", fontSize: "0.75rem", marginBottom: "4px" }}>{label}</p>
      {payload.map((p: any) => (
        <p key={p.name} style={{ color: p.color || "var(--accent-cyan)", fontWeight: 700, fontSize: "0.9rem" }}>
          {p.value} XP
        </p>
      ))}
    </div>
  );
};

export default function AnalyticsPage() {
  const [kpi, setKpi] = useState<KPI | null>(null);
  const [xpHistory, setXpHistory] = useState<XPDataPoint[]>([]);
  const [decisionImpacts, setDecisionImpacts] = useState<DecisionImpact[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAnalyticsSummary()
      .then((data) => {
        setKpi(data.kpi);
        setXpHistory(data.xp_history || []);
        setDecisionImpacts(data.decision_impacts || []);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const radarData = decisionImpacts.slice(0, 3).map((d) => ({
    name: d.decision_name.slice(0, 20),
    Mutluluk: Math.max(0, 50 + d.happiness_delta),
    Tasarruf: Math.max(0, 50 + d.savings_delta / 1000),
    Kariyer: d.career_score,
  }));

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">
          <span className="text-gradient">İlerleme Analitiği</span>
        </h1>
        <p className="page-subtitle">Aktivitelerini, kararlarını ve hedef uyumunu izle</p>
      </div>

      {loading ? (
        <div style={{ textAlign: "center", padding: "60px", color: "var(--text-muted)" }}>
          <div style={{ fontSize: "2rem", marginBottom: "12px" }}>📊</div>
          <p>Analitikler yükleniyor...</p>
        </div>
      ) : (
        <>
          {/* KPI Cards */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "16px", marginBottom: "32px" }}>
            {[
              { label: "Toplam XP", value: (kpi?.total_xp ?? 0).toLocaleString(), delta: `Seviye ${kpi?.level ?? 1}`, color: "var(--accent-cyan)" },
              { label: "Tamamlanan Görev", value: String(kpi?.completed_quests ?? 0), delta: "Bugün", color: "var(--accent-green)" },
              { label: "Aktif Gün", value: String(kpi?.active_days ?? 0), delta: "Son 30 gün", color: "var(--accent-violet)" },
              { label: "Hedef Uyumu", value: `${kpi?.goal_alignment ?? 0}%`, delta: `${kpi?.simulation_branches ?? 0} dal`, color: "var(--accent-amber)" },
            ].map((kpiItem) => (
              <div key={kpiItem.label} className="glass-card" style={{ padding: "22px" }}>
                <div style={{ fontFamily: "'Outfit', sans-serif", fontSize: "1.9rem", fontWeight: 800, color: kpiItem.color }}>
                  {kpiItem.value}
                </div>
                <div style={{ fontSize: "0.8rem", color: "var(--text-secondary)", marginTop: "4px" }}>{kpiItem.label}</div>
                <div style={{ fontSize: "0.75rem", color: kpiItem.color, marginTop: "4px", opacity: 0.8 }}>{kpiItem.delta}</div>
              </div>
            ))}
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px", marginBottom: "24px" }}>
            {/* XP Bar Chart */}
            <div className="glass-card" style={{ padding: "28px" }}>
              <h2 style={{ fontFamily: "'Outfit', sans-serif", fontSize: "1rem", fontWeight: 600, marginBottom: "20px" }}>
                Haftalık XP Kazanımı
              </h2>
              {xpHistory.length > 0 ? (
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={xpHistory} margin={{ top: 4, right: 8, bottom: 4, left: -20 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                    <XAxis dataKey="label" tick={{ fill: "var(--text-muted)", fontSize: 11 }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fill: "var(--text-muted)", fontSize: 11 }} axisLine={false} tickLine={false} />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar dataKey="xp" fill="url(#xpGrad)" radius={[6, 6, 0, 0]} />
                    <defs>
                      <linearGradient id="xpGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#00e5ff" stopOpacity={0.9} />
                        <stop offset="100%" stopColor="#7c3aed" stopOpacity={0.6} />
                      </linearGradient>
                    </defs>
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div style={{ height: "200px", display: "flex", alignItems: "center", justifyContent: "center", color: "var(--text-muted)", fontSize: "0.85rem" }}>
                  Henüz yeterli veri yok.
                </div>
              )}
            </div>

            {/* Activity Heatmap */}
            <div className="glass-card" style={{ padding: "28px" }}>
              <h2 style={{ fontFamily: "'Outfit', sans-serif", fontSize: "1rem", fontWeight: 600, marginBottom: "8px" }}>
                Özet Pano
              </h2>
              <p style={{ color: "var(--text-muted)", fontSize: "0.8rem", marginBottom: "20px" }}>Kişisel gelişim metriklerin</p>
              <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
                {[
                  { label: "Hedef Uyumu", value: kpi?.goal_alignment ?? 0, color: "var(--accent-amber)" },
                  { label: "Quest Tamamlama", value: kpi ? Math.round((kpi.completed_quests / 3) * 100) : 0, color: "var(--accent-green)" },
                  { label: "Kütüphane İlerlemesi", value: kpi ? Math.round((kpi.library_resources_completed / Math.max(1, kpi.library_resources_completed + 2)) * 100) : 0, color: "var(--accent-violet)" },
                  { label: "Simülasyon Aktifliği", value: Math.min(100, (kpi?.simulation_branches ?? 0) * 25), color: "var(--accent-cyan)" },
                ].map((bar) => (
                  <div key={bar.label}>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "5px" }}>
                      <span style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>{bar.label}</span>
                      <span style={{ fontSize: "0.8rem", color: bar.color, fontWeight: 600 }}>{bar.value}%</span>
                    </div>
                    <div style={{ height: "6px", background: "rgba(255,255,255,0.06)", borderRadius: "999px", overflow: "hidden" }}>
                      <div style={{
                        height: "100%", width: `${bar.value}%`, background: bar.color,
                        borderRadius: "999px", boxShadow: `0 0 8px ${bar.color}50`,
                        transition: "width 1s ease",
                      }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Decision Impact */}
          <div className="glass-card" style={{ padding: "28px" }}>
            <h2 style={{ fontFamily: "'Outfit', sans-serif", fontSize: "1rem", fontWeight: 600, marginBottom: "8px" }}>
              Karar Etki Analizi
            </h2>
            <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem", marginBottom: "24px" }}>
              Simülasyon dallarının metriklere etkisi
            </p>
            {decisionImpacts.length === 0 ? (
              <div style={{ textAlign: "center", padding: "40px", color: "var(--text-muted)" }}>
                <div style={{ fontSize: "1.8rem", marginBottom: "8px" }}>🌿</div>
                <p>Henüz dal oluşturulmadı. Simülasyon sayfasından "What If" deneyin!</p>
              </div>
            ) : (
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "16px" }}>
                {decisionImpacts.map((d) => (
                  <div key={d.branch_id} className="glass-card" style={{ padding: "20px" }}>
                    <h3 style={{ fontFamily: "'Outfit', sans-serif", fontWeight: 600, fontSize: "0.9rem", marginBottom: "12px" }}>
                      {d.decision_name}
                    </h3>
                    <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                      {[
                        { label: "Mutluluk", value: d.happiness_delta, suffix: "%", positive: d.happiness_delta >= 0 },
                        { label: "Tasarruf", value: d.savings_delta, suffix: "$", positive: d.savings_delta >= 0 },
                        { label: "Stres", value: d.stress_delta, suffix: "%", positive: d.stress_delta <= 0 },
                        { label: "Kariyer Skoru", value: d.career_score, suffix: "", positive: d.career_score >= 50 },
                      ].map((m) => (
                        <div key={m.label} style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                          <span style={{ fontSize: "0.78rem", color: "var(--text-muted)" }}>{m.label}</span>
                          <span style={{ fontSize: "0.85rem", fontWeight: 600, color: m.positive ? "var(--accent-green)" : "var(--accent-pink)" }}>
                            {m.value > 0 ? "+" : ""}{m.value}{m.suffix}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
