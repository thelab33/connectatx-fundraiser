(function(){
  // derive shades from --brand (H S L)
  const root = document.documentElement;
  const get = name => getComputedStyle(root).getPropertyValue(name).trim();
  const set = (name, val) => root.style.setProperty(name, val);
  const [h,s,l] = get('--brand').split(' ').map(v=>parseFloat(v));

  function lmod(delta){ return Math.max(0, Math.min(100, l + delta)); }
  set('--accent', `${h} ${s} ${l}%`);
  set('--accent-600', `${h} ${s} ${Math.max(30, l-8)}%`);
  set('--accent-700', `${h} ${s} ${Math.max(26, l-14)}%`);
  set('--accent-glow', `${h} ${s} ${Math.min(90, l+12)}%`);
})();

