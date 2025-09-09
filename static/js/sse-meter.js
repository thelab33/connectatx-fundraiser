(() => {
  try{
    const es = new EventSource('http://localhost:5055/dev/sse');
    es.onmessage = (e) => { try{
      const d = JSON.parse(e.data||'{}');
      window.dispatchEvent(new CustomEvent('fc:meter:update', { detail:d }));
    }catch{} };
    addEventListener('pagehide', ()=>es.close(), {once:true});
  }catch{}
})();
