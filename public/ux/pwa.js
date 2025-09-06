if('serviceWorker' in navigator){
  window.addEventListener('load', ()=>navigator.serviceWorker.register('/ux/sw.js').catch(()=>{}));
}
