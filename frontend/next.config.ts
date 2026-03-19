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
  // Additional Server Actions stability configurations
  reactStrictMode: true,
  // Clear server action cache on build
  cleanDistDir: true,
};

export default nextConfig;
