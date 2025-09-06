addEventListener('DOMContentLoaded', ()=>{
  const qs=new URLSearchParams(location.search); const utm=[...qs.keys()].filter(k=>k.startsWith('utm_')); if(!utm.length) return;
  document.querySelectorAll('a[href^="/"]').forEach(a=>{
    const u=new URL(a.href, location.origin); utm.forEach(k=>u.searchParams.set(k, qs.get(k))); a.href=String(u);
  });
});
