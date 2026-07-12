"use client";

import { useEffect, useRef, useState } from "react";
import { fetchWithAuth } from "@/lib/api";

interface BriefingData {
  text: string;
  audio_available: boolean;
  tts_engine: string;
}

export default function DailyBriefing() {
  const [briefing, setBriefing] = useState<BriefingData | null>(null);
  const [loading, setLoading] = useState(false);
  const [playing, setPlaying] = useState(false);
  const [audioError, setAudioError] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const loadBriefing = async () => {
    setLoading(true);
    try {
      const data = await fetchWithAuth("/api/v1/briefing/daily");
      setBriefing(data);
    } catch (e) {
      console.error("Briefing load error:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBriefing();
  }, []);

  const handlePlayAudio = async () => {
    if (!briefing?.text) return;
    setAudioError(null);

    if (playing && audioRef.current) {
      audioRef.current.pause();
      setPlaying(false);
      return;
    }

    try {
      const data = await fetchWithAuth("/api/v1/briefing/tts", {
        method: "POST",
        body: JSON.stringify({ text: briefing.text, lang: "tr" }),
      });

      if (!data.audio_base64) {
        setAudioError("Ses motoru şu an kullanılamıyor.");
        return;
      }

      const audioBlob = base64ToBlob(data.audio_base64, "audio/mpeg");
      const audioUrl = URL.createObjectURL(audioBlob);

      if (audioRef.current) {
        audioRef.current.pause();
      }
      const audio = new Audio(audioUrl);
      audioRef.current = audio;

      audio.onended = () => setPlaying(false);
      audio.onerror = () => {
        setAudioError("Ses oynatılamadı.");
        setPlaying(false);
      };

      await audio.play();
      setPlaying(true);
    } catch (e) {
      setAudioError("Ses oluşturulamadı. Lütfen tekrar deneyin.");
    }
  };

  return (
    <div
      style={{
        padding: "20px 22px",
        background: "rgba(124,58,237,0.04)",
        border: "1px solid rgba(124,58,237,0.15)",
        borderRadius: "var(--radius-md)",
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* Background glow */}
      <div style={{
        position: "absolute", top: 0, right: 0, width: "120px", height: "120px",
        background: "radial-gradient(circle, rgba(124,58,237,0.12) 0%, transparent 70%)",
        pointerEvents: "none",
      }} />

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "12px" }}>
        <div>
          <div style={{ fontSize: "0.7rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "4px" }}>
            Yapay Zeka — Günlük Brifing
          </div>
          <h3 style={{ fontSize: "0.95rem", fontWeight: 700, color: "var(--accent-violet)", fontFamily: "'Outfit', sans-serif" }}>
            🤖 AlterLife AI
          </h3>
        </div>

        <button
          id="btn-briefing-play"
          onClick={handlePlayAudio}
          disabled={loading || !briefing}
          style={{
            display: "flex",
            alignItems: "center",
            gap: "6px",
            padding: "7px 14px",
            background: playing ? "rgba(124,58,237,0.15)" : "rgba(124,58,237,0.08)",
            border: `1px solid ${playing ? "var(--accent-violet)" : "rgba(124,58,237,0.25)"}`,
            borderRadius: "999px",
            color: "var(--accent-violet)",
            fontSize: "0.78rem",
            fontWeight: 600,
            cursor: "pointer",
            fontFamily: "'Inter', sans-serif",
            transition: "all 0.2s ease",
          }}
        >
          {playing ? (
            <>
              <span style={{ animation: "waveAnim 0.8s ease infinite" }}>🔊</span>
              Durdur
            </>
          ) : (
            <>
              🎙️ Dinle
            </>
          )}
        </button>
      </div>

      {loading ? (
        <div style={{ fontSize: "0.82rem", color: "var(--text-muted)", fontStyle: "italic" }}>
          Brifing hazırlanıyor...
        </div>
      ) : briefing ? (
        <p style={{
          fontSize: "0.84rem",
          color: "var(--text-secondary)",
          lineHeight: 1.65,
          fontStyle: "italic",
        }}>
          "{briefing.text}"
        </p>
      ) : null}

      {audioError && (
        <p style={{ fontSize: "0.75rem", color: "var(--accent-pink)", marginTop: "8px" }}>
          {audioError}
        </p>
      )}

      {briefing && !briefing.audio_available && (
        <p style={{ fontSize: "0.7rem", color: "var(--text-muted)", marginTop: "8px" }}>
          💡 Sesli brifing için backend&apos;e <code>gtts</code> kurun: <code>pip install gtts</code>
        </p>
      )}

      {/* Sound wave animation when playing */}
      {playing && (
        <div style={{ display: "flex", gap: "3px", alignItems: "center", marginTop: "12px" }}>
          {[1, 2, 3, 4, 5, 4, 3, 2, 1].map((h, i) => (
            <div
              key={i}
              style={{
                width: "3px",
                height: `${h * 4}px`,
                background: "var(--accent-violet)",
                borderRadius: "999px",
                animation: `waveBar 0.8s ease ${i * 0.1}s infinite`,
                opacity: 0.8,
              }}
            />
          ))}
        </div>
      )}

      <style>{`
        @keyframes waveBar {
          0%, 100% { transform: scaleY(1); opacity: 0.8; }
          50% { transform: scaleY(1.8); opacity: 1; }
        }
        @keyframes waveAnim {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.2); }
        }
      `}</style>
    </div>
  );
}

function base64ToBlob(base64: string, mimeType: string): Blob {
  const bytes = atob(base64);
  const ab = new ArrayBuffer(bytes.length);
  const ia = new Uint8Array(ab);
  for (let i = 0; i < bytes.length; i++) {
    ia[i] = bytes.charCodeAt(i);
  }
  return new Blob([ab], { type: mimeType });
}
