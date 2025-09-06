function toast(msg){ const t=document.createElement('div'); t.className='toast'; t.textContent=msg; document.body.appendChild(t); setTimeout(()=>t.remove(),1600); }
addEventListener('DOMContentLoaded', ()=>{
  document.querySelectorAll('[data-share]').forEach(btn=>{
    btn.addEventListener('click', async ()=>{
      const url = new URL(btn.dataset.url || location.href);
      if(btn.dataset.utm) url.searchParams.set('utm_source', btn.dataset.utm);
      const data = {title:btn.dataset.title||document.title, text:btn.dataset.text||'', url:String(url)};
      try{
        if(navigator.share){ await navigator.share(data); toast('Shared!'); }
        else{ await navigator.clipboard.writeText(String(url)); toast('Link copied'); }
      }catch{}
    });
  });
});
