self.addEventListener('install', function(event) {
  self.skipWaiting();
});

self.addEventListener('activate', function(event) {
  event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request).then(function(response) {
      return response || fetch(event.request);
    })
  );
});

// Placeholder for push notifications
self.addEventListener('push', function(event) {
  const data = event.data ? event.data.text() : 'MedReminder Notification';
  event.waitUntil(
    self.registration.showNotification('MedReminder', {
      body: data,
      icon: '/static/icons/icon-192x192.png'
    })
  );
}); 