function mount(container, pct){
  const milestones = [25,50,75,100];
  container.classList.add('badges');
  milestones.forEach(m=>{
    const b=document.createElement('span'); b.className='badge'; b.dataset.hit = (pct>=m);
    b.innerHTML = (pct>=m? '🏅':'🔘') + ' ' + m + '%';
    container.appendChild(b);
  });
}
addEventListener('DOMContentLoaded', ()=>{
  document.querySelectorAll('[data-progress][data-goal]').forEach(el=>{
    const current=+el.dataset.progress||0, goal=+el.dataset.goal||1, pct = Math.floor((current/goal)*100);
    const target = el.querySelector('[data-milestones]') || el; mount(target, pct);
  });
});
