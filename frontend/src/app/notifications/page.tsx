"use client";

import { useEffect, useState } from "react";
import { getNotifications, markNotificationRead } from "@/lib/api";

export default function NotificationsPage() {
  const [items, setItems] = useState<any[]>([]);
  const [unread, setUnread] = useState(0);

  const load = async () => {
    const data = await getNotifications();
    setItems(data.notifications || []);
    setUnread(data.unread_count || 0);
  };

  useEffect(() => {
    load().catch(console.error);
  }, []);

  const markRead = async (id: string) => {
    await markNotificationRead(id);
    await load();
  };

  return (
    <div className="page-container" style={{ maxWidth: "900px", padding: "40px 24px" }}>
      <div className="page-header" style={{ marginBottom: "28px" }}>
        <h1 className="page-title" style={{ fontSize: "2rem", fontWeight: 800 }}>
          <span className="text-gradient">Bildirim Merkezi</span>
        </h1>
        <p className="page-subtitle" style={{ color: "var(--text-secondary)", fontSize: "0.95rem" }}>
          {unread} okunmamış sinyal: quest, risk, review ve hedef hatırlatmaları.
        </p>
      </div>

      <div style={{ display: "grid", gap: "14px" }}>
        {items.map((item) => (
          <article
            key={item.notification_id}
            className="glass-card"
            style={{
              padding: "20px",
              borderColor: item.is_read ? "var(--glass-border)" : "rgba(0,229,255,0.32)",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", gap: "16px" }}>
              <div>
                <span style={{ color: severityColor(item.severity), fontSize: "0.75rem", fontWeight: 800 }}>
                  {item.type.toUpperCase()}
                </span>
                <h2 style={{ fontSize: "1rem", margin: "6px 0" }}>{item.title}</h2>
                <p style={{ color: "var(--text-secondary)", fontSize: "0.86rem", lineHeight: 1.55 }}>{item.message}</p>
              </div>
              <button className="btn-ghost" disabled={item.is_read} onClick={() => markRead(item.notification_id)}>
                {item.is_read ? "Okundu" : "Okundu Yap"}
              </button>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}

function severityColor(severity: string) {
  if (severity === "warning") return "var(--accent-amber)";
  if (severity === "success") return "var(--accent-green)";
  return "var(--accent-cyan)";
}
