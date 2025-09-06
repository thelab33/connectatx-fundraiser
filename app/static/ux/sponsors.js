addEventListener('DOMContentLoaded', ()=>{
  document.querySelectorAll('[data-sponsors]').forEach(grid=>{
    grid.classList.add('sponsor-grid');
    const items = [...grid.querySelectorAll('[data-sponsor]')];
    items.sort((a,b)=>+(b.dataset.weight||1)-+(a.dataset.weight||1)).forEach(n=>grid.appendChild(n));
    items.forEach(i=>i.classList.add('sponsor'));
  });
});
