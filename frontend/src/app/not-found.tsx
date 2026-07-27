import Link from "next/link";

export default function NotFound() {
  return (
    <section className="system-state">
      <div className="glass-card system-state-card">
        <p className="system-state-code">404 · EVREN BULUNAMADI</p>
        <h1>Bu yaşam dalı henüz oluşturulmamış.</h1>
        <p>Bağlantı değişmiş veya aradığınız sayfa başka bir evrende kalmış olabilir.</p>
        <Link className="btn-primary" href="/dashboard">Dashboard’a Dön</Link>
      </div>
    </section>
  );
}
