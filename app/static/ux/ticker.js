addEventListener('DOMContentLoaded', ()=>{
  document.querySelectorAll('[data-donor-ticker]').forEach(root=>{
    const track = root.querySelector('.ticker__track') || root.appendChild(Object.assign(document.createElement('div'),{className:'ticker__track'}));
    let items = [...root.querySelectorAll('.ticker__item')]; if(!items.length) return;
    // duplicate for seamless loop
    items.concat(items.map(n=>n.cloneNode(true))).forEach(n=>track.appendChild(n));
    let x=0, speed = +(root.dataset.speed||40); let raf;
    const step = (t)=>{ x -= (speed/60); if(Math.abs(x) > (items[0].offsetWidth+32)) x=0; track.style.transform=`translateX(${x}px)`; raf=requestAnimationFrame(step) };
    const start = ()=>raf|| (raf=requestAnimationFrame(step)); const stop = ()=>{cancelAnimationFrame(raf); raf=0}
    root.addEventListener('mouseenter', stop); root.addEventListener('mouseleave', start); start();
  });
});
