#!/bin/bash
echo "⚙️  Injecting Tailwind polish into hero..."

sed -i '/class="hero-sub"/s/"/ mb-3 max-w-prose text-lg md:text-base leading-snug"/' templates/components/hero.html
sed -i '/data-test="donate-primary"/s/"/ hover:shadow-[0_0_24px_rgba(250,204,21,.4)]"/' templates/components/hero.html
sed -i '/class="qr-wrap"/s/"/ hidden sm:grid"/' templates/components/hero.html
sed -i '/class="btn btn-gold sheen donate-now"/s/"/ animate-\[glowPulse_6s_ease-in-out_infinite\]"/' templates/components/hero.html
sed -i '/backdrop-filter: blur(16px)/s/blur(16px)/blur(20px)/' src/styles/tailwind-entry.css
sed -i '/class="title-block"/s/"/ gap-y-3"/' templates/components/hero.html
sed -i '/class="mobile-sticky-cta"/s/"/ shadow-lg ring-2 ring-offset-2 ring-yellow-400"/' templates/components/hero.html

echo "✅ Hero section Tailwind polish complete."
