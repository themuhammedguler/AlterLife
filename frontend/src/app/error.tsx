"use client";

import { useEffect } from "react";

export default function ErrorPage({
  error,
  unstable_retry,
}: {
  error: Error & { digest?: string };
  unstable_retry: () => void;
}) {
  useEffect(() => {
    console.error("AlterLife page error", error);
  }, [error]);

  return (
    <section className="system-state" role="alert">
      <div className="glass-card system-state-card">
        <p className="system-state-code">SİSTEM HATASI</p>
        <h1>Bu evren dalı yüklenemedi.</h1>
        <p>Geçici bir sorun oluştu. Verileriniz korunuyor; işlemi yeniden deneyebilirsiniz.</p>
        {error.digest && <small>Hata referansı: {error.digest}</small>}
        <button type="button" className="btn-primary" onClick={() => unstable_retry()}>
          Yeniden Dene
        </button>
      </div>
    </section>
  );
}
