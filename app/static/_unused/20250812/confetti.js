export function launchConfetti() {
  const colors = ['#facc15', '#dc2626', '#fff', '#18181b'];
  for (let i = 0; i < 64; i++) {
    const confetti = document.createElement('div');
    confetti.className = 'confetti';
    confetti.style.background = colors[Math.floor(Math.random() * colors.length)];
    confetti.style.left = `${Math.random() * 100}vw`;
    confetti.style.animationDelay = `${Math.random() * 1.5}s`;
    document.body.appendChild(confetti);
    setTimeout(() => confetti.remove(), 1800);
  }
}
