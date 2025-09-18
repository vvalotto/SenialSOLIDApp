// Service Worker for Senial SOLID - Performance Optimization
const CACHE_NAME = 'senial-solid-v1.5.0';
const STATIC_CACHE = 'senial-static-v1.5.0';
const DYNAMIC_CACHE = 'senial-dynamic-v1.5.0';

// Assets to cache immediately
const STATIC_ASSETS = [
    '/',
    '/static/dist/main.min.css',
    '/static/dist/main.min.js',
    '/static/dist/vendors.min.js',
    '/static/favicon.ico',
    '/static/css/critical.css'
];

// CDN assets to cache
const CDN_ASSETS = [
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js',
    'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css'
];

// Install event - cache static assets
self.addEventListener('install', event => {
    console.log('SW: Installing service worker...');
    
    event.waitUntil(
        Promise.all([
            // Cache static assets
            caches.open(STATIC_CACHE).then(cache => {
                console.log('SW: Caching static assets');
                return cache.addAll(STATIC_ASSETS.concat(CDN_ASSETS));
            }),
            // Skip waiting to activate immediately
            self.skipWaiting()
        ])
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
    console.log('SW: Activating service worker...');
    
    event.waitUntil(
        Promise.all([
            // Clean up old caches
            caches.keys().then(cacheNames => {
                return Promise.all(
                    cacheNames
                        .filter(name => name !== STATIC_CACHE && name !== DYNAMIC_CACHE)
                        .map(name => {
                            console.log('SW: Deleting old cache:', name);
                            return caches.delete(name);
                        })
                );
            }),
            // Take control immediately
            self.clients.claim()
        ])
    );
});

// Fetch event - implement caching strategies
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }
    
    // Skip chrome-extension and other non-http(s) URLs
    if (!url.protocol.startsWith('http')) {
        return;
    }
    
    // Different strategies based on resource type
    if (isStaticAsset(url)) {
        event.respondWith(cacheFirstStrategy(request));
    } else if (isAPIRequest(url)) {
        event.respondWith(networkFirstStrategy(request));
    } else if (isImageRequest(url)) {
        event.respondWith(cacheFirstStrategy(request));
    } else if (isCDNRequest(url)) {
        event.respondWith(staleWhileRevalidateStrategy(request));
    } else {
        event.respondWith(networkFirstStrategy(request));
    }
});

// Cache First Strategy - Good for static assets
async function cacheFirstStrategy(request) {
    try {
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            const cache = await caches.open(STATIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        console.warn('SW: Cache first strategy failed:', error);
        return new Response('Offline - Resource not available', { status: 503 });
    }
}

// Network First Strategy - Good for dynamic content
async function networkFirstStrategy(request) {
    try {
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        console.warn('SW: Network first strategy failed, trying cache:', error);
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        return new Response('Offline - Content not available', { status: 503 });
    }
}

// Stale While Revalidate Strategy - Good for CDN resources
async function staleWhileRevalidateStrategy(request) {
    const cachedResponse = await caches.match(request);
    const fetchPromise = fetch(request).then(response => {
        if (response.ok) {
            const cache = caches.open(STATIC_CACHE);
            cache.then(c => c.put(request, response.clone()));
        }
        return response;
    }).catch(() => cachedResponse);
    
    return cachedResponse || fetchPromise;
}

// Helper functions to identify request types
function isStaticAsset(url) {
    return url.pathname.includes('/static/') || 
           url.pathname.endsWith('.css') || 
           url.pathname.endsWith('.js') ||
           url.pathname.endsWith('.ico');
}

function isAPIRequest(url) {
    return url.pathname.startsWith('/api/') || 
           url.pathname.includes('/ajax/') ||
           url.search.includes('ajax=1');
}

function isImageRequest(url) {
    return /\.(png|jpg|jpeg|gif|webp|avif|svg)$/i.test(url.pathname);
}

function isCDNRequest(url) {
    return url.hostname.includes('cdn.jsdelivr.net') ||
           url.hostname.includes('cdnjs.cloudflare.com') ||
           url.hostname.includes('unpkg.com');
}

// Background sync for offline actions (future enhancement)
self.addEventListener('sync', event => {
    console.log('SW: Background sync triggered:', event.tag);
    
    if (event.tag === 'background-sync') {
        event.waitUntil(doBackgroundSync());
    }
});

async function doBackgroundSync() {
    try {
        // Sync pending actions when back online
        console.log('SW: Performing background sync...');
        
        // Example: Send queued analytics, form submissions, etc.
        const pendingRequests = await getStoredRequests();
        await Promise.all(pendingRequests.map(sendRequest));
        await clearStoredRequests();
        
    } catch (error) {
        console.error('SW: Background sync failed:', error);
    }
}

// Push notifications (future enhancement)
self.addEventListener('push', event => {
    if (!event.data) return;
    
    const data = event.data.json();
    const options = {
        body: data.body,
        icon: '/static/favicon.ico',
        badge: '/static/favicon.ico',
        vibrate: [100, 50, 100],
        data: {
            url: data.url || '/',
            timestamp: Date.now()
        },
        actions: [
            {
                action: 'view',
                title: 'Ver',
                icon: '/static/favicon.ico'
            },
            {
                action: 'dismiss',
                title: 'Descartar'
            }
        ]
    };
    
    event.waitUntil(
        self.registration.showNotification(data.title || 'Senial SOLID', options)
    );
});

// Notification click handling
self.addEventListener('notificationclick', event => {
    event.notification.close();
    
    if (event.action === 'view') {
        const url = event.notification.data.url;
        event.waitUntil(clients.openWindow(url));
    }
});

// Placeholder functions for offline capabilities
async function getStoredRequests() {
    // Return stored requests from IndexedDB
    return [];
}

async function sendRequest(request) {
    // Send individual request
    return fetch(request);
}

async function clearStoredRequests() {
    // Clear stored requests from IndexedDB
    return true;
}

// Performance monitoring
self.addEventListener('message', event => {
    if (event.data && event.data.type === 'PERFORMANCE_METRIC') {
        console.log('SW: Performance metric received:', event.data.metric);
        // Store or send performance metrics
    }
});

// Cache size management
async function manageCacheSize() {
    const cacheNames = await caches.keys();
    
    for (const cacheName of cacheNames) {
        const cache = await caches.open(cacheName);
        const requests = await cache.keys();
        
        // Keep only the most recent 50 entries per cache
        if (requests.length > 50) {
            const oldRequests = requests.slice(0, requests.length - 50);
            await Promise.all(oldRequests.map(request => cache.delete(request)));
        }
    }
}

// Run cache management every hour
setInterval(manageCacheSize, 60 * 60 * 1000);