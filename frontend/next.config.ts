import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',
  distDir: '.next',
  // Ensure proper asset serving in production
  basePath: '',
  assetPrefix: '/',
  // Generate static HTML files with .html extension
  trailingSlash: false,
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
  // Optimize for production deployment
  poweredByHeader: false,
};

export default nextConfig;
