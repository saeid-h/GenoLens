/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Relatives compare / family-tree can exceed the default ~30s proxy cutoff.
  experimental: {
    proxyTimeout: 300_000,
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://127.0.0.1:8000/api/:path*",
      },
    ];
  },
};

export default nextConfig;
