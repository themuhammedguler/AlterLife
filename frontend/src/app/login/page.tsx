"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { loginWithEmail, loginWithGoogle } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGoogleLogin = async () => {
    setLoading(true);
    setError(null);
    try {
      // Simulate Google Sign-In by requesting a token from Firebase/Google 
      // or passing a mock identifier in fallback mode.
      const mockGoogleIdToken = "mock_token_sedef_google";
      const data = await loginWithGoogle(mockGoogleIdToken);
      if (data.is_new_user) {
        router.push("/onboarding");
      } else {
        router.push("/dashboard");
      }
    } catch (err: any) {
      setError(err.message || "Google ile giriş yaparken bir hata oluştu.");
    } finally {
      setLoading(false);
    }
  };

  const handleEmailLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setError("Lütfen e-posta ve şifrenizi girin.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await loginWithEmail(email, password);
      if (data.is_new_user) {
        router.push("/onboarding");
      } else {
        router.push("/dashboard");
      }
    } catch (err: any) {
      setError(err.message || "Giriş başarısız. Lütfen bilgilerinizi kontrol edin.");
    } finally {
      setLoading(false);
    }
  };

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
      <div
        className="glass-card animate-fade-up"
        style={{ width: "100%", maxWidth: "420px", padding: "52px 44px", textAlign: "center" }}
      >
        <h1
          style={{
            fontFamily: "'Outfit', sans-serif",
            fontSize: "2rem",
            fontWeight: 800,
            marginBottom: "8px",
            letterSpacing: "-0.02em",
          }}
        >
          <span className="text-gradient">AlterLife</span>
        </h1>
        <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem", marginBottom: "32px" }}>
          Dijital ikizinle geleceğini şekillendirmeye başla.
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
              textAlign: "left",
            }}
          >
            {error}
          </div>
        )}

        {/* Google OAuth Button */}
        <button
          id="btn-google-login"
          disabled={loading}
          style={{
            width: "100%",
            padding: "14px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "12px",
            background: "rgba(255,255,255,0.06)",
            border: "1px solid var(--glass-border)",
            borderRadius: "var(--radius-md)",
            color: "var(--text-primary)",
            fontFamily: "'Outfit', sans-serif",
            fontWeight: 600,
            fontSize: "0.95rem",
            cursor: loading ? "not-allowed" : "pointer",
            transition: "all 0.2s ease",
            marginBottom: "20px",
            opacity: loading ? 0.7 : 1,
          }}
          onClick={handleGoogleLogin}
        >
          <svg width="18" height="18" viewBox="0 0 48 48">
            <path fill="#FFC107" d="M43.611 20.083H42V20H24v8h11.303c-1.649 4.657-6.08 8-11.303 8-6.627 0-12-5.373-12-12s5.373-12 12-12c3.059 0 5.842 1.154 7.961 3.039l5.657-5.657C34.046 6.053 29.268 4 24 4 12.955 4 4 12.955 4 24s8.955 20 20 20 20-8.955 20-20c0-1.341-.138-2.65-.389-3.917z"/>
            <path fill="#FF3D00" d="m6.306 14.691 6.571 4.819C14.655 15.108 18.961 12 24 12c3.059 0 5.842 1.154 7.961 3.039l5.657-5.657C34.046 6.053 29.268 4 24 4 16.318 4 9.656 8.337 6.306 14.691z"/>
            <path fill="#4CAF50" d="M24 44c5.166 0 9.86-1.977 13.409-5.192l-6.19-5.238A11.91 11.91 0 0 1 24 36c-5.202 0-9.619-3.317-11.283-7.946l-6.522 5.025C9.505 39.556 16.227 44 24 44z"/>
            <path fill="#1976D2" d="M43.611 20.083H42V20H24v8h11.303a12.04 12.04 0 0 1-4.087 5.571l.003-.002 6.19 5.238C36.971 39.205 44 34 44 24c0-1.341-.138-2.65-.389-3.917z"/>
          </svg>
          Google ile Giriş Yap
        </button>

        {/* Divider */}
        <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "20px" }}>
          <div style={{ flex: 1, height: "1px", background: "var(--glass-border)" }} />
          <span style={{ color: "var(--text-muted)", fontSize: "0.8rem" }}>veya</span>
          <div style={{ flex: 1, height: "1px", background: "var(--glass-border)" }} />
        </div>

        {/* Email / password Form */}
        <form onSubmit={handleEmailLogin}>
          <div style={{ display: "flex", flexDirection: "column", gap: "10px", marginBottom: "20px" }}>
            <input
              id="input-email"
              type="email"
              placeholder="E-posta adresiniz"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={loading}
              style={inputStyle}
            />
            <input
              id="input-password"
              type="password"
              placeholder="Şifre"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading}
              style={inputStyle}
            />
          </div>

          <button
            id="btn-email-login"
            type="submit"
            className="btn-primary"
            disabled={loading}
            style={{ width: "100%", justifyContent: "center", opacity: loading ? 0.7 : 1 }}
          >
            {loading ? "Giriş Yapılıyor..." : "Giriş Yap"}
          </button>
        </form>

        <p style={{ marginTop: "24px", fontSize: "0.82rem", color: "var(--text-muted)" }}>
          Hesabın yok mu?{" "}
          <Link href="/onboarding" style={{ color: "var(--accent-cyan)", textDecoration: "none", fontWeight: 600 }}>
            Kayıt Ol
          </Link>
        </p>
      </div>
    </div>
  );
}

const inputStyle: React.CSSProperties = {
  padding: "12px 16px",
  background: "rgba(255,255,255,0.04)",
  border: "1px solid var(--glass-border)",
  borderRadius: "var(--radius-md)",
  color: "var(--text-primary)",
  fontSize: "0.9rem",
  outline: "none",
  fontFamily: "'Inter', sans-serif",
  width: "100%",
};
