import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import AstroPWA from '@vite-pwa/astro';

export default defineConfig({
  site: 'https://fitness.local',
  build: { format: 'directory' },
  // Must be 'always': @vite-pwa/astro derives precache URLs from this, and with
  // 'ignore' it stores "/programs/marathon" while every link points at
  // "/programs/marathon/" — the lookup misses and offline silently serves nothing.
  trailingSlash: 'always',
  integrations: [
    mdx(),
    AstroPWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'Training',
        short_name: 'Training',
        description: 'Marathon and strength plans.',
        theme_color: '#0F1316',
        background_color: '#0F1316',
        display: 'standalone',
        start_url: '/',
        icons: [
          { src: 'icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: 'icon-512.png', sizes: '512x512', type: 'image/png' },
          { src: 'icon-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
        ],
      },
      workbox: {
        // archive/*.html and *.md are picked up here; do NOT also list them in
        // includeAssets — the two collide and Workbox refuses conflicting revisions.
        globPatterns: ['**/*.{html,css,js,svg,png,ico,webmanifest,md}'],
        navigateFallback: '/',
        runtimeCaching: [
          {
            // Thumbnails survive offline — better than the originals, where the tiles went blank.
            urlPattern: /^https:\/\/i\.ytimg\.com\/.*/,
            handler: 'StaleWhileRevalidate',
            options: {
              cacheName: 'yt-thumbnails',
              expiration: { maxEntries: 60, maxAgeSeconds: 60 * 60 * 24 * 90 },
              cacheableResponse: { statuses: [0, 200] },
            },
          },
        ],
      },
      // The player itself must never be precached — it needs signal by design.
      devOptions: { enabled: false },
    }),
  ],
});
