import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',
  distDir: '.next',
  experimental: {
    serverActions: {
      bodySizeLimit: '2mb',
    },
  },
  // Disable caching for server components to prevent stale deployments
  cacheHandler: undefined,
  generateEtags: false,
};

export default nextConfig;
