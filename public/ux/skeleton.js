addEventListener('DOMContentLoaded', ()=>{
  document.querySelectorAll('[data-skeleton]').forEach(n=>{
    const clear=()=>n.removeAttribute('data-skeleton');
    n.dataset.skelAuto==='off' ? 0 : setTimeout(clear, 1200);
  });
});
