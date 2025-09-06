const storageKey='fc-theme';
function applyTheme(mode){ document.documentElement.dataset.theme=mode; }
function initBrand(){
  const brand = document.documentElement.dataset.brand; if(brand) document.documentElement.style.setProperty('--brand', brand);
}
addEventListener('DOMContentLoaded', ()=>{
  initBrand();
  let saved = localStorage.getItem(storageKey);
  if(!saved){ saved = matchMedia('(prefers-color-scheme: dark)').matches ? 'dark':'light'; }
  applyTheme(saved);
  // Enable toggles if present
  document.querySelectorAll('[data-toggle-theme]').forEach(btn=>{
    btn.addEventListener('click', ()=>{
      const next = (document.documentElement.dataset.theme==='dark')?'light':'dark';
      localStorage.setItem(storageKey,next); applyTheme(next);
    });
  });
});
