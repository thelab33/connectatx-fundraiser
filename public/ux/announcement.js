const KEY='fc-ann-dismiss';
addEventListener('DOMContentLoaded', ()=>{
  const host = document.querySelector('[data-announcement]'); if(!host) return;
  const id = host.dataset.id || host.textContent?.trim()?.slice(0,24) || 'default';
  if(localStorage.getItem(KEY+id)) return host.remove();
  const start = host.dataset.start? new Date(host.dataset.start):null;
  const end   = host.dataset.end?   new Date(host.dataset.end):null;
  const now = new Date();
  if(start && now<start || end && now>end) return host.remove();
  host.classList.add('announce'); host.innerHTML = `
    <div class="announce__inner">
      <div class="muted"><strong class="brand">📣 ${host.dataset.title||'Update'}</strong> ${host.dataset.text||host.textContent||''}</div>
      ${host.dataset.href? `<a class="announce__cta" href="${host.dataset.href}">${host.dataset.cta||'Learn more'}</a>`:''}
      <button class="announce__close" aria-label="Dismiss">✕</button>
    </div>`;
  host.querySelector('.announce__close')?.addEventListener('click',()=>{ localStorage.setItem(KEY+id,'1'); host.remove(); });
});
