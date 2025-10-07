(() => {
  const qrBox = document.getElementById('qr-box');
  const link  = document.getElementById('qr-fallback-link');
  if (!qrBox || !link) return;

  const BASE = link.getAttribute('href') || '/donate';
  const peer = (()=>{ try{
    const qs=new URLSearchParams(location.search);
    if (qs.get('peer')) return qs.get('peer');
    const raw=localStorage.getItem('fc_ref_ctx'); if(!raw) return null;
    const ctx=JSON.parse(raw)||{}; return ctx.data?.peer_slug || ctx.data?.peer || null;
  }catch{return null;} })();

  const u = new URL(BASE, location.origin);
  u.searchParams.set('utm_source','qr');
  u.searchParams.set('utm_medium','hero');
  u.searchParams.set('utm_campaign','fundraiser');
  if (peer) u.searchParams.set('peer', peer);
  const href = u.toString();
  link.href = href;

  function renderWithSoldair() {
    const c = document.createElement('canvas');
    try {
      window.QRCode.toCanvas(c, href, {margin:1, width:128}, (err)=>{
        if (err) return;
        qrBox.innerHTML = ""; qrBox.appendChild(c);
      });
      return true;
    } catch { return false; }
  }
  function renderWithConstructor() {
    try {
      qrBox.innerHTML="";
      new window.QRCode(qrBox, { text: href, width: 128, height: 128, correctLevel: (window.QRCode.CorrectLevel||{}).M || 0 });
      return true;
    } catch { return false; }
  }
  if (window.QRCode && (window.QRCode.toCanvas ? renderWithSoldair() : renderWithConstructor())) return;
  // Fallback: show the URL as text so it’s still usable
  qrBox.textContent = href; qrBox.style.fontSize='.72rem'; qrBox.style.wordBreak='break-all';
})();
