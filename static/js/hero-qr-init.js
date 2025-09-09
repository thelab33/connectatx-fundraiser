(() => {
  const el = document.getElementById('qr-canvas');
  if (!el) return;
  const url = (location.origin || '') + '/donate?utm_source=qr&utm_medium=hero&utm_campaign=fundraiser';
  if (window.QRCode && typeof window.QRCode.toCanvas === 'function') {
    window.QRCode.toCanvas(el, url, { margin: 1, width: 160 }, (err) => { if (err) console.error(err); });
  } else { // graceful fallback to PNG
    const img=new Image(); img.alt='Donate QR'; img.width=160; img.height=160; img.style.borderRadius='12px';
    img.src='/static/images/qr/hero-donate.png'; el.replaceWith(img);
  }
})();
