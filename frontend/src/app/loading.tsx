export default function Loading() {
  return (
    <div className="system-state" role="status" aria-live="polite">
      <div className="glass-card system-state-card">
        <div className="loading-orbit" aria-hidden="true" />
        <p>Simülasyon verileri yükleniyor…</p>
      </div>
    </div>
  );
}
