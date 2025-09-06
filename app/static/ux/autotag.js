addEventListener('DOMContentLoaded', ()=>{
  const hasEliteHeader = !!document.querySelector('.site-header');

  // 1) CTA pulse on donate/sponsor/share buttons (always ok)
  [...document.querySelectorAll('a,button,[role="button"]')].forEach(el=>{
    const t=(el.textContent||'').toLowerCase();
    if(/donate|sponsor|become|share/.test(t)){ el.dataset.tierCta='1'; el.classList.add('cta-pulse'); }
  });

  // 2) Progress parse ($X / $Y) for badges + favicon (always ok)
  const m = (document.body.textContent||'').match(/\$?\s*([\d,]+)\s*\/\s*\$?\s*([\d,]+)/);
  if(m){
    const cur = +m[1].replace(/,/g,''), goal = +m[2].replace(/,/g,'');
    const host = document.querySelector('[data-progress]') || document.querySelector('[data-goal-host]') || document.body;
    host.setAttribute('data-progress',cur); host.setAttribute('data-goal',goal);
    (host.querySelector('[data-milestones]') || host.appendChild(Object.assign(document.createElement('div'),{dataset:{milestones:''}})));
  }

  // 3) DO NOT add bars if header is present (prevents duplicates)
  if(hasEliteHeader) return;

  // (Fallback only) light-touch glow on first hero/card
  const hero = document.querySelector('[data-glass], [class*="hero"], section, main > *');
  if(hero && !hero.hasAttribute('data-glass')){ hero.setAttribute('data-glass',''); hero.classList.add('glass2','ambient-glow'); }

  // (Fallback only) simple announcement + ticker
  if(!document.querySelector('[data-announcement]')){
    const bar=document.createElement('div'); bar.setAttribute('data-announcement',''); bar.dataset.title='Real-time shoutouts';
    bar.dataset.text='Thanks for fueling the season!'; document.body.prepend(bar);
  }
  if(!document.querySelector('[data-donor-ticker]')){
    const t = document.createElement('div'); t.className='ticker glass2'; t.setAttribute('data-donor-ticker',''); t.dataset.speed='50';
    t.innerHTML='<div class="ticker__track"><span class="ticker__item">🌟 Live supporters welcome</span><span class="ticker__item">👏 Share to boost reach</span></div>';
    document.body.insertBefore(t, document.body.children[1]);
  }
});
