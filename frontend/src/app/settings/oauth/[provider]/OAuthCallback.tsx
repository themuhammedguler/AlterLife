"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { connectCalendar, connectGithub } from "@/lib/api";

export default function OAuthCallback({ provider }: { provider: string }) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [message, setMessage] = useState("Bağlantı tamamlanıyor…");

  useEffect(() => {
    const code = searchParams.get("code");
    const state = searchParams.get("state");
    const stateKey = provider === "google" ? "google-calendar" : "github";
    const expectedState = sessionStorage.getItem(`alterlife_oauth_state_${stateKey}`);

    if (!code || !state || state !== expectedState) {
      setMessage("OAuth doğrulaması başarısız veya süresi dolmuş.");
      return;
    }

    sessionStorage.removeItem(`alterlife_oauth_state_${stateKey}`);
    const redirectUri = `${window.location.origin}/settings/oauth/${provider}`;
    const connect = provider === "google" ? connectCalendar : connectGithub;
    connect(code, redirectUri)
      .then(() => router.replace("/settings"))
      .catch((error) => setMessage(error instanceof Error ? error.message : "Bağlantı kurulamadı."));
  }, [provider, router, searchParams]);

  return (
    <div role="status" style={{ minHeight: "70vh", display: "grid", placeItems: "center" }}>
      <div className="glass-card" style={{ padding: 32 }}>{message}</div>
    </div>
  );
}
