import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",  // Docker multi-stage build için gerekli
};

export default nextConfig;
