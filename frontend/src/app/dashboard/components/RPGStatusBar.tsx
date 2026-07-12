"use client";

import { useEffect, useRef, useState } from "react";

interface Props {
  energy: number;
  focus: number;
  maxEnergy?: number;
  maxFocus?: number;
  onRest: () => Promise<void>;
}

export default function RPGStatusBar({
  energy,
  focus,
  maxEnergy = 100,
  maxFocus = 100,
  onRest,
}: Props) {
  const [resting, setResting] = useState(false);
  const energyPct = Math.max(0, Math.min(100, (energy / maxEnergy) * 100));
  const focusPct = Math.max(0, Math.min(100, (focus / maxFocus) * 100));

  const isLowEnergy = energy <= 20;
  const isLowFocus = focus <= 20;

  const handleRest = async () => {
    setResting(true);
    try {
      await onRest();
    } finally {
      setResting(false);
    }
  };

  const energyColor =
    energyPct > 50 ? "var(--accent-amber)" : energyPct > 20 ? "#f97316" : "var(--accent-pink)";
  const focusColor =
    focusPct > 50 ? "var(--accent-violet)" : focusPct > 20 ? "#818cf8" : "var(--accent-pink)";

  return (
    <div
      style={{
        padding: "16px 20px",
        background: "var(--glass-bg)",
        border: `1px solid ${isLowEnergy ? "rgba(236,72,153,0.3)" : "var(--glass-border)"}`,
        borderRadius: "var(--radius-md)",
        transition: "border-color 0.3s ease",
        animation: isLowEnergy ? "pulseWarning 2s ease infinite" : "none",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
        <span style={{ fontSize: "0.78rem", fontWeight: 600, color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
          RPG Durumu
        </span>
        {isLowEnergy && (
          <button
            onClick={handleRest}
            disabled={resting}
            style={{
              padding: "4px 12px",
              background: "rgba(236,72,153,0.1)",
              border: "1px solid rgba(236,72,153,0.3)",
              borderRadius: "999px",
              color: "var(--accent-pink)",
              fontSize: "0.72rem",
              fontWeight: 600,
              cursor: "pointer",
              fontFamily: "'Inter', sans-serif",
              animation: "pulseWarning 1.5s ease infinite",
            }}
          >
            {resting ? "Dinleniliyor..." : "😴 Dinlen (+25 XP)"}
          </button>
        )}
      </div>

      {/* Energy Bar */}
      <div style={{ marginBottom: "10px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "5px" }}>
          <span style={{ fontSize: "0.74rem", color: isLowEnergy ? "var(--accent-pink)" : "var(--text-muted)" }}>
            ⚡ Energy {isLowEnergy && "— Düşük!"}
          </span>
          <span style={{ fontSize: "0.74rem", fontWeight: 700, color: energyColor }}>
            {energy}/{maxEnergy}
          </span>
        </div>
        <div style={{ height: "6px", background: "rgba(255,255,255,0.06)", borderRadius: "999px", overflow: "hidden" }}>
          <div
            style={{
              height: "100%",
              width: `${energyPct}%`,
              background: energyColor,
              borderRadius: "999px",
              boxShadow: `0 0 8px ${energyColor}60`,
              transition: "width 0.8s ease, background 0.3s ease",
            }}
          />
        </div>
      </div>

      {/* Focus Bar */}
      <div>
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "5px" }}>
          <span style={{ fontSize: "0.74rem", color: isLowFocus ? "var(--accent-pink)" : "var(--text-muted)" }}>
            🔮 Focus {isLowFocus && "— Düşük!"}
          </span>
          <span style={{ fontSize: "0.74rem", fontWeight: 700, color: focusColor }}>
            {focus}/{maxFocus}
          </span>
        </div>
        <div style={{ height: "6px", background: "rgba(255,255,255,0.06)", borderRadius: "999px", overflow: "hidden" }}>
          <div
            style={{
              height: "100%",
              width: `${focusPct}%`,
              background: focusColor,
              borderRadius: "999px",
              boxShadow: `0 0 8px ${focusColor}60`,
              transition: "width 0.8s ease, background 0.3s ease",
            }}
          />
        </div>
      </div>

      {/* Tooltip when full */}
      {energyPct === 100 && focusPct === 100 && (
        <p style={{ fontSize: "0.7rem", color: "var(--accent-green)", marginTop: "10px", textAlign: "center" }}>
          ✨ Tam kapasitedesin — Bu gün iyi geçecek!
        </p>
      )}

      <style>{`
        @keyframes pulseWarning {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.6; }
        }
      `}</style>
    </div>
  );
}
