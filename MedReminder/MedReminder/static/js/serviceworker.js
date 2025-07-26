// Service worker for push notifications

self.addEventListener('push', function(event) {
    const data = event.data.json();
    const title = data.title || 'MedReminder';
    const options = {
        body: data.body,
        icon: data.icon || '/static/images/icon.png',
        badge: data.badge || '/static/images/badge.png',
        data: data.data
    };

    event.waitUntil(
        self.registration.showNotification(title, options)
    );
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    // Handle notification click
    if (event.notification.data && event.notification.data.url) {
        event.waitUntil(
            clients.openWindow(event.notification.data.url)
        );
    }
});
