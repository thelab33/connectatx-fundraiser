#!/usr/bin/env python3
"""
forge_prestige_patch2.py — SV-Elite Partial Upgrader (Non-Overlay Sweep)
- Auto-updates ALL non-overlay partials with SaaS-ready markup
- Creates timestamped backups for rollback
"""

import shutil, time
from pathlib import Path

PARTIALS_DIR = Path("app/templates/partials")

PATCHES = {
    "program_pulse.html": """{# =====================================================================
   FundChamps — Program Pulse (SV-Elite)
   ===================================================================== #}
<section id="program-pulse" class="relative z-10 bg-zinc-950 text-white py-16">
  <div class="max-w-6xl mx-auto px-4">
    <h2 class="text-3xl font-bold mb-6 text-center">Program Pulse</h2>
    <p class="opacity-70 mb-6 text-center">Keep track of our latest games, stats, and upcoming events.</p>
    <div class="overflow-x-auto">
      <table class="min-w-full text-sm text-left bg-zinc-900 rounded-xl">
        <thead class="bg-zinc-800 text-xs uppercase">
          <tr>
            <th scope="col" class="px-4 py-2">Date</th>
            <th scope="col" class="px-4 py-2">Opponent</th>
            <th scope="col" class="px-4 py-2">Result</th>
            <th scope="col" class="px-4 py-2">Location</th>
          </tr>
        </thead>
        <tbody>
          <tr class="border-t border-zinc-700">
            <td class="px-4 py-2">Aug 20</td>
            <td class="px-4 py-2">Rivals Elite</td>
            <td class="px-4 py-2 text-green-400">W 78-65</td>
            <td class="px-4 py-2">Austin, TX</td>
          </tr>
          <tr class="border-t border-zinc-700">
            <td class="px-4 py-2">Aug 27</td>
            <td class="px-4 py-2">Houston Stars</td>
            <td class="px-4 py-2 text-red-400">L 71-75</td>
            <td class="px-4 py-2">Houston, TX</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</section>
""",

    "impact_lockers.html": """{# =====================================================================
   FundChamps — Impact Lockers (SV-Elite)
   ===================================================================== #}
<section id="impact-lockers" class="relative z-10 bg-black text-white py-16">
  <div class="max-w-6xl mx-auto px-4">
    <h2 class="text-3xl font-bold text-center mb-10">Impact Lockers</h2>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="bg-zinc-900 rounded-xl p-6 text-center shadow-lg">
        <h3 class="text-xl font-semibold mb-2">Travel</h3>
        <p class="opacity-70">Cover tournament travel costs for our athletes.</p>
      </div>
      <div class="bg-zinc-900 rounded-xl p-6 text-center shadow-lg">
        <h3 class="text-xl font-semibold mb-2">Gear</h3>
        <p class="opacity-70">Ensure players have uniforms, shoes, and training equipment.</p>
      </div>
      <div class="bg-zinc-900 rounded-xl p-6 text-center shadow-lg">
        <h3 class="text-xl font-semibold mb-2">Academics</h3>
        <p class="opacity-70">Support tutoring and academic programs alongside athletics.</p>
      </div>
    </div>
  </div>
</section>
""",

    "funds_allocation.html": """{# =====================================================================
   FundChamps — Funds Allocation (SV-Elite)
   ===================================================================== #}
<section id="funds-allocation" class="relative z-10 bg-zinc-950 text-white py-16">
  <div class="max-w-5xl mx-auto px-4 text-center">
    <h2 class="text-3xl font-bold mb-6">Funds Allocation</h2>
    <p class="opacity-70 mb-8">Every dollar raised is allocated with transparency.</p>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="p-6 bg-zinc-900 rounded-xl">
        <h3 class="font-semibold">40% Travel</h3>
      </div>
      <div class="p-6 bg-zinc-900 rounded-xl">
        <h3 class="font-semibold">35% Gear</h3>
      </div>
      <div class="p-6 bg-zinc-900 rounded-xl">
        <h3 class="font-semibold">25% Academics</h3>
      </div>
    </div>
  </div>
</section>
""",

    "testimonials.html": """{# =====================================================================
   FundChamps — Testimonials (SV-Elite)
   ===================================================================== #}
<section id="testimonials" class="relative z-10 bg-black text-white py-16">
  <div class="max-w-6xl mx-auto px-4 text-center">
    <h2 class="text-3xl font-bold mb-8">What People Are Saying</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
      <blockquote class="p-6 bg-zinc-900 rounded-xl">
        <p class="italic opacity-80">"Supporting Connect ATX Elite has been incredible. Watching the kids grow on and off the court is inspiring."</p>
        <footer class="mt-4 font-semibold">– Jane D.</footer>
      </blockquote>
      <blockquote class="p-6 bg-zinc-900 rounded-xl">
        <p class="italic opacity-80">"This program truly invests in our youth’s future. Proud to be a sponsor!"</p>
        <footer class="mt-4 font-semibold">– Acme Corp</footer>
      </blockquote>
    </div>
  </div>
</section>
""",

    "newsletter.html": """{# =====================================================================
   FundChamps — Newsletter Signup (SV-Elite)
   ===================================================================== #}
<section id="newsletter" class="relative z-10 bg-zinc-950 text-white py-16">
  <div class="max-w-xl mx-auto text-center px-4">
    <h2 class="text-3xl font-bold mb-4">Stay Connected</h2>
    <p class="opacity-70 mb-6">Sign up for team news, game results, and exclusive updates.</p>
    <form action="#" method="post" class="flex flex-col sm:flex-row gap-3">
      <label for="newsletter-email" class="sr-only">Email</label>
      <input id="newsletter-email" type="email" name="email" required class="flex-1 rounded-lg px-4 py-2 text-black" placeholder="Enter your email">
      <button type="submit" class="px-5 py-2 bg-[color:var(--fc-brand)] text-black rounded-lg">Subscribe</button>
    </form>
  </div>
</section>
"""
}

def patch_file(filename, new_content):
    path = PARTIALS_DIR / filename
    if not path.exists():
        print(f"❌ {filename} not found, skipping.")
        return
    backup = path.with_suffix(path.suffix + f".bak-" + time.strftime("%Y%m%d-%H%M%S"))
    shutil.copy2(path, backup)
    path.write_text(new_content, encoding="utf-8")
    print(f"✅ Patched {filename} (backup: {backup.name})")

if __name__ == "__main__":
    for fn, content in PATCHES.items():
        patch_file(fn, content)
    print("\n🎉 Non-overlay partials upgraded to SV-Elite.")
    print("↩ To rollback: copy .bak file back into place.")

