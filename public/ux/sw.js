const CACHE='fc-v1';
const ASSETS=['/','/ux/elite.css','/ux/init.js','/ux/pro.js'];
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS))));
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k))))));
self.addEventListener('fetch',e=>{
  const u=new URL(e.request.url);
  if(u.pathname.startsWith('/ux')||u.pathname.startsWith('/images')||u.pathname==='/'){
    e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request).then(res=>{ const copy=res.clone(); caches.open(CACHE).then(c=>c.put(e.request,copy)); return res; }).catch(()=>r)));
  }
});
