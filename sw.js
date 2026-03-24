const CACHE_NAME = 'ipl-fantasy-v1';

// Install the service worker
self.addEventListener('install', event => {
  self.skipWaiting();
});

// Fetch data (keeps the app requiring internet so live scores always load)
self.addEventListener('fetch', event => {
  event.respondWith(fetch(event.request));
});
