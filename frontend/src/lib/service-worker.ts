// Service Worker Registration
// This file registers the service worker for offline capabilities

export const registerServiceWorker = () => {
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/sw.js')
        .then(registration => {
          console.log('SW registered: ', registration);
          
          // Handle updates
          registration.onupdatefound = () => {
            const installingWorker = registration.installing;
            if (installingWorker) {
              installingWorker.onstatechange = () => {
                if (installingWorker.state === 'installed') {
                  if (navigator.serviceWorker.controller) {
                    // New update available
                    console.log('New content is available; please refresh.');
                  } else {
                    // Content is cached for offline use
                    console.log('Content is cached for offline use.');
                  }
                }
              };
            }
          };
        })
        .catch(error => {
          console.log('SW registration failed: ', error);
        });
    });
  }
};

export const unregisterServiceWorker = () => {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.ready
      .then(registration => {
        registration.unregister();
      })
      .catch(error => {
        console.log('SW unregistration failed: ', error);
      });
  }
};