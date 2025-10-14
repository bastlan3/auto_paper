/** @type {import('next').NextConfig} */
const nextConfig = {
    async rewrites() {
        return [
            {
                source: '/api/:path*',
                destination: 'http://localhost:8000/api/:path*', // Proxy to Backend
            },
        ];
    },
     experimental: {
    proxyTimeout: 600000, // 10 minutes in milliseconds
  },
};

export default nextConfig;