"use client";

import { useEffect, useState } from "react";
import {
  addDecisionJournal,
  createWeeklyReview,
  exportCoachReport,
  getActiveGoal,
  getDecisionJournal,
  getMilestoneTimeline,
  getRealityCheck,
  getRiskRadar,
  mentorChat,
} from "@/lib/api";

export default function CoachPage() {
  const [activeGoal, setActiveGoal] = useState<any>(null);
  const [radar, setRadar] = useState<any>(null);
  const [timeline, setTimeline] = useState<any>(null);
  const [reality, setReality] = useState<any>(null);
  const [journal, setJournal] = useState<any[]>([]);
  const [mentorMessage, setMentorMessage] = useState("Bugün çok yorgunum, hedefim için en küçük doğru hamle ne?");
  const [mentorAnswer, setMentorAnswer] = useState<any>(null);
  const [decision, setDecision] = useState("");
  const [expectation, setExpectation] = useState("");
  const [reviewResult, setReviewResult] = useState<any>(null);

  const load = async () => {
    const [goalData, radarData, timelineData, realityData, journalData] = await Promise.all([
      getActiveGoal(),
      getRiskRadar(),
      getMilestoneTimeline(),
      getRealityCheck(),
      getDecisionJournal(),
    ]);
    setActiveGoal(goalData);
    setRadar(radarData);
    setTimeline(timelineData);
    setReality(realityData);
    setJournal(journalData.entries || []);
  };

  useEffect(() => {
    load().catch(console.error);
  }, []);

  const askMentor = async () => {
    const data = await mentorChat(mentorMessage, "playful");
    setMentorAnswer(data);
  };

  const saveDecision = async () => {
    if (!decision.trim() || !expectation.trim()) return;
    await addDecisionJournal({ decision, expectation, confidence: 65, revisit_in_days: 30 });
    setDecision("");
    setExpectation("");
    const data = await getDecisionJournal();
    setJournal(data.entries || []);
  };

  const runWeeklyReview = async () => {
    const data = await createWeeklyReview({
      wins: ["Bir hedef dalı netleşti", "Günlük quest ritmi kuruldu"],
      blockers: ["Zaman ve enerji dalgalanması"],
      energy_score: 72,
      next_week_focus: "Tek ana çıktıyı bitir ve risk radarını düşür.",
    });
    setReviewResult(data);
  };

  const downloadReport = async () => {
    const report = await exportCoachReport();
    const blob = new Blob([report.markdown], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = report.filename || "alterlife-report.md";
    anchor.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="page-container" style={{ maxWidth: "1180px", padding: "40px 24px" }}>
      <div className="page-header" style={{ marginBottom: "28px" }}>
        <h1 className="page-title" style={{ fontSize: "2rem", fontWeight: 800 }}>
          <span className="text-gradient">Coach Center</span>
        </h1>
        <p className="page-subtitle" style={{ color: "var(--text-secondary)", fontSize: "0.95rem" }}>
          Aktif hedef, risk radar, mentor, haftalık review ve karar günlüğü tek merkezde.
        </p>
        <button className="btn-primary" onClick={downloadReport} style={{ marginTop: "14px" }}>
          Raporu İndir
        </button>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1.1fr 0.9fr", gap: "20px" }}>
        <section className="glass-card" style={{ padding: "24px" }}>
          <h2 style={titleStyle}>Aktif Hedef</h2>
          <h3 style={{ fontSize: "1.15rem", marginBottom: "8px" }}>{activeGoal?.title || "Yükleniyor..."}</h3>
          <p style={mutedText}>{activeGoal?.description || "Simülasyon sayfasından bir dal seçerek ana hedefi sabitle."}</p>
          {reality && (
            <div style={panelStyle}>
              <strong>Reality Check</strong>
              <p style={mutedText}>{reality.verdict}</p>
              <small style={{ color: "var(--accent-amber)" }}>{reality.minimum_weekly_commitment}</small>
            </div>
          )}
        </section>

        <section className="glass-card" style={{ padding: "24px" }}>
          <h2 style={titleStyle}>Haftalık Review</h2>
          <p style={mutedText}>Haftayı kapat, ritmi ayarla, gelecek haftanın tek ana odağını seç.</p>
          <button className="btn-primary" onClick={runWeeklyReview} style={{ marginTop: "12px" }}>
            Review Oluştur
          </button>
          {reviewResult && (
            <div style={panelStyle}>
              <strong>{reviewResult.summary}</strong>
              <p style={mutedText}>{reviewResult.recommended_adjustment}</p>
            </div>
          )}
        </section>

        <section className="glass-card" style={{ padding: "24px" }}>
          <h2 style={titleStyle}>Risk Radar</h2>
          <p style={mutedText}>Genel risk: %{radar?.overall_risk ?? 0}</p>
          <div style={{ display: "grid", gap: "10px", marginTop: "14px" }}>
            {(radar?.risks || []).map((risk: any) => (
              <div key={risk.name} style={panelStyle}>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <strong>{risk.name}</strong>
                  <span style={{ color: risk.score > 65 ? "var(--accent-pink)" : "var(--accent-green)" }}>%{risk.score}</span>
                </div>
                <p style={mutedText}>{risk.signal}</p>
                <small style={{ color: "var(--accent-cyan)" }}>{risk.preventive_quest}</small>
              </div>
            ))}
          </div>
        </section>

        <section className="glass-card" style={{ padding: "24px" }}>
          <h2 style={titleStyle}>AI Mentor Chat</h2>
          <textarea value={mentorMessage} onChange={(event) => setMentorMessage(event.target.value)} style={textareaStyle} />
          <button className="btn-primary" onClick={askMentor} style={{ marginTop: "10px" }}>
            Mentora Sor
          </button>
          {mentorAnswer && (
            <div style={panelStyle}>
              <p style={mutedText}>{mentorAnswer.answer}</p>
              <small style={{ color: "var(--accent-green)" }}>{mentorAnswer.suggested_action}</small>
            </div>
          )}
        </section>

        <section className="glass-card" style={{ padding: "24px" }}>
          <h2 style={titleStyle}>Milestone Timeline</h2>
          <div style={{ display: "grid", gap: "10px" }}>
            {(timeline?.milestones || []).map((item: any) => (
              <div key={item.period} style={panelStyle}>
                <strong>{item.period} · {item.title}</strong>
                <p style={mutedText}>{item.output}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="glass-card" style={{ padding: "24px" }}>
          <h2 style={titleStyle}>Decision Journal</h2>
          <input placeholder="Karar" value={decision} onChange={(event) => setDecision(event.target.value)} style={inputStyle} />
          <textarea placeholder="Ne bekliyorsun?" value={expectation} onChange={(event) => setExpectation(event.target.value)} style={textareaStyle} />
          <button className="btn-primary" onClick={saveDecision} style={{ marginTop: "10px" }}>
            Kararı Kaydet
          </button>
          <div style={{ display: "grid", gap: "8px", marginTop: "14px" }}>
            {journal.slice(-3).map((entry) => (
              <div key={entry.entry_id} style={panelStyle}>
                <strong>{entry.decision}</strong>
                <p style={mutedText}>{entry.expectation}</p>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}

const titleStyle = { color: "var(--accent-cyan)", fontSize: "1rem", fontWeight: 800, marginBottom: "10px" };
const mutedText = { color: "var(--text-secondary)", fontSize: "0.84rem", lineHeight: 1.55 };
const panelStyle = {
  padding: "13px",
  border: "1px solid var(--glass-border)",
  borderRadius: "var(--radius-md)",
  background: "rgba(255,255,255,0.025)",
  marginTop: "10px",
};
const inputStyle = {
  width: "100%",
  padding: "10px 12px",
  background: "rgba(255,255,255,0.04)",
  border: "1px solid var(--glass-border)",
  borderRadius: "var(--radius-md)",
  color: "var(--text-primary)",
  marginBottom: "10px",
};
const textareaStyle = {
  ...inputStyle,
  minHeight: "86px",
  resize: "vertical" as const,
  fontFamily: "'Inter', sans-serif",
};
