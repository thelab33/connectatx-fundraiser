const CACHE = 'fc-static-v1';
const ASSETS = [
  '/static/css/tailwind.min.css',
  '/static/css/fc-tokens.css',
  '/static/images/hero.avif'
];
self.addEventListener('install', e => e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS))));
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  e.respondWith(caches.match(e.request).then(r => r || fetch(e.request)));
});

