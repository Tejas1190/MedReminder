// Function to convert base64 string to Uint8Array
function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
        .replace(/\-/g, '+')
        .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

// Register service worker and subscribe to push
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register(serviceWorkerPath).then(function(registration) {
        console.log('Service Worker registered with scope:', registration.scope);
        
        // Request permission for notifications
        return Notification.requestPermission();
    }).then(function(permission) {
        if (permission === 'granted') {
            console.log('Notification permission granted.');
            // Get the subscription
            return navigator.serviceWorker.ready;
        }
    }).then(function(serviceWorkerRegistration) {
        return serviceWorkerRegistration.pushManager.getSubscription();
    }).then(function(subscription) {
        if (subscription) {
            return subscription;
        }
        
        // Subscribe with VAPID public key
        return navigator.serviceWorker.ready.then(function(serviceWorkerRegistration) {
            return serviceWorkerRegistration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: urlBase64ToUint8Array(vapidPublicKey)
            });
        });
    }).then(function(subscription) {
        // Send subscription to backend
        fetch('/register-push/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(subscription)
        });
    }).catch(function(error) {
        console.error('Service Worker registration failed:', error);
    });
}
