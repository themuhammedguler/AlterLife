"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { isAuthenticated } from "@/lib/api";

const PUBLIC_ROUTES = new Set(["/", "/login", "/demo"]);

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (!PUBLIC_ROUTES.has(pathname) && !isAuthenticated()) {
      router.replace(`/login?next=${encodeURIComponent(pathname)}`);
      return;
    }
    setReady(true);
  }, [pathname, router]);

  if (!ready && !PUBLIC_ROUTES.has(pathname)) {
    return (
      <div role="status" style={{ minHeight: "100vh", display: "grid", placeItems: "center" }}>
        Oturum kontrol ediliyor…
      </div>
    );
  }

  return children;
}
