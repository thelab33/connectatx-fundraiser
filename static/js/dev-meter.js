(() => {
  // Only run locally so you don't spoof prod numbers
  if (!['localhost','127.0.0.1'].includes(location.hostname)) return;
  let raised = 0, goal = 10000;
  setInterval(() => {
    raised = Math.min(goal, raised + Math.floor(Math.random()*90 + 30));
    window.dispatchEvent(new CustomEvent('fc:meter:update', { detail: { raised, goal }}));
  }, 1500);
})();
