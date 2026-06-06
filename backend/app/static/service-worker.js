const CACHE_NAME = "landa-cache-v1";
const ASSETS = [
    "/",
    "/static/css/base.css",
    "/static/manifest.json",
];

self.addEventListener("install", function (event) {
    event.waitUntil(
        caches.open(CACHE_NAME).then(function (cache) {
            return cache.addAll(ASSETS);
        })
    );
});

self.addEventListener("activate", function (event) {
    event.waitUntil(
        caches.keys().then(function (keys) {
            return Promise.all(
                keys
                    .filter(function (key) {
                        return key !== CACHE_NAME;
                    })
                    .map(function (key) {
                        return caches.delete(key);
                    })
            );
        })
    );
});

self.addEventListener("fetch", function (event) {
    if (event.request.url.startsWith(self.location.origin)) {
        event.respondWith(
            caches.match(event.request).then(function (cached) {
                return cached || fetch(event.request);
            })
        );
    }
});
