const quotes = [
  {
    text: 'The brotherhood and discipline we build here creates leaders for life.',
    author: 'Coach A. Rodriguez',
    title: 'Program Director',
    avatar: '/static/images/coach-avatar.jpg',
  },
  {
    text: 'We’re not just coaching basketball. We’re shaping futures.',
    author: 'Coach Jasmine',
    title: 'Academic Coordinator',
    avatar: '/static/images/coach2.jpg',
  },
  {
    text: 'This team changed my life — it gave me purpose, focus, and family.',
    author: 'Jordan M.',
    title: 'Alumni Captain',
    avatar: '/static/images/player1.jpg',
  },
];
let currentQuoteIndex = 0;
function showQuote(i) {
  const q = quotes[i];
  document.getElementById('hero-quote-text').innerText = q.text;
  document.getElementById('hero-quote-author').innerText = q.author;
  document.getElementById('hero-quote-title').innerText = q.title;
  document.getElementById('hero-quote-avatar').src = q.avatar;
}
function showNextQuote() {
  currentQuoteIndex = (currentQuoteIndex + 1) % quotes.length;
  showQuote(currentQuoteIndex);
}
function showPrevQuote() {
  currentQuoteIndex = (currentQuoteIndex - 1 + quotes.length) % quotes.length;
  showQuote(currentQuoteIndex);
}
function copyQuote() {
  const q = quotes[currentQuoteIndex];
  navigator.clipboard.writeText(`"${q.text}" — ${q.author}, ${q.title}`);
  alert('Quote copied!');
}
function shareQuote() {
  const q = quotes[currentQuoteIndex];
  if (navigator.share)
    navigator.share({
      title: 'Connect ATX Elite',
      text: `"${q.text}" — ${q.author}`,
    });
  else alert('Share not supported.');
}
document.addEventListener('DOMContentLoaded', () => showQuote(0));
