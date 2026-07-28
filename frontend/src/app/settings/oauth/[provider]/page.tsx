import { Suspense } from "react";
import OAuthCallback from "./OAuthCallback";

export default async function OAuthCallbackPage({
  params,
}: {
  params: Promise<{ provider: string }>;
}) {
  const { provider } = await params;
  return (
    <Suspense fallback={<div>OAuth sonucu yükleniyor…</div>}>
      <OAuthCallback provider={provider} />
    </Suspense>
  );
}
