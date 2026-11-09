const CACHE_NAME = 'oracle-cache-v1';
const ASSETS = [
  '/',
  '/static/index.html',
  '/static/manifest.json',
  '/static/icon.svg',
  'https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,600&family=Hanken+Grotesk:wght@400;500;600&display=swap'
];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS)));
});

self.addEventListener('fetch', (e) => {
  if (e.request.url.includes('/api/')) return; 
  e.respondWith(caches.match(e.request).then((res) => res || fetch(e.request)));
});
