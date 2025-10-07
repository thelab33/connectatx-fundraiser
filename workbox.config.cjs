module.exports = {
  globDirectory: 'app/static/',
  globPatterns: ['**/*.{js,css,svg,woff2,json,png,jpg,jpeg,webp,avif,xml,txt}'],
  swDest: 'app/static/sw.js',
  ignoreURLParametersMatching: [/^utm_/, /^fbclid$/],
  maximumFileSizeToCacheInBytes: 8 * 1024 * 1024,
  runtimeCaching: [
    {
      urlPattern: ({request}) => request.destination === 'image',
      handler: 'CacheFirst',
      options: {
        cacheName: 'images-v1',
        expiration: { maxEntries: 150, maxAgeSeconds: 60 * 60 * 24 * 30 }
      }
    },
    {
      urlPattern: ({request}) => ['style','script','worker'].includes(request.destination),
      handler: 'StaleWhileRevalidate',
      options: { cacheName: 'assets-v1' }
    }
  ]
};
