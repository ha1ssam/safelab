/** @type {import('next').NextConfig} */
const nextConfig = {
  // Django expects URLs ending in `/`. Without `trailingSlash: true`, Next 13
  // strips the slash and Django returns 404 on POST/PUT (its APPEND_SLASH
  // redirect only works for GET).
  trailingSlash: true,
  // Skip the 308 redirect Next would otherwise issue when normalizing trailing
  // slashes — we want the rewrite to forward the request as-is.
  skipTrailingSlashRedirect: true,
  async rewrites() {
    return [
      // 127.0.0.1 (not "localhost") avoids Node connecting over IPv6 (::1) to
      // a Django process bound to IPv4 only.
      {
        source: "/api/:path*",
        destination: "http://127.0.0.1:8000/api/:path*/",
      },
      {
        source: "/media/:path*",
        destination: "http://127.0.0.1:8000/media/:path*",
      },
    ];
  },
};

module.exports = nextConfig;
