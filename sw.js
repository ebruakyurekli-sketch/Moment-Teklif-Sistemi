/* Moment Teklif Sistemi — Service Worker v1 */
const CACHE = 'moment-v1';
const STATIC = ['/logo_img'];

/* Kurulum: sadece logo'yu önbelleğe al */
self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(STATIC)).then(() => self.skipWaiting())
  );
});

/* Aktivasyon: eski cache sürümlerini temizle */
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

/* Fetch stratejisi:
   - API çağrıları (/api/, /generate_pdf, /login, /logout) → her zaman network
   - Diğerleri → network-first, hata olursa cache, o da yoksa offline sayfası
*/
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);

  /* Sadece aynı origin, GET istekleri */
  if (e.request.method !== 'GET' || url.origin !== self.location.origin) return;

  /* API ve PDF → network only */
  if (url.pathname.startsWith('/api/') ||
      url.pathname.startsWith('/generate_pdf') ||
      url.pathname === '/login' ||
      url.pathname === '/logout') {
    return; /* tarayıcı varsayılan davranışına bırak */
  }

  /* Network-first */
  e.respondWith(
    fetch(e.request)
      .then(res => {
        /* Başarılıysa cache'e de yaz (logo gibi statik kaynaklar) */
        if (res.ok && STATIC.includes(url.pathname)) {
          const clone = res.clone();
          caches.open(CACHE).then(c => c.put(e.request, clone));
        }
        return res;
      })
      .catch(() =>
        caches.match(e.request).then(cached => {
          if (cached) return cached;
          /* Tamamen offline ve ana sayfa isteniyorsa minimal mesaj */
          if (url.pathname === '/') {
            return new Response(
              `<!DOCTYPE html><html lang="tr"><head><meta charset="UTF-8">
               <meta name="viewport" content="width=device-width,initial-scale=1">
               <title>Moment Teklif</title>
               <style>body{font-family:-apple-system,sans-serif;display:flex;align-items:center;
               justify-content:center;height:100vh;margin:0;background:#EDE3D0;text-align:center}
               h2{color:#1C1C1C;font-size:20px}p{color:#666;font-size:14px;margin-top:8px}</style>
               </head><body><div>
               <div style="font-size:42px;margin-bottom:12px">📵</div>
               <h2>İnternet Bağlantısı Yok</h2>
               <p>Teklif sistemine erişmek için<br>internet bağlantısı gereklidir.</p>
               </div></body></html>`,
              { headers: { 'Content-Type': 'text/html; charset=utf-8' } }
            );
          }
        })
      )
  );
});
