import type { Metadata } from "next";
import "./globals.css";
import Navbar from "@/components/Navbar";

export const metadata: Metadata = {
  title: "AlterLife – Dijital İkizinle Geleceğini Şekillendir",
  description:
    "Kariyerini, finansını ve hayatını simüle eden kişisel AI karar destek sistemi. 'Almanya'ya gidersem ne olur?' – AlterLife ile cevapla.",
  keywords: ["digital twin", "AI", "karar destek", "kariyer simülatör", "RPG"],
  openGraph: {
    title: "AlterLife – Enter the Simulation",
    description: "Hayatının farklı yollarını AI ile simüle et.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="tr">
      <body>
        {/* Ambient Background Orbs */}
        <div className="orb orb-violet" aria-hidden="true" />
        <div className="orb orb-cyan" aria-hidden="true" />

        <Navbar />
        <main>{children}</main>
      </body>
    </html>
  );
}
