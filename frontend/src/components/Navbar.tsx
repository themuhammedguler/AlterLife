"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navLinks = [
  { href: "/dashboard",   label: "Dashboard" },
  { href: "/simulations", label: "Simulasyon" },
  { href: "/skills",      label: "Yetenekler" },
  { href: "/library",     label: "Kutuphane" },
  { href: "/analytics",   label: "Analitik" },
  { href: "/community",   label: "Topluluk" },
];

export default function Navbar() {
  const pathname = usePathname();

  if (pathname === "/login" || pathname === "/onboarding" || pathname === "/") {
    return null;
  }

  return (
    <nav
      style={{
        height: "var(--nav-height)",
        background: "rgba(7, 11, 20, 0.85)",
        backdropFilter: "blur(20px)",
        WebkitBackdropFilter: "blur(20px)",
        borderBottom: "1px solid var(--glass-border)",
        position: "sticky",
        top: 0,
        zIndex: 100,
        display: "flex",
        alignItems: "center",
        padding: "0 28px",
        justifyContent: "space-between",
      }}
    >
      {/* Logo */}
      <Link href="/dashboard" style={{ textDecoration: "none" }}>
        <span
          className="text-gradient"
          style={{
            fontFamily: "'Outfit', sans-serif",
            fontWeight: 800,
            fontSize: "1.2rem",
            letterSpacing: "-0.01em",
          }}
        >
          AlterLife
        </span>
      </Link>

      {/* Nav links */}
      <div style={{ display: "flex", gap: "2px" }}>
        {navLinks.map((link) => {
          const isActive = pathname === link.href;
          return (
            <Link
              key={link.href}
              href={link.href}
              style={{
                display: "flex",
                alignItems: "center",
                padding: "6px 14px",
                borderRadius: "var(--radius-sm)",
                textDecoration: "none",
                fontSize: "0.85rem",
                fontWeight: isActive ? 600 : 400,
                fontFamily: "'Inter', sans-serif",
                color: isActive ? "var(--accent-cyan)" : "var(--text-secondary)",
                background: isActive ? "rgba(0, 229, 255, 0.08)" : "transparent",
                border: isActive ? "1px solid rgba(0, 229, 255, 0.2)" : "1px solid transparent",
                transition: "all 0.2s ease",
              }}
            >
              {link.label}
            </Link>
          );
        })}
      </div>

      {/* Profile */}
      <Link
        href="/settings"
        style={{
          display: "flex",
          alignItems: "center",
          gap: "10px",
          textDecoration: "none",
          padding: "6px 16px",
          borderRadius: "var(--radius-md)",
          border: "1px solid var(--glass-border)",
          background: "var(--glass-bg)",
          transition: "all 0.2s ease",
        }}
      >
        <div
          style={{
            width: "28px",
            height: "28px",
            borderRadius: "50%",
            background: "var(--gradient-cyan-violet)",
          }}
        />
        <div>
          <div style={{ fontSize: "0.82rem", fontWeight: 600, color: "var(--text-primary)" }}>
            Sedef K.
          </div>
          <div style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>Svr 1 · 0 XP</div>
        </div>
      </Link>
    </nav>
  );
}
