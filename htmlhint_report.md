
   Config loaded: .htmlhintrc

   /home/cyberboyz/connectatx-fundraiser/app/templates/base.html
[37m      L10 |[90m  <meta name="viewport"content="width=device-width, initial-scale=1, maximum-scale=5, viewport-fit=co...[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L10 |[90m...1, maximum-scale=5, viewport-fit=cover"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L11 |[90m  <meta name="robots"content="index,follow,max-image-preview:large"/>[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L11 |[90m...="index,follow,max-image-preview:large"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L12 |[90m  <meta name="color-scheme"content="dark light"/>[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L12 |[90m...name="color-scheme"content="dark light"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L13 |[90m  <meta name="theme-color"content="{{ team.theme_color|default('#facc15', true) }}"/>[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L13 |[90m...heme_color|default('#facc15', true) }}"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L14 |[90m  <meta http-equiv="X-UA-Compatible"content="IE=edge"/>[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L14 |[90m...quiv="X-UA-Compatible"content="IE=edge"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L15 |[90m  <link rel="canonical"href="{{ request.url_root|trim('/') }}"/>[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L15 |[90m...href="{{ request.url_root|trim('/') }}"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L16 |[90m  <link rel="manifest"href="{{ url_for('static', filename='manifest.webmanifest', v=asset_version) }}...[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L16 |[90m...fest.webmanifest', v=asset_version) }}"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L19 |[90m  <meta name="description"content="{{ team.meta_description|default('Connect ATX Elite — Family-run A...[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L19 |[90m...ure leaders in East Austin.', true) }}"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L24 |[90m  <meta property="og:type"content="website"/>[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L24 |[90m...eta property="og:type"content="website"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L25 |[90m  <meta property="og:title"content="{{ team.og_title|default('Connect ATX Elite | Empowering Youth', ...[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L25 |[90m...TX Elite | Empowering Youth', true) }}"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L26 |[90m  <meta property="og:description"content="{{ team.og_description|default('Support our basketball jour...[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L26 |[90m...next generation of leaders.', true) }}"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L27 |[90m  <meta property="og:image"content="{{ ogimg }}"/>[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L27 |[90m...roperty="og:image"content="{{ ogimg }}"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L28 |[90m  <meta property="og:url"content="{{ request.url }}"/>[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L28 |[90m...rty="og:url"content="{{ request.url }}"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L29 |[90m  <meta property="og:site_name"content="{{ team.team_name|default('Connect ATX Elite', true) }}"/>[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L29 |[90m...|default('Connect ATX Elite', true) }}"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L30 |[90m  <meta property="og:image:alt"content="{{ team.og_alt|default(team.og_title|default('Connect ATX Eli...[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L30 |[90m...t('Connect ATX Elite', true), true) }}"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L31 |[90m  <meta name="twitter:card"content="summary_large_image"/>[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L31 |[90m...tter:card"content="summary_large_image"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L32 |[90m  <meta name="twitter:site"content="{{ team.twitter_handle|default('@ConnectATXElite', true) }}"/>[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L32 |[90m...e|default('@ConnectATXElite', true) }}"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L33 |[90m  <meta name="twitter:title"content="{{ team.og_title|default('Connect ATX Elite | Empowering Youth',...[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L33 |[90m...TX Elite | Empowering Youth', true) }}"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L34 |[90m  <meta name="twitter:description"content="{{ team.og_description|default('Support our basketball jou...[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L34 |[90m...next generation of leaders.', true) }}"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L35 |[90m  <meta name="twitter:image"content="{{ ogimg }}"/>[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L35 |[90m...me="twitter:image"content="{{ ogimg }}"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L38 |[90m  <link rel="icon"type="image/png"sizes="32x32"href="{{ (team and team.favicon) and url_for('static',...[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L38 |[90m...ages/favicon.png', v=asset_version) }}"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L39 |[90m  <link rel="apple-touch-icon"href="{{ (team and team.apple_icon) and url_for('static', filename=team...[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L39 |[90m...images/logo.avif', v=asset_version) }}"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L40 |[90m  <meta name="apple-mobile-web-app-capable"content="yes"/>[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L40 |[90m...le-mobile-web-app-capable"content="yes"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L41 |[90m  <meta name="apple-mobile-web-app-status-bar-style"content="black-translucent"/>[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L41 |[90m...s-bar-style"content="black-translucent"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L44 |[90m  <link rel="preconnect"href="https://fonts.googleapis.com"crossorigin />[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L44 |[90m...tps://fonts.googleapis.com"crossorigin />[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L45 |[90m  <link rel="preconnect"href="https://fonts.gstatic.com"crossorigin />[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L45 |[90m..."https://fonts.gstatic.com"crossorigin />[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L46 |[90m  <link rel="preconnect"href="https://api.stripe.com"/>[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L46 |[90m...reconnect"href="https://api.stripe.com"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L47 |[90m  <link rel="dns-prefetch"href="https://fonts.googleapis.com"/>[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L47 |[90m...tch"href="https://fonts.googleapis.com"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L48 |[90m  <link rel="dns-prefetch"href="https://api.stripe.com"/>[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L48 |[90m...-prefetch"href="https://api.stripe.com"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L51 |[90m  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap"rel="style...[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L51 |[90m...rel="stylesheet"crossorigin="anonymous"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L52 |[90m  <link rel="preload"href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=sw...[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L52 |[90m...=swap"as="style"crossorigin="anonymous"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L55 |[90m  <link rel="preload"href="{{ url_for('static', filename=team.logo if team and team.logo else 'images...[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L55 |[90m...o.webp') }}"as="image"type="image/webp"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L58 |[90m  <link rel="preload"href="{{ url_for('static', filename='css/tailwind.min.css', v=asset_version) }}"...[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L58 |[90m...in.css', v=asset_version) }}"as="style"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L59 |[90m  <link rel="stylesheet"href="{{ url_for('static', filename='css/tailwind.min.css', v=asset_version) ...[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L59 |[90m...n.css', v=asset_version) }}"media="all"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L61 |[90m    <link rel="stylesheet"href="{{ url_for('static', filename='css/input.css', v=asset_version) }}">[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L61 |[90m...me='css/input.css', v=asset_version) }}">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L64 |[90m    <link rel="stylesheet"href="{{ url_for('static', filename='css/' ~ team.custom_css, v=asset_versi...[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L64 |[90m... ~ team.custom_css, v=asset_version) }}">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L105 |[90m  <a href="#main-content"class="sr-only focus:not-sr-only absolute top-2 left-2 bg-yellow-400 text-bl...[39m
[37m              ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L105 |[90m...d px-3 py-1 rounded-lg z-50"tabindex="0">Skip to main content</a>[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L105 |[90m...g z-50"tabindex="0">Skip to main content</a>[39m
[37m                                                       ^ [31mTag must be paired, no start tag: [ </a> ] (tag-pair)[39m
[37m      L108 |[90m  <button id="dark-mode-toggle"aria-label="Toggle dark mode"[39m
[37m              ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L110 |[90m  >[39m
[37m              ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L111 |[90m    <span aria-hidden="true"class="block text-lg">🌙</span>[39m
[37m                ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L111 |[90m... aria-hidden="true"class="block text-lg">🌙</span>[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L111 |[90m...ia-hidden="true"class="block text-lg">🌙</span>[39m
[37m                                                         ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L113 |[90m  </button>[39m
[37m              ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L116 |[90m  <div id="page-loader"[39m
[37m              ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L119 |[90m  >[39m
[37m              ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L120 |[90m    <svg class="animate-spin h-12 w-12 text-yellow-400"xmlns="http://www.w3.org/2000/svg"fill="none"v...[39m
[37m                ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L120 |[90m.../2000/svg"fill="none"viewBox="0 0 24 24">[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L121 |[90m      <circle class="opacity-25"cx="12"cy="12"r="10"stroke="currentColor"stroke-width="4"/>[39m
[37m                  ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L121 |[90m...0"stroke="currentColor"stroke-width="4"/>[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L122 |[90m      <path class="opacity-75"fill="currentColor"d="M4 12a8 8 0 018-8v8z"/>[39m
[37m                  ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L122 |[90m...="currentColor"d="M4 12a8 8 0 018-8v8z"/>[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L123 |[90m    </svg>[39m
[37m                ^ [31mTag must be paired, no start tag: [ </svg> ] (tag-pair)[39m
[37m      L124 |[90m  </div>[39m
[37m              ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L154 |[90m  <script src="{{ url_for('static', filename='js/main.js', v=asset_version) }}"defer></script>[39m
[37m              ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L154 |[90m...='js/main.js', v=asset_version) }}"defer></script>[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L154 |[90m...'js/main.js', v=asset_version) }}"defer></script>[39m
[37m                                                       ^ [31mTag must be paired, no start tag: [ </script> ] (tag-pair)[39m

   /home/cyberboyz/connectatx-fundraiser/app/templates/index.html
[37m      L13 |[90m  <main class="flex flex-col gap-20 max-w-6xl mx-auto w-full px-4 sm:px-8"role="main"tabindex="-1">[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L13 |[90m...ll px-4 sm:px-8"role="main"tabindex="-1">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L1 |[90m{% extends "base.html"%}[39m
[37m          ^ [31mDoctype must be declared before any non-comment content. (doctype-first)[39m
[37m      L36 |[90m        <h2 id="{{ section.id }}-heading"class="sr-only">{{ section.label }}</h2>[39m
[37m                   ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L36 |[90m...{{ section.id }}-heading"class="sr-only">{{ section.label }}</h2>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L36 |[90m...ding"class="sr-only">{{ section.label }}</h2>[39m
[37m                                                      ^ [31mTag must be paired, no start tag: [ </h2> ] (tag-pair)[39m
[37m      L48 |[90m      <div id="admin-onboarding"class="relative z-40">[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L48 |[90m...="admin-onboarding"class="relative z-40">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L50 |[90m      </div>[39m
[37m                 ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L52 |[90m  </main>[39m
[37m             ^ [31mTag must be paired, no start tag: [ </main> ] (tag-pair)[39m

   /home/cyberboyz/connectatx-fundraiser/app/templates/admin/base.html
[37m      L1 |[90m{% extends "base.html"%}[39m
[37m          ^ [31mDoctype must be declared before any non-comment content. (doctype-first)[39m

   /home/cyberboyz/connectatx-fundraiser/app/templates/admin/dashboard.html
[37m      L1 |[90m{% extends "admin_base.html"%}[39m
[37m          ^ [31mDoctype must be declared before any non-comment content. (doctype-first)[39m
[37m      L83 |[90m            <form action="{{ url_for('admin.approve_sponsor', sponsor_id=s.id) }}"method="POST"style=...[39m
[37m                       ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L83 |[90m... }}"method="POST"style="display: inline">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L84 |[90m              <button type="submit"class="bg-gold text-zinc-900 px-3 py-1 rounded hover:bg-yellow-300...[39m
[37m                         ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L84 |[90m...0 px-3 py-1 rounded hover:bg-yellow-300">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L86 |[90m              </button>[39m
[37m                         ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L87 |[90m            </form>[39m
[37m                       ^ [31mTag must be paired, no start tag: [ </form> ] (tag-pair)[39m
[37m      L93 |[90m          <td colspan="6"class="py-8 text-center text-zinc-400">No sponsors found.</td>[39m
[37m                     ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L93 |[90m...6"class="py-8 text-center text-zinc-400">No sponsors found.</td>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L93 |[90m...center text-zinc-400">No sponsors found.</td>[39m
[37m                                                      ^ [31mTag must be paired, no start tag: [ </td> ] (tag-pair)[39m
[37m      L124 |[90m          <td colspan="4"class="py-8 text-center text-zinc-400">No transactions yet.</td>[39m
[37m                      ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L124 |[90m...4"class="py-8 text-center text-zinc-400">No transactions yet.</td>[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L124 |[90m...nter text-zinc-400">No transactions yet.</td>[39m
[37m                                                       ^ [31mTag must be paired, no start tag: [ </td> ] (tag-pair)[39m

   /home/cyberboyz/connectatx-fundraiser/app/templates/admin/sponsors.html
[37m      L1 |[90m{% extends "admin/base.html"%}[39m
[37m          ^ [31mDoctype must be declared before any non-comment content. (doctype-first)[39m
[37m      L74 |[90m        <td colspan="6"class="py-8 text-center text-zinc-400">[39m
[37m                   ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L74 |[90m...6"class="py-8 text-center text-zinc-400">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L76 |[90m        </td>[39m
[37m                   ^ [31mTag must be paired, no start tag: [ </td> ] (tag-pair)[39m

   /home/cyberboyz/connectatx-fundraiser/app/templates/macros/confetti.html
[37m      L1 |[90m{# macros/confetti.html #}[39m
[37m          ^ [31mDoctype must be declared before any non-comment content. (doctype-first)[39m

   /home/cyberboyz/connectatx-fundraiser/app/templates/macros/progress.html
[37m      L7 |[90m  {%- set _pct = (_pct if _pct >= 0.0 else 0.0) -%}[39m
[37m                                         ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L8 |[90m  {%- set _pct = (_pct if _pct <= 100.0 else 100.0) -%}[39m
[37m                                         ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L1 |[90m{# macros/progress.html — Defines the progress_meter macro #}[39m
[37m          ^ [31mDoctype must be declared before any non-comment content. (doctype-first)[39m
[37m      L43 |[90m    <div class="w-full bg-zinc-800/70 rounded-full overflow-hidden shadow-inner"style="height: inheri...[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L43 |[90m...en shadow-inner"style="height: inherit;">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L52 |[90m    <div class="absolute inset-0 flex items-center justify-center font-bold leading-none pointer-even...[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L52 |[90m...-events-none"style="font-size: inherit;">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L56 |[90m    </div>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L57 |[90m  </div>[39m
[37m             ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m

   /home/cyberboyz/connectatx-fundraiser/app/templates/macros/sponsor_card.html
[37m      L1 |[90m{# ==============================[39m
[37m          ^ [31mDoctype must be declared before any non-comment content. (doctype-first)[39m
[37m      L21 |[90m    <h2 id="sponsor-wall-title"class="text-2xl sm:text-3xl font-black tracking-tight bg-gradient-to-r...[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L21 |[90m... drop-shadow-lg flex items-center gap-2">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L23 |[90m    </h2>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </h2> ] (tag-pair)[39m
[37m      L24 |[90m    <button id="sponsor-wall-close"aria-label="Close sponsor wall"[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L25 |[90m...hover:bg-yellow-400/20 backdrop-blur-sm">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L27 |[90m    </button>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L31 |[90m  <div id="donation-ticker"class="w-full py-1 px-4 bg-yellow-400/10 text-yellow-300 text-xs font-mono...[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L31 |[90m...ow-x-auto border-b border-yellow-400/15">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L37 |[90m  </div>[39m
[37m             ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L57 |[90m    <button type="button"class="leaderboard-toggle text-xs sm:text-sm font-bold py-1 px-3 rounded bg-...[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L58 |[90m      data-type="all">All-Time</button>[39m
[37m                                ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L58 |[90m      data-type="all">All-Time</button>[39m
[37m                                         ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L59 |[90m    <button type="button"class="leaderboard-toggle text-xs sm:text-sm font-bold py-1 px-3 rounded bg-...[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L60 |[90m      data-type="month">This Month</button>[39m
[37m                                  ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L60 |[90m      data-type="month">This Month</button>[39m
[37m                                             ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L71 |[90m  <div id="sponsor-wall-list"[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L73 |[90m...st"tabindex="0"aria-label="Sponsor List">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L78 |[90m...orted|length) if sponsors_sorted|length < 12 else 0 %}[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L88 |[90m        <span class="text-3xl mb-1 animate-bounce select-none"aria-hidden="true">✨</span>[39m
[37m                   ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L88 |[90m...te-bounce select-none"aria-hidden="true">✨</span>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L88 |[90m...-bounce select-none"aria-hidden="true">✨</span>[39m
[37m                                                       ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L91 |[90m        <button type="button"class="rounded-full bg-yellow-400 px-5 py-2 font-black text-black shadow...[39m
[37m                   ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L91 |[90m...ia-label="Become a Sponsor"tabindex="-1">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L93 |[90m        </button>[39m
[37m                   ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L96 |[90m  </div>[39m
[37m             ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L100 |[90m    <button type="button"onclick="openSponsorModal()"[39m
[37m                ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L102 |[90m      aria-label="Become a Sponsor">[39m
[37m                                               ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L104 |[90m    </button>[39m
[37m                ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L107 |[90m      <button onclick="shareSponsorWall('x')"aria-label="Share on X"class="p-2 rounded-full bg-zinc-8...[39m
[37m                  ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L107 |[90m... text-yellow-400 hover:bg-yellow-500/30">[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L108 |[90m        <svg viewBox="0 0 24 24"width="20"height="20"><!-- X icon --></svg>[39m
[37m                    ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L108 |[90m...viewBox="0 0 24 24"width="20"height="20"><!-- X icon --></svg>[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L108 |[90m...24"width="20"height="20"><!-- X icon --></svg>[39m
[37m                                                       ^ [31mTag must be paired, no start tag: [ </svg> ] (tag-pair)[39m
[37m      L109 |[90m      </button>[39m
[37m                  ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L110 |[90m      <button onclick="shareSponsorWall('fb')"aria-label="Share on Facebook"class="p-2 rounded-full b...[39m
[37m                  ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L110 |[90m...-800 text-blue-500 hover:bg-blue-400/30">[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L111 |[90m        <svg viewBox="0 0 24 24"width="20"height="20"><!-- FB icon --></svg>[39m
[37m                    ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L111 |[90m...viewBox="0 0 24 24"width="20"height="20"><!-- FB icon --></svg>[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L111 |[90m...4"width="20"height="20"><!-- FB icon --></svg>[39m
[37m                                                       ^ [31mTag must be paired, no start tag: [ </svg> ] (tag-pair)[39m
[37m      L112 |[90m      </button>[39m
[37m                  ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L113 |[90m      <button onclick="shareSponsorWall('ln')"aria-label="Share on LinkedIn"class="p-2 rounded-full b...[39m
[37m                  ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L113 |[90m...-800 text-blue-700 hover:bg-blue-600/30">[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L114 |[90m        <svg viewBox="0 0 24 24"width="20"height="20"><!-- LinkedIn icon --></svg>[39m
[37m                    ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L114 |[90m...viewBox="0 0 24 24"width="20"height="20"><!-- LinkedIn icon --></svg>[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L114 |[90m...h="20"height="20"><!-- LinkedIn icon --></svg>[39m
[37m                                                       ^ [31mTag must be paired, no start tag: [ </svg> ] (tag-pair)[39m
[37m      L115 |[90m      </button>[39m
[37m                  ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L128 |[90m  <span id="sponsor-nudge-dot"class="absolute top-2 right-2 w-2 h-2 rounded-full bg-pink-500 animate-...[39m
[37m              ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L128 |[90m...d-full bg-pink-500 animate-pulse hidden"></span>[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L128 |[90m...-full bg-pink-500 animate-pulse hidden"></span>[39m
[37m                                                       ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m

   /home/cyberboyz/connectatx-fundraiser/app/templates/macros/ui.html
[37m      L16 |[90m  {%- set _pct = (_pct if _pct >= 0.0 else 0.0) | min(100.0) -%}[39m
[37m                                          ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L26 |[90m  <div[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L33 |[90m        if (this.pct >= 100) {[39m
[37m                                ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L35 |[90m            .then(m => m.default({ particleCount: 120, origin: { y: 0.8 } }))[39m
[37m                                ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L36 |[90m            .catch(() => {});[39m
[37m                                  ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L53 |[90m  >[39m
[37m             ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L54 |[90m    <div class="w-full bg-zinc-800/80 rounded-full overflow-hidden shadow-inner"style="height: inheri...[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L54 |[90m...en shadow-inner"style="height: inherit;">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L1 |[90m{# ===========================================================================[39m
[37m          ^ [31mDoctype must be declared before any non-comment content. (doctype-first)[39m
[37m      L60 |[90m    </div>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L61 |[90m    <div class="absolute inset-0 flex items-center justify-center font-bold leading-none pointer-even...[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L61 |[90m...-events-none"style="font-size: inherit;">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L65 |[90m    </div>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L66 |[90m  </div>[39m
[37m             ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L108 |[90m  <a[39m
[37m              ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L126 |[90m  >[39m
[37m              ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L133 |[90m      <span class="mr-2 inline-flex items-center"aria-hidden="true">[39m
[37m                  ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L133 |[90m...ine-flex items-center"aria-hidden="true">[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L139 |[90m      </span>[39m
[37m                  ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L142 |[90m  </a>[39m
[37m              ^ [31mTag must be paired, no start tag: [ </a> ] (tag-pair)[39m

   /home/cyberboyz/connectatx-fundraiser/app/templates/partials/about_section.html
[37m      L23 |[90m<section[39m
[37m           ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L29 |[90m>[39m
[37m           ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L30 |[90m  <meta itemprop="name"content="player_team"/>[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L30 |[90m...ta itemprop="name"content="player_team"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L31 |[90m  <meta itemprop="areaServed"content="team_region"/>[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L31 |[90m...mprop="areaServed"content="team_region"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L32 |[90m  <meta itemprop="memberOf"content="team_league"/>[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L32 |[90m...temprop="memberOf"content="team_league"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L1 |[90m from "macros/ui.html"import render_button[39m
[37m          ^ [31mDoctype must be declared before any non-comment content. (doctype-first)[39m
[37m      L35 |[90m  <img src="img_src"alt="REVIEW_ME"aria-hidden="true"[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L36 |[90m...  class="loading="lazy"decoding="async"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L37 |[90m  <img src="img_src"alt="REVIEW_ME"aria-hidden="true"[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L38 |[90m...  class="loading="lazy"decoding="async"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L40 |[90m  <h2 id="about-main-heading"[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L42 |[90m      tabindex="0">[39m
[37m                             ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L44 |[90m  </h2>[39m
[37m             ^ [31mTag must be paired, no start tag: [ </h2> ] (tag-pair)[39m
[37m      L46 |[90m  <div class=">[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L46 |[90m  <div class=">[39m
[37m                         ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L48 |[90m    <article class="aria-label="Learn more">      <ul class="aria-label="Team attributes">[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L48 |[90m... <article class="aria-label="Learn more">      <ul class="aria-label="Team attributes">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L48 |[90m...le class="aria-label="Learn more">      <ul class="aria-label="Team attributes">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L48 |[90m... <ul class="aria-label="Team attributes">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L54 |[90m...m — it’s a <span class=">family movement</span> in <span class="> team_region</span> where kids and p...[39m
[37m                                                        ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L64 |[90m      </div>[39m
[37m                 ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L65 |[90m    </article>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </article> ] (tag-pair)[39m
[37m      L68 |[90m    <section class="role="region"aria-label="Testimonials"tabindex="0">[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L68 |[90m...on"aria-label="Testimonials"tabindex="0">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L69 |[90m      <h3 class=">[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L69 |[90m      <h3 class=">[39m
[37m                            ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L71 |[90m      </h3>[39m
[37m                 ^ [31mTag must be paired, no start tag: [ </h3> ] (tag-pair)[39m
[37m      L72 |[90m      <div id="testimonial-carousel"class="aria-live="polite"aria-atomic="true"tabindex="0">[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L72 |[90m...e="polite"aria-atomic="true"tabindex="0">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L73 |[90m        <figure class="aria-label="Testimonial quote and author">[39m
[37m                   ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L73 |[90m...ria-label="Testimonial quote and author">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L74 |[90m          <blockquote id="carousel-quote"class="></blockquote>[39m
[37m                     ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L74 |[90m...  <blockquote id="carousel-quote"class="></blockquote>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L74 |[90m... <blockquote id="carousel-quote"class="></blockquote>[39m
[37m                                                      ^ [31mTag must be paired, no start tag: [ </blockquote> ] (tag-pair)[39m
[37m      L75 |[90m          <figcaption id="carousel-author"class="></figcaption>[39m
[37m                     ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L75 |[90m... <figcaption id="carousel-author"class="></figcaption>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L75 |[90m...<figcaption id="carousel-author"class="></figcaption>[39m
[37m                                                      ^ [31mTag must be paired, no start tag: [ </figcaption> ] (tag-pair)[39m
[37m      L76 |[90m          <img src="rings_img"alt="REVIEW_ME"aria-hidden="true"class="loading="lazy"decoding="async"/...[39m
[37m                     ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L76 |[90m...e"class="loading="lazy"decoding="async"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L77 |[90m        </figure>[39m
[37m                   ^ [31mTag must be paired, no start tag: [ </figure> ] (tag-pair)[39m
[37m      L78 |[90m        <nav class="aria-label="Select testimonial">[39m
[37m                   ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L78 |[90m...v class="aria-label="Select testimonial">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L80 |[90m          <button class="[39m
[37m                     ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L83 |[90m                  type="button"></button>[39m
[37m                                          ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L83 |[90m                  type="button"></button>[39m
[37m                                           ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L85 |[90m        </nav>[39m
[37m                   ^ [31mTag must be paired, no start tag: [ </nav> ] (tag-pair)[39m
[37m      L86 |[90m        <button id="copy-quote"class="aria-label="Copy quote to clipboard"type="button">[39m
[37m                   ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L86 |[90m...l="Copy quote to clipboard"type="button">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L88 |[90m        </button>[39m
[37m                   ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L89 |[90m        <span id="copy-toast"class=">Copied!</span>[39m
[37m                   ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L89 |[90m        <span id="copy-toast"class=">Copied!</span>[39m
[37m                                               ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L90 |[90m      </div>[39m
[37m                 ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L91 |[90m    </section>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </section> ] (tag-pair)[39m
[37m      L92 |[90m  </div>[39m
[37m             ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L93 |[90m</section>[39m
[37m           ^ [31mTag must be paired, no start tag: [ </section> ] (tag-pair)[39m
[37m      L96 |[90m<dialog id="story-modal"[39m
[37m           ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L98 |[90m...="story-title"role="dialog"tabindex="-1">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L99 |[90m  <div id="story-box"[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L101 |[90m       role="document"tabindex="0">[39m
[37m                                              ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L102 |[90m    <button id="story-close"[39m
[37m                ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L104 |[90m...a-label="Close story modal"type="button">×</button>[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L104 |[90m...label="Close story modal"type="button">×</button>[39m
[37m                                                       ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L105 |[90m    <h2 id="story-title"[39m
[37m                ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L106 |[90m        class=">[39m
[37m                           ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L108 |[90m    </h2>[39m
[37m                ^ [31mTag must be paired, no start tag: [ </h2> ] (tag-pair)[39m
[37m      L114 |[90m    <nav class="aria-label="Video sources"role="tablist">[39m
[37m                ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L114 |[90m...aria-label="Video sources"role="tablist">[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L116 |[90m      <button id="tab- t.id"[39m
[37m                  ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L120 |[90m              type="button">[39m
[37m                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L122 |[90m      </button>[39m
[37m                  ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L124 |[90m    </nav>[39m
[37m                ^ [31mTag must be paired, no start tag: [ </nav> ] (tag-pair)[39m
[37m      L126 |[90m    <div id="panel- t.id"[39m
[37m                ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L129 |[90m... aria-labelledby="tab- t.id"tabindex="0">[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L131 |[90m      <video controls preload="none"poster="video_poster"class=">[39m
[37m                  ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L131 |[90m...eload="none"poster="video_poster"class=">[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L132 |[90m        <source src="video_src"type="video/mp4"/>[39m
[37m                    ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L132 |[90m...<source src="video_src"type="video/mp4"/>[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L134 |[90m      </video>[39m
[37m                  ^ [31mTag must be paired, no start tag: [ </video> ] (tag-pair)[39m
[37m      L136 |[90m      <iframe src="kvue_url"class="allowfullscreen loading="lazy"referrerpolicy="no-referrer"></ifram...[39m
[37m                  ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L136 |[90m...ading="lazy"referrerpolicy="no-referrer"></iframe>[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L136 |[90m...ding="lazy"referrerpolicy="no-referrer"></iframe>[39m
[37m                                                       ^ [31mTag must be paired, no start tag: [ </iframe> ] (tag-pair)[39m
[37m      L138 |[90m      <iframe src="https://www.youtube.com/embed/ youtube_id"class="allowfullscreen loading="lazy"ref...[39m
[37m                  ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L138 |[90m...ading="lazy"referrerpolicy="no-referrer"></iframe>[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L138 |[90m...ding="lazy"referrerpolicy="no-referrer"></iframe>[39m
[37m                                                       ^ [31mTag must be paired, no start tag: [ </iframe> ] (tag-pair)[39m
[37m      L140 |[90m    </div>[39m
[37m                ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L142 |[90m    <p class="><strong> player_team</strong> &nbsp;|&nbsp; Family-run · Community-powered · Champions...[39m
[37m                ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L142 |[90m    <p class="><strong> player_team</strong> &nbsp;|&nbsp; Family-run · Community-powered · Champions...[39m
[37m                          ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L142 |[90m...n · Community-powered · Champions rising</p>[39m
[37m                                                       ^ [31mTag must be paired, no start tag: [ </p> ] (tag-pair)[39m
[37m      L143 |[90m  </div>[39m
[37m              ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L144 |[90m</dialog>[39m
[37m            ^ [31mTag must be paired, no start tag: [ </dialog> ] (tag-pair)[39m
[37m      L152 |[90m[39m
[37m            ^ [31mTag must be paired, missing: [ </span></span></strong></li> ], open tag match failed [ <span class=">championship character</span> for life.</span>
      </p>
      <div class="> ] on line 55. (tag-pair)[39m

   /home/cyberboyz/connectatx-fundraiser/app/templates/partials/admin_onboarding_popover.html
[37m      L2 |[90m<div[39m
[37m          ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L16 |[90m>[39m
[37m           ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L17 |[90m  <h3 id="onboard-title-admin"class=">[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L17 |[90m  <h3 id="onboard-title-admin"class=">[39m
[37m                                                ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L18 |[90m    <span class=">🎯</span> Welcome, Admin![39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L18 |[90m    <span class=">🎯</span> Welcome, Admin![39m
[37m                            ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L1 |[90m if current_user.is_authenticated and current_user.is_admin and not session.getonboarded[39m
[37m          ^ [31mDoctype must be declared before any non-comment content. (doctype-first)[39m
[37m      L18 |[90m    <span class=">🎯</span> Welcome, Admin![39m
[37m                                 ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L19 |[90m  </h3>[39m
[37m             ^ [31mTag must be paired, no start tag: [ </h3> ] (tag-pair)[39m
[37m      L22 |[90m  <ol class="aria-label="Onboarding Steps">[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L22 |[90m...<ol class="aria-label="Onboarding Steps">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L23 |[90m    <template x-for="step, i in stepLabels":key="i">[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L23 |[90m...te x-for="step, i in stepLabels":key="i">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L24 |[90m      <li class=">[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L24 |[90m      <li class=">[39m
[37m                            ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L36 |[90m          <span x-show="stepsi"class=">✔️</span>[39m
[37m                     ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L36 |[90m          <span x-show="stepsi"class=">✔️</span>[39m
[37m                                                 ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L36 |[90m...         <span x-show="stepsi"class=">✔️</span>[39m
[37m                                                        ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L38 |[90m        <span[39m
[37m                   ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L41 |[90m        ></span>[39m
[37m                   ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L41 |[90m        ></span>[39m
[37m                    ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L42 |[90m      </li>[39m
[37m                 ^ [31mTag must be paired, no start tag: [ </li> ] (tag-pair)[39m
[37m      L43 |[90m    </template>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </template> ] (tag-pair)[39m
[37m      L44 |[90m  </ol>[39m
[37m             ^ [31mTag must be paired, no start tag: [ </ol> ] (tag-pair)[39m
[37m      L47 |[90m  <div class=">[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L47 |[90m  <div class=">[39m
[37m                         ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L48 |[90m    <a href="/dashboard"@click="stepQuick0"class="tabindex="0"aria-label="Learn more">Dashboard</a ar...[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L48 |[90m...ass="tabindex="0"aria-label="Learn more">Dashboard</a aria-label="Learn more">    <a href="/admin/inv...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L48 |[90m...dex="0"aria-label="Learn more">Dashboard</a aria-label="Learn more">    <a href="/admin/invite"@click...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L48 |[90m...re">Dashboard</a aria-label="Learn more">    <a href="/admin/invite"@click="stepQuick1"class="tabinde...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L48 |[90m...ashboard</a aria-label="Learn more">    <a href="/admin/invite"@click="stepQuick1"class="tabindex="0"...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L48 |[90m...ass="tabindex="0"aria-label="Learn more">Invite Sponsors</a aria-label="Learn more">    <a href="/adm...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L48 |[90m..."aria-label="Learn more">Invite Sponsors</a aria-label="Learn more">    <a href="/admin/import"@click...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L48 |[90m...vite Sponsors</a aria-label="Learn more">    <a href="/admin/import"@click="stepQuick2"class="tabinde...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L48 |[90m...Sponsors</a aria-label="Learn more">    <a href="/admin/import"@click="stepQuick2"class="tabindex="0"...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L48 |[90m...ass="tabindex="0"aria-label="Learn more">Import Contacts</a aria-label="Learn more">  </div>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L48 |[90m..."aria-label="Learn more">Import Contacts</a aria-label="Learn more">  </div>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L48 |[90m...port Contacts</a aria-label="Learn more">  </div>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L48 |[90m...t Contacts</a aria-label="Learn more">  </div>[39m
[37m                                                      ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L50 |[90m  <p class="id="ai-concierge-desc">💡 Need help? Use the AI Concierge<span aria-label="chat icon">💬<...[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L50 |[90m  <p class="id="ai-concierge-desc">💡 Need help? Use the AI Concierge<span aria-label="chat icon">💬<...[39m
[37m                                             ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L50 |[90m...label="chat icon">💬</span> at any time.</p>[39m
[37m                                                        ^ [31mTag must be paired, no start tag: [ </p> ] (tag-pair)[39m
[37m      L52 |[90m  <button[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L56 |[90m  >Got it!</button>[39m
[37m             ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L56 |[90m  >Got it!</button>[39m
[37m                     ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L57 |[90m</div>[39m
[37m           ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L61 |[90m<div[39m
[37m           ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L68 |[90m>[39m
[37m           ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L70 |[90m</div>[39m
[37m           ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m

   /home/cyberboyz/connectatx-fundraiser/app/templates/partials/back_to_top.html
[37m      L2 |[90m<button[39m
[37m          ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L8 |[90m>[39m
[37m          ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L2 |[90m<button[39m
[37m          ^ [31mDoctype must be declared before any non-comment content. (doctype-first)[39m
[37m      L10 |[90m  <span class=">Scroll to top</span>[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L10 |[90m  <span class=">Scroll to top</span>[39m
[37m                          ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L10 |[90m  <span class=">Scroll to top</span>[39m
[37m                                        ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L11 |[90m</button>[39m
[37m           ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m

   /home/cyberboyz/connectatx-fundraiser/app/templates/partials/digital_hub.html
[37m      L2 |[90m<button[39m
[37m          ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L9 |[90m>[39m
[37m          ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L10 |[90m  <span class=">Open chat</span>💬[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L10 |[90m  <span class=">Open chat</span>💬[39m
[37m                          ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L2 |[90m<button[39m
[37m          ^ [31mDoctype must be declared before any non-comment content. (doctype-first)[39m
[37m      L10 |[90m  <span class=">Open chat</span>💬[39m
[37m                                    ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L11 |[90m</button>[39m
[37m           ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L14 |[90m<dialog[39m
[37m           ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L20 |[90m>[39m
[37m           ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L21 |[90m  <div[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L26 |[90m  >[39m
[37m             ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L27 |[90m    <header class=">[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L27 |[90m    <header class=">[39m
[37m                              ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L28 |[90m      <span class="aria-hidden="true">🤖</span>[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L28 |[90m      <span class="aria-hidden="true">🤖</span>[39m
[37m                                                ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L28 |[90m      <span class="aria-hidden="true">🤖</span>[39m
[37m                                                     ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L29 |[90m      <h3 id="ai-modal-title"class=">AI Concierge</h3>[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L29 |[90m      <h3 id="ai-modal-title"class=">AI Concierge</h3>[39m
[37m                                               ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L29 |[90m... id="ai-modal-title"class=">AI Concierge</h3>[39m
[37m                                                      ^ [31mTag must be paired, no start tag: [ </h3> ] (tag-pair)[39m
[37m      L30 |[90m      <button[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L35 |[90m      >×</button>[39m
[37m                 ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L35 |[90m      >×</button>[39m
[37m                   ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L36 |[90m    </header>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </header> ] (tag-pair)[39m
[37m      L38 |[90m    <section[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L44 |[90m    >[39m
[37m               ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L46 |[90m    </section>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </section> ] (tag-pair)[39m
[37m      L48 |[90m    <div[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L53 |[90m    >AI is typing…</div>[39m
[37m               ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L53 |[90m    >AI is typing…</div>[39m
[37m                              ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L55 |[90m    <div[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L59 |[90m    >[39m
[37m               ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L62 |[90m    </div>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L64 |[90m    <form[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L70 |[90m    >[39m
[37m               ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L71 |[90m      <label class="for="ai-chat-input">Your message</label>[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L71 |[90m      <label class="for="ai-chat-input">Your message</label>[39m
[37m                                                  ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L71 |[90m... class="for="ai-chat-input">Your message</label>[39m
[37m                                                      ^ [31mTag must be paired, no start tag: [ </label> ] (tag-pair)[39m
[37m      L72 |[90m      <input[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L83 |[90m      />[39m
[37m                  ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L84 |[90m      <button[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L89 |[90m      >[39m
[37m                 ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L91 |[90m      </button>[39m
[37m                 ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L92 |[90m    </form>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </form> ] (tag-pair)[39m
[37m      L93 |[90m  </div>[39m
[37m             ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L94 |[90m</dialog>[39m
[37m           ^ [31mTag must be paired, no start tag: [ </dialog> ] (tag-pair)[39m

   /home/cyberboyz/connectatx-fundraiser/app/templates/partials/donate_modal.html
[37m      L2 |[90m<div id="donate-modal"class="role="dialog"aria-modal="true"aria-labelledby="donate-modal-title">[39m
[37m          ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L2 |[90m...rue"aria-labelledby="donate-modal-title">[39m
[37m                                                     ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L3 |[90m  <div class=">[39m
[37m            ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L3 |[90m  <div class=">[39m
[37m                        ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L4 |[90m    <button id="donate-modal-close"class="aria-label="Close">&times;</button>[39m
[37m              ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L4 |[90m...te-modal-close"class="aria-label="Close">&times;</button>[39m
[37m                                                     ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L1 |[90m# partials/donate_modal.html #[39m
[37m          ^ [31mDoctype must be declared before any non-comment content. (doctype-first)[39m
[37m      L4 |[90m...-close"class="aria-label="Close">&times;</button>[39m
[37m                                                     ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L5 |[90m    <h2 id="donate-modal-title"class=">Sponsor or Donate</h2>[39m
[37m              ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L5 |[90m    <h2 id="donate-modal-title"class=">Sponsor or Donate</h2>[39m
[37m                                                ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L5 |[90m...te-modal-title"class=">Sponsor or Donate</h2>[39m
[37m                                                     ^ [31mTag must be paired, no start tag: [ </h2> ] (tag-pair)[39m
[37m      L6 |[90m    <form id="donate-form"class=">[39m
[37m              ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L6 |[90m    <form id="donate-form"class=">[39m
[37m                                           ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L7 |[90m      <input name="name"required placeholder="Your Name"class="/ aria-label="Enter value">      <inpu...[39m
[37m                ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L7 |[90m...r Name"class="/ aria-label="Enter value">      <input name="email"required type="email"placeholder="E...[39m
[37m                                                     ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L7 |[90m...class="/ aria-label="Enter value">      <input name="email"required type="email"placeholder="Email"cl...[39m
[37m                                                     ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L7 |[90m..."Email"class="/ aria-label="Enter value">      <input name="amount"required type="number"min="5"step=...[39m
[37m                                                     ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L7 |[90m...class="/ aria-label="Enter value">      <input name="amount"required type="number"min="5"step="any"pl...[39m
[37m                                                     ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L7 |[90m...untUSD"class="/ aria-label="Enter value">      <select name="tier"class=">[39m
[37m                                                     ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L7 |[90m...class="/ aria-label="Enter value">      <select name="tier"class=">[39m
[37m                                                     ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L7 |[90m... value">      <select name="tier"class=">[39m
[37m                                                     ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L13 |[90m      </select>[39m
[37m                 ^ [31mTag must be paired, no start tag: [ </select> ] (tag-pair)[39m
[37m      L15 |[90m...       <span class=">Upload Logooptional</span>[39m
[37m                                                      ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L16 |[90m        <input type="file"name="logo"class="accept="image/*"/ aria-label="Enter value">      </label>[39m
[37m                   ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L16 |[90m...cept="image/*"/ aria-label="Enter value">      </label>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L17 |[90m      <div class=">[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L17 |[90m      <div class=">[39m
[37m                             ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L18 |[90m        <button type="button"id="stripe-pay-btn"class="aria-label="Donate with PayPal">Pay with Card<...[39m
[37m                   ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L18 |[90m...n"class="aria-label="Donate with PayPal">Pay with Card</button aria-label="Donate with PayPal">      ...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L18 |[90m...label="Donate with PayPal">Pay with Card</button aria-label="Donate with PayPal">        <button type...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L18 |[90m...</button aria-label="Donate with PayPal">        <button type="button"id="paypal-pay-btn"class="aria-...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L18 |[90m...aria-label="Donate with PayPal">        <button type="button"id="paypal-pay-btn"class="aria-label="Do...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L18 |[90m...n"class="aria-label="Donate with PayPal">PayPal</button aria-label="Donate with PayPal">      </div>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L18 |[90m...="aria-label="Donate with PayPal">PayPal</button aria-label="Donate with PayPal">      </div>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L18 |[90m...</button aria-label="Donate with PayPal">      </div>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L18 |[90m...n aria-label="Donate with PayPal">      </div>[39m
[37m                                                      ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L19 |[90m    </form>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </form> ] (tag-pair)[39m
[37m      L20 |[90m    <div id="donate-thankyou"class=">[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L20 |[90m    <div id="donate-thankyou"class=">[39m
[37m                                               ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L22 |[90m      <p class=">You’re a game changer!</p>[39m
[37m                                                   ^ [31mTag must be paired, no start tag: [ </p> ] (tag-pair)[39m
[37m      L23 |[90m    </div>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L24 |[90m  </div>[39m
[37m             ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L25 |[90m</div>[39m
[37m           ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L27 |[90m[39m
[37m           ^ [31mTag must be paired, missing: [ </h3> ], open tag match failed [ <h3 class=">Thank you! 🎉</h3>
      <p class="> ] on line 21. (tag-pair)[39m

   /home/cyberboyz/connectatx-fundraiser/app/templates/partials/donation_modal.html
[37m      L2 |[90m<form[39m
[37m          ^ [31mDoctype must be declared before any non-comment content. (doctype-first)[39m
[37m      L15 |[90m  <div class=">[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L15 |[90m  <div class=">[39m
[37m                         ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L16 |[90m    <input[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L28 |[90m    />[39m
[37m                ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L36 |[90m    <span class=">$</span>[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L36 |[90m    <span class=">$</span>[39m
[37m                            ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L36 |[90m    <span class=">$</span>[39m
[37m                              ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L37 |[90m    <p id="donation-amount-help"class=">[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L37 |[90m    <p id="donation-amount-help"class=">[39m
[37m                                                  ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L38 |[90m      <span class=">Minimum $5</span> &mdash; every dollar goes to kids.[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L38 |[90m      <span class=">Minimum $5</span> &mdash; every dollar goes to kids.[39m
[37m                              ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L38 |[90m      <span class=">Minimum $5</span> &mdash; every dollar goes to kids.[39m
[37m                                         ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L39 |[90m    </p>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </p> ] (tag-pair)[39m
[37m      L40 |[90m  </div>[39m
[37m             ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L44 |[90m    <fieldset class="aria-describedby="payment-method-help">[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L44 |[90m...="aria-describedby="payment-method-help">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L45 |[90m      <legend class=">Payment Method</legend>[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L45 |[90m      <legend class=">Payment Method</legend>[39m
[37m                                ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L45 |[90m      <legend class=">Payment Method</legend>[39m
[37m                                               ^ [31mTag must be paired, no start tag: [ </legend> ] (tag-pair)[39m
[37m      L46 |[90m      <button[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L52 |[90m      >[39m
[37m                 ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L53 |[90m        <svg class="fill="none"stroke="currentColor"viewBox="0 0 24 24"aria-label="REVIEW_ME"><rect x...[39m
[37m                   ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L53 |[90m...iewBox="0 0 24 24"aria-label="REVIEW_ME"><rect x="3"y="6"width="18"height="12"rx="3"stroke-width="2"/...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L53 |[90m...ewBox="0 0 24 24"aria-label="REVIEW_ME"><rect x="3"y="6"width="18"height="12"rx="3"stroke-width="2"/ ...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L53 |[90m...stroke-width="2"/ aria-label="REVIEW_ME"><path d="M7 10h.01M17 10h.01M12 15v.01"/ aria-label="REVIEW_...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L53 |[90m...troke-width="2"/ aria-label="REVIEW_ME"><path d="M7 10h.01M17 10h.01M12 15v.01"/ aria-label="REVIEW_M...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L53 |[90m...0h.01M12 15v.01"/ aria-label="REVIEW_ME"></svg aria-label="REVIEW_ME">        Card[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L53 |[90m...h.01M12 15v.01"/ aria-label="REVIEW_ME"></svg aria-label="REVIEW_ME">        Card[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L53 |[90m..."REVIEW_ME"></svg aria-label="REVIEW_ME">        Card[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L54 |[90m      </button>[39m
[37m                 ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L55 |[90m      <button[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L61 |[90m      >[39m
[37m                 ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L62 |[90m        <svg class="fill="currentColor"viewBox="0 0 24 24"aria-label="REVIEW_ME"><rect x="2"y="6"widt...[39m
[37m                   ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L62 |[90m...iewBox="0 0 24 24"aria-label="REVIEW_ME"><rect x="2"y="6"width="20"height="12"rx="4"/ aria-label="REV...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L62 |[90m...ewBox="0 0 24 24"aria-label="REVIEW_ME"><rect x="2"y="6"width="20"height="12"rx="4"/ aria-label="REVI...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L62 |[90m...eight="12"rx="4"/ aria-label="REVIEW_ME"><text x="12"y="16"text-anchor="middle"font-size="8"fill="#1a...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L62 |[90m...ight="12"rx="4"/ aria-label="REVIEW_ME"><text x="12"y="16"text-anchor="middle"font-size="8"fill="#1a2...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L62 |[90m...="8"fill="#1a202c"aria-label="REVIEW_ME">PP</text aria-label="REVIEW_ME"></svg aria-label="REVIEW_ME"...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L62 |[90m..."fill="#1a202c"aria-label="REVIEW_ME">PP</text aria-label="REVIEW_ME"></svg aria-label="REVIEW_ME">  ...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L62 |[90m...VIEW_ME">PP</text aria-label="REVIEW_ME"></svg aria-label="REVIEW_ME">        PayPal[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L62 |[90m...IEW_ME">PP</text aria-label="REVIEW_ME"></svg aria-label="REVIEW_ME">        PayPal[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L62 |[90m..."REVIEW_ME"></svg aria-label="REVIEW_ME">        PayPal[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L63 |[90m      </button>[39m
[37m                 ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L64 |[90m    </fieldset>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </fieldset> ] (tag-pair)[39m
[37m      L65 |[90m    <p id="payment-method-help"class=">100 Secure. Choose Card or PayPal.</p>[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L65 |[90m    <p id="payment-method-help"class=">100 Secure. Choose Card or PayPal.</p>[39m
[37m                                                 ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L65 |[90m...ass=">100 Secure. Choose Card or PayPal.</p>[39m
[37m                                                      ^ [31mTag must be paired, no start tag: [ </p> ] (tag-pair)[39m
[37m      L69 |[90m  <div id="stripe-form"class=">[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L69 |[90m  <div id="stripe-form"class=">[39m
[37m                                         ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L70 |[90m    <div id="stripe-element"class="aria-label="Credit or debit card input"></div>[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L70 |[90m..."aria-label="Credit or debit card input"></div>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L70 |[90m...aria-label="Credit or debit card input"></div>[39m
[37m                                                      ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L71 |[90m  </div>[39m
[37m             ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L74 |[90m  <div id="paypal-form"class="aria-hidden="true">[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L74 |[90m...d="paypal-form"class="aria-hidden="true">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L75 |[90m    <div id="paypal-button-container"class="></div>[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L75 |[90m...<div id="paypal-button-container"class="></div>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L75 |[90m...div id="paypal-button-container"class="></div>[39m
[37m                                                      ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L76 |[90m  </div>[39m
[37m             ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L79 |[90m  <div class=">[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L79 |[90m  <div class=">[39m
[37m                         ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L80 |[90m    <button[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L86 |[90m    >[39m
[37m               ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L88 |[90m    </button>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L89 |[90m...Powered by <span class=">Stripe & PayPal</span></p>[39m
[37m                                                      ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L90 |[90m  </div>[39m
[37m             ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m

   /home/cyberboyz/connectatx-fundraiser/app/templates/partials/flash_and_onboarding.html
[37m      L4 |[90m    <div[39m
[37m              ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L9 |[90m    >[39m
[37m              ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L1 |[90m# ======================= FLASH MESSAGESElite Polish ======================= #[39m
[37m          ^ [31mDoctype must be declared before any non-comment content. (doctype-first)[39m
[37m      L28 |[90m          <button[39m
[37m                     ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L34 |[90m          >&times;</button>[39m
[37m                     ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L34 |[90m          >&times;</button>[39m
[37m                             ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L37 |[90m    </div>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L67 |[90m  <div[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L75 |[90m  >[39m
[37m             ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L76 |[90m    <h2 id="onboard-title"class=">[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L76 |[90m    <h2 id="onboard-title"class=">[39m
[37m                                            ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L77 |[90m      <span class=">🏀</span> Welcome![39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L77 |[90m      <span class=">🏀</span> Welcome![39m
[37m                              ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L77 |[90m      <span class=">🏀</span> Welcome![39m
[37m                                   ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L78 |[90m    </h2>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </h2> ] (tag-pair)[39m
[37m      L79 |[90m    <p id="onboard-description"class=">[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L79 |[90m    <p id="onboard-description"class=">[39m
[37m                                                 ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L81 |[90m      <span class=">Become a Champion Sponsor today!</span>[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L81 |[90m      <span class=">Become a Champion Sponsor today!</span>[39m
[37m                              ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L81 |[90m...class=">Become a Champion Sponsor today!</span>[39m
[37m                                                      ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L82 |[90m    </p>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </p> ] (tag-pair)[39m
[37m      L83 |[90m    <button[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L89 |[90m        .then=> document.getElementByIdonboarding-popover.remove;[39m
[37m                         ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L92 |[90m    >[39m
[37m               ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L94 |[90m    </button>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L95 |[90m  </div>[39m
[37m             ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m

   /home/cyberboyz/connectatx-fundraiser/app/templates/partials/footer.html
[37m      L1 |[90m# === Pro-Polished Footer Partial — FundChamps Elite Edition === #[39m
[37m          ^ [31mDoctype must be declared before any non-comment content. (doctype-first)[39m
[37m      L16 |[90m    <img src="footer_logo"alt="Connect ATX Elite logo"class="aria-hidden="true"loading="lazy"decoding...[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L16 |[90m...en="true"loading="lazy"decoding="async"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L17 |[90m  </div>[39m
[37m             ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L20 |[90m  <a href="#main"class="tabindex="0"aria-label="Learn more">Skip to Main</a aria-label="Learn more">[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L20 |[90m...ass="tabindex="0"aria-label="Learn more">Skip to Main</a aria-label="Learn more">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L20 |[90m...="0"aria-label="Learn more">Skip to Main</a aria-label="Learn more">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L20 |[90m...>Skip to Main</a aria-label="Learn more">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L21 |[90m  <div class=">[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L21 |[90m  <div class=">[39m
[37m                         ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L23 |[90m    <section aria-label="Team brand and social links"class=">[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L23 |[90m...bel="Team brand and social links"class=">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L24 |[90m      <img src="footer_logo"alt="team.team_name orFundChamps logo"class="loading="lazy"decoding="asyn...[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L24 |[90m...o"class="loading="lazy"decoding="async"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L28 |[90m...&nbsp;|&nbsp; team.location orAustin, TX</p>[39m
[37m                                                      ^ [31mTag must be paired, no start tag: [ </p> ] (tag-pair)[39m
[37m      L29 |[90m      <p class=">© now_year</p>[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L29 |[90m      <p class=">© now_year</p>[39m
[37m                           ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L29 |[90m      <p class=">© now_year</p>[39m
[37m                                      ^ [31mTag must be paired, no start tag: [ </p> ] (tag-pair)[39m
[37m      L30 |[90m      <nav class="aria-label="Social media links">[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L30 |[90m...v class="aria-label="Social media links">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L32 |[90m          <a href="team.instagram"target="_blank"rel="noopener noreferrer"aria-label="Instagram"class...[39m
[37m                     ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L32 |[90m...noreferrer"aria-label="Instagram"class=">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L33 |[90m            <svg class="fill="none"stroke="currentColor"viewBox="0 0 24 24"aria-hidden="true"aria-lab...[39m
[37m                       ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L33 |[90m...aria-hidden="true"aria-label="REVIEW_ME">              <rect x="2"y="2"width="20"height="20"rx="6"str...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L33 |[90m...ue"aria-label="REVIEW_ME">              <rect x="2"y="2"width="20"height="20"rx="6"stroke-width="2"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L33 |[90m...h="20"height="20"rx="6"stroke-width="2"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L34 |[90m              <circle cx="12"cy="12"r="5"stroke-width="2"/>[39m
[37m                         ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L34 |[90m...cle cx="12"cy="12"r="5"stroke-width="2"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L35 |[90m              <circle cx="18"cy="6"r="1.5"fill="currentColor"/>[39m
[37m                         ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L35 |[90m...cx="18"cy="6"r="1.5"fill="currentColor"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L36 |[90m            </svg>[39m
[37m                       ^ [31mTag must be paired, no start tag: [ </svg> ] (tag-pair)[39m
[37m      L37 |[90m          </a>[39m
[37m                     ^ [31mTag must be paired, no start tag: [ </a> ] (tag-pair)[39m
[37m      L40 |[90m          <a href="team.facebook"target="_blank"rel="noopener noreferrer"aria-label="Facebook"class="...[39m
[37m                     ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L40 |[90m... noreferrer"aria-label="Facebook"class=">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L41 |[90m            <svg class="fill="none"stroke="currentColor"viewBox="0 0 24 24"aria-hidden="true"aria-lab...[39m
[37m                       ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L41 |[90m...aria-hidden="true"aria-label="REVIEW_ME">              <rect x="2"y="2"width="20"height="20"rx="6"str...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L41 |[90m...ue"aria-label="REVIEW_ME">              <rect x="2"y="2"width="20"height="20"rx="6"stroke-width="2"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L41 |[90m...h="20"height="20"rx="6"stroke-width="2"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L42 |[90m              <path d="M16 8h-2a2 2 0 0 0-2 2v2h4l-1 4h-3v4"stroke-width="2"/>[39m
[37m                         ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L42 |[90m... 0 0-2 2v2h4l-1 4h-3v4"stroke-width="2"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L43 |[90m            </svg>[39m
[37m                       ^ [31mTag must be paired, no start tag: [ </svg> ] (tag-pair)[39m
[37m      L44 |[90m          </a>[39m
[37m                     ^ [31mTag must be paired, no start tag: [ </a> ] (tag-pair)[39m
[37m      L47 |[90m          <a href="team.twitter"target="_blank"rel="noopener noreferrer"aria-label="Twitter / X"class...[39m
[37m                     ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L47 |[90m...referrer"aria-label="Twitter / X"class=">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L48 |[90m            <svg class="fill="none"stroke="currentColor"viewBox="0 0 24 24"aria-hidden="true"aria-lab...[39m
[37m                       ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L48 |[90m...aria-hidden="true"aria-label="REVIEW_ME">              <rect x="2"y="2"width="20"height="20"rx="6"str...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L48 |[90m...ue"aria-label="REVIEW_ME">              <rect x="2"y="2"width="20"height="20"rx="6"stroke-width="2"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L48 |[90m...h="20"height="20"rx="6"stroke-width="2"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L49 |[90m              <path d="M7 17L17 7M7 7l10 10"stroke-width="2"/>[39m
[37m                         ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L49 |[90m...="M7 17L17 7M7 7l10 10"stroke-width="2"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L50 |[90m            </svg>[39m
[37m                       ^ [31mTag must be paired, no start tag: [ </svg> ] (tag-pair)[39m
[37m      L51 |[90m          </a>[39m
[37m                     ^ [31mTag must be paired, no start tag: [ </a> ] (tag-pair)[39m
[37m      L53 |[90m      </nav>[39m
[37m                 ^ [31mTag must be paired, no start tag: [ </nav> ] (tag-pair)[39m
[37m      L54 |[90m    </section>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </section> ] (tag-pair)[39m
[37m      L57 |[90m    <section aria-label="Fundraising progress and quick links"class=">[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L57 |[90m...raising progress and quick links"class=">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L58 |[90m      <div[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L64 |[90m      >[39m
[37m                 ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L65 |[90m        <div id="footer-bar"style="width: pct;"class="></div>[39m
[37m                   ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L65 |[90m...d="footer-bar"style="width: pct;"class="></div>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L65 |[90m...="footer-bar"style="width: pct;"class="></div>[39m
[37m                                                      ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L66 |[90m      </div>[39m
[37m                 ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L67 |[90m      <p id="footer-status"class=">[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L67 |[90m      <p id="footer-status"class=">[39m
[37m                                             ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L69 |[90m if raised >= goal[39m
[37m                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L70 |[90m          <span class="id="footer-confetti"aria-label="Goal reached celebration"role="img">🎉</span>[39m
[37m                     ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L70 |[90m...bel="Goal reached celebration"role="img">🎉</span>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L70 |[90m...="Goal reached celebration"role="img">🎉</span>[39m
[37m                                                        ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L72 |[90m      </p>[39m
[37m                 ^ [31mTag must be paired, no start tag: [ </p> ] (tag-pair)[39m
[37m      L73 |[90m      <nav class="aria-label="Contact and donation quick links">[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L73 |[90m...label="Contact and donation quick links">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L74 |[90m        <a class="href="mailto: team.email orarodgps@gmail.com"aria-label="Learn more">📧 Email</a ar...[39m
[37m                   ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L74 |[90m...rodgps@gmail.com"aria-label="Learn more">📧 Email</a aria-label="Learn more">        <a class="href="...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L74 |[90m...ail.com"aria-label="Learn more">📧 Email</a aria-label="Learn more">        <a class="href="team.webs...[39m
[37m                                                        ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L74 |[90m...ore">📧 Email</a aria-label="Learn more">        <a class="href="team.website orhttps://www.connectat...[39m
[37m                                                        ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L74 |[90m...mail</a aria-label="Learn more">        <a class="href="team.website orhttps://www.connectatxelite.co...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L74 |[90m...pener noreferrer"aria-label="Learn more">🌐 Website</a aria-label="Learn more">        <a class="href...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L74 |[90m...errer"aria-label="Learn more">🌐 Website</a aria-label="Learn more">        <a class="href="team.payp...[39m
[37m                                                        ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L74 |[90m...e">🌐 Website</a aria-label="Learn more">        <a class="href="team.paypal orhttps://www.paypal.com...[39m
[37m                                                        ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L74 |[90m...site</a aria-label="Learn more">        <a class="href="team.paypal orhttps://www.paypal.com/donate/y...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L74 |[90m...pener noreferrer"aria-label="Learn more">💸 Donate</a aria-label="Learn more">      </nav>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L74 |[90m...ferrer"aria-label="Learn more">💸 Donate</a aria-label="Learn more">      </nav>[39m
[37m                                                        ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L74 |[90m...re">💸 Donate</a aria-label="Learn more">      </nav>[39m
[37m                                                        ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L74 |[90m...Donate</a aria-label="Learn more">      </nav>[39m
[37m                                                      ^ [31mTag must be paired, no start tag: [ </nav> ] (tag-pair)[39m
[37m      L75 |[90m    </section>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </section> ] (tag-pair)[39m
[37m      L78 |[90m    <section aria-label="Direct contact and next event countdown"class=">[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L78 |[90m...contact and next event countdown"class=">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L79 |[90m...<strong aria-label="Learn more">Contact:</strong aria-label="Learn more"> <a class="href="mailto: tea...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L79 |[90m...Contact:</strong aria-label="Learn more"> <a class="href="mailto: team.email orarodgps@gmail.com"aria...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L79 |[90m...ntact:</strong aria-label="Learn more"> <a class="href="mailto: team.email orarodgps@gmail.com"aria-l...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L79 |[90m...rodgps@gmail.com"aria-label="Learn more"> team.email orarodgps@gmail.com</a aria-label="Learn more"><...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L79 |[90m...rn more"> team.email orarodgps@gmail.com</a aria-label="Learn more"></p aria-label="Learn more">     ...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L79 |[90m...gps@gmail.com</a aria-label="Learn more"></p aria-label="Learn more">      <p aria-label="Learn more"...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L79 |[90m...ps@gmail.com</a aria-label="Learn more"></p aria-label="Learn more">      <p aria-label="Learn more">...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L79 |[90m..."Learn more"></p aria-label="Learn more">      <p aria-label="Learn more"><strong aria-label="Learn m...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L79 |[90m..."><strong aria-label="Learn more">Phone:</strong aria-label="Learn more"> <a class="href="tel: team.p...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L79 |[90m...">Phone:</strong aria-label="Learn more"> <a class="href="tel: team.phone or512 820-0475"aria-label="...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L79 |[90m...Phone:</strong aria-label="Learn more"> <a class="href="tel: team.phone or512 820-0475"aria-label="Le...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L79 |[90m...e or512 820-0475"aria-label="Learn more"> team.phone or512 820-0475</a aria-label="Learn more"></p ar...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L79 |[90m...="Learn more"> team.phone or512 820-0475</a aria-label="Learn more"></p aria-label="Learn more">     ...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L79 |[90m...r512 820-0475</a aria-label="Learn more"></p aria-label="Learn more">      <p id="next-event"aria-liv...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L79 |[90m...512 820-0475</a aria-label="Learn more"></p aria-label="Learn more">      <p id="next-event"aria-live...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L79 |[90m..."Learn more"></p aria-label="Learn more">      <p id="next-event"aria-live="polite"aria-atomic="true"...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L79 |[90m...more"></p aria-label="Learn more">      <p id="next-event"aria-live="polite"aria-atomic="true"class="...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L79 |[90m...a-live="polite"aria-atomic="true"class=">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L80 |[90m        Next Tournament: <span id="next-event-text"aria-live="polite">Loading…</span>[39m
[37m                                    ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L80 |[90m...n id="next-event-text"aria-live="polite">Loading…</span>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L80 |[90m...t-event-text"aria-live="polite">Loading…</span>[39m
[37m                                                       ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L79 |[90m... more">      <p aria-label="Learn more"><strong aria-label="Learn more">Phone:</strong aria-label="Le...[39m
[37m                                                      ^ [31mTag must be paired, missing: [ </strong> ], start tag match failed [ <strong aria-label="Learn more"> ] on line 79. (tag-pair)[39m
[37m      L82 |[90m      <button type="button"onclick="openSupporters"class="aria-label="View all supporters">View All S...[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L82 |[90m..."class="aria-label="View all supporters">View All Supporters</button>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L82 |[90m...View all supporters">View All Supporters</button>[39m
[37m                                                      ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L83 |[90m    </section>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </section> ] (tag-pair)[39m
[37m      L84 |[90m  </div>[39m
[37m             ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L87 |[90m  <div[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L92 |[90m  >[39m
[37m             ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L93 |[90m    <strong class=">Recent Supporters:</strong>[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L93 |[90m    <strong class=">Recent Supporters:</strong>[39m
[37m                              ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L94 |[90m    <span id="ticker-items"class=">[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L94 |[90m    <span id="ticker-items"class=">[39m
[37m                                             ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L104 |[90m    </span>[39m
[37m                ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L105 |[90m  </div>[39m
[37m              ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L111 |[90m    </span>[39m
[37m                ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L122 |[90m      <button type="button"class="aria-label="Close supporters modal"onclick="closeSupporters">×</but...[39m
[37m                  ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L122 |[90m...pporters modal"onclick="closeSupporters">×</button>[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L122 |[90m...orters modal"onclick="closeSupporters">×</button>[39m
[37m                                                       ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L123 |[90m      <h3 id="supporters-title"class=">🏆 All Supporters</h3>[39m
[37m                  ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L123 |[90m      <h3 id="supporters-title"class=">🏆 All Supporters</h3>[39m
[37m                                                  ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L115 |[90m  <dialog[39m
[37m              ^ [31mTag must be paired, missing: [ </dialog></p> ], start tag match failed [ <dialog
    id="supporters-modal"
    aria-modal="true"
    aria-labelledby="supporters-title"
    class="
  >
    <div class="> ] on line 115. (tag-pair)[39m
[37m      L124 |[90m      <ul class="tabindex="0">[39m
[37m                  ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L124 |[90m      <ul class="tabindex="0">[39m
[37m                                         ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L132 |[90m      </ul>[39m
[37m                  ^ [31mTag must be paired, no start tag: [ </ul> ] (tag-pair)[39m
[37m      L133 |[90m      <p class=">Thank you for championing our mission!</p>[39m
[37m                  ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L133 |[90m      <p class=">Thank you for championing our mission!</p>[39m
[37m                            ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L133 |[90m...">Thank you for championing our mission!</p>[39m
[37m                                                       ^ [31mTag must be paired, no start tag: [ </p> ] (tag-pair)[39m
[37m      L134 |[90m    </div>[39m
[37m                ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L135 |[90m  </dialog>[39m
[37m              ^ [31mTag must be paired, no start tag: [ </dialog> ] (tag-pair)[39m
[37m      L139 |[90m<a[39m
[37m            ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L144 |[90m>[39m
[37m            ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L146 |[90m</a>[39m
[37m            ^ [31mTag must be paired, no start tag: [ </a> ] (tag-pair)[39m

   /home/cyberboyz/connectatx-fundraiser/app/templates/partials/header_and_announcement.html
[37m      L5 |[90m<header[39m
[37m          ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L13 |[90m>[39m
[37m           ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L19 |[90m    <div[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L28 |[90m    >[39m
[37m               ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L1 |[90m from "macros/ui.html"import render_button[39m
[37m          ^ [31mDoctype must be declared before any non-comment content. (doctype-first)[39m
[37m      L31 |[90m        <a[39m
[37m                   ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L36 |[90m        > announcement.cta</a>[39m
[37m                   ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L36 |[90m        > announcement.cta</a>[39m
[37m                                     ^ [31mTag must be paired, no start tag: [ </a> ] (tag-pair)[39m
[37m      L38 |[90m      <button[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L43 |[90m      >×</button>[39m
[37m                 ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L43 |[90m      >×</button>[39m
[37m                   ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L44 |[90m    </div>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L49 |[90m    <div[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L55 |[90m    >[39m
[37m               ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L57 |[90m    </div>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L61 |[90m  <div class=">[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L61 |[90m  <div class=">[39m
[37m                         ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L62 |[90m    <a[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L65 |[90m    >[39m
[37m               ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L66 |[90m      <img        src="logo_src"[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L73 |[90m      />[39m
[37m                  ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L74 |[90m      <span class=">[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L74 |[90m      <span class=">[39m
[37m                              ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L76 |[90m      </span>[39m
[37m                 ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L77 |[90m    </a>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </a> ] (tag-pair)[39m
[37m      L78 |[90m    <nav class="aria-label="Primary navigation">[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L78 |[90m...v class="aria-label="Primary navigation">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L85 |[90m          <span class="></span>[39m
[37m                                   ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L88 |[90m    </nav>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </nav> ] (tag-pair)[39m
[37m      L89 |[90m    <div class="aria-label="Fundraising progress"role="region">[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L89 |[90m...abel="Fundraising progress"role="region">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L94 |[90m        <span class=">$ raised | comma</span>[39m
[37m                                                 ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L98 |[90m      <div class=">[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L98 |[90m      <div class=">[39m
[37m                             ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L99 |[90m        <div class="style="width: pct;"></div>[39m
[37m                   ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L99 |[90m        <div class="style="width: pct;"></div>[39m
[37m                                                  ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L99 |[90m        <div class="style="width: pct;"></div>[39m
[37m                                                   ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L100 |[90m      </div>[39m
[37m                  ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L101 |[90m    </div>[39m
[37m                ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L102 |[90m    <div class=">[39m
[37m                ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L102 |[90m    <div class=">[39m
[37m                            ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L106 |[90m    </div>[39m
[37m                ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L107 |[90m  </div>[39m
[37m              ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L108 |[90m  <div class="aria-label="Trust and credibility statement">[39m
[37m              ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L108 |[90m...-label="Trust and credibility statement">[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L110 |[90m  </div>[39m
[37m              ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L112 |[90m  <nav[39m
[37m              ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L124 |[90m  >[39m
[37m              ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L125 |[90m    <button @click="mobileOpen = false"aria-label="Close menu"class="type="button">×</button>[39m
[37m                ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L125 |[90m...a-label="Close menu"class="type="button">×</button>[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L125 |[90m...label="Close menu"class="type="button">×</button>[39m
[37m                                                       ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L127 |[90m      <a href="# id"@click="mobileOpen = false"class="tabindex="0"role="menuitem"aria-label="Learn mo...[39m
[37m                  ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L127 |[90m...0"role="menuitem"aria-label="Learn more"> label</a aria-label="Learn more"> endfor[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L127 |[90m..."menuitem"aria-label="Learn more"> label</a aria-label="Learn more"> endfor[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L127 |[90m... more"> label</a aria-label="Learn more"> endfor[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L128 |[90m    <div class=">[39m
[37m                ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L128 |[90m    <div class=">[39m
[37m                            ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L131 |[90m    </div>[39m
[37m                ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L132 |[90m  </nav>[39m
[37m              ^ [31mTag must be paired, no start tag: [ </nav> ] (tag-pair)[39m
[37m      L133 |[90m</header>[39m
[37m            ^ [31mTag must be paired, no start tag: [ </header> ] (tag-pair)[39m
[37m      L135 |[90m<a href="#donate"class="aria-label="Quick Donate">💸 Quick Donate</a>[39m
[37m            ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L135 |[90m...#donate"class="aria-label="Quick Donate">💸 Quick Donate</a>[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L135 |[90m...ria-label="Quick Donate">💸 Quick Donate</a>[39m
[37m                                                         ^ [31mTag must be paired, no start tag: [ </a> ] (tag-pair)[39m

   /home/cyberboyz/connectatx-fundraiser/app/templates/partials/header_sponsor_ticker.html
[37m      L10 |[90m<div[39m
[37m           ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L17 |[90m>[39m
[37m           ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L18 |[90m  <span class="aria-hidden="true">🌟</span>[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L18 |[90m  <span class="aria-hidden="true">🌟</span>[39m
[37m                                            ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L1 |[90m# ===========================[39m
[37m          ^ [31mDoctype must be declared before any non-comment content. (doctype-first)[39m
[37m      L18 |[90m  <span class="aria-hidden="true">🌟</span>[39m
[37m                                                 ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L19 |[90m  <span class=">Thanks to our amazing sponsors:</span>[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L19 |[90m  <span class=">Thanks to our amazing sponsors:</span>[39m
[37m                          ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L19 |[90m... class=">Thanks to our amazing sponsors:</span>[39m
[37m                                                      ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L20 |[90m  <span id="ticker-track"class=">[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L20 |[90m  <span id="ticker-track"class=">[39m
[37m                                           ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L28 |[90m      <a[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L33 |[90m      > sponsor.name</a>[39m
[37m                 ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L33 |[90m      > sponsor.name</a>[39m
[37m                               ^ [31mTag must be paired, no start tag: [ </a> ] (tag-pair)[39m
[37m      L35 |[90m        <span aria-hidden="true"class=">•</span>[39m
[37m                   ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L35 |[90m        <span aria-hidden="true"class=">•</span>[39m
[37m                                                  ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L35 |[90m...       <span aria-hidden="true"class=">•</span>[39m
[37m                                                       ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L38 |[90m  </span>[39m
[37m             ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L39 |[90m</div>[39m
[37m           ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m

   /home/cyberboyz/connectatx-fundraiser/app/templates/partials/hero_and_fundraiser.html
[37m      L21 |[90m<section[39m
[37m           ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L27 |[90m>[39m
[37m           ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L1 |[90m from "macros/confetti.html"import launch_confetti[39m
[37m          ^ [31mDoctype must be declared before any non-comment content. (doctype-first)[39m
[37m      L29 |[90m  <img    src="url_forstatic, filename=hero_img if:// not in hero_img elseimages/ ~ hero_img"[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L37 |[90m  />[39m
[37m              ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L40 |[90m  <div class=">[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L40 |[90m  <div class=">[39m
[37m                         ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L41 |[90m    <div class="style="width:min97vw,1320px;height:min88vw,670px;"aria-hidden="true"></div>[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L41 |[90m...height:min88vw,670px;"aria-hidden="true"></div>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L41 |[90m...eight:min88vw,670px;"aria-hidden="true"></div>[39m
[37m                                                      ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L42 |[90m  </div>[39m
[37m             ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L49 |[90m      <span class="> live_announcement</span>[39m
[37m                                                 ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L57 |[90m      <img        src="url_forstatic, filename=logo_src"[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L62 |[90m      />[39m
[37m                  ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L63 |[90m      <h1[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L67 |[90m      >[39m
[37m                 ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L69 |[90m      </h1>[39m
[37m                 ^ [31mTag must be paired, no start tag: [ </h1> ] (tag-pair)[39m
[37m      L70 |[90m      <div class=">[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L70 |[90m      <div class=">[39m
[37m                             ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L71 |[90m        <svg class="fill="none"viewBox="0 0 16 16"aria-label="REVIEW_ME"><circle cx="8"cy="8"r="7"str...[39m
[37m                   ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L71 |[90m...iewBox="0 0 16 16"aria-label="REVIEW_ME"><circle cx="8"cy="8"r="7"stroke="#D32F2F"stroke-width="2"/ a...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L71 |[90m...ewBox="0 0 16 16"aria-label="REVIEW_ME"><circle cx="8"cy="8"r="7"stroke="#D32F2F"stroke-width="2"/ ar...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L71 |[90m...stroke-width="2"/ aria-label="REVIEW_ME"></svg aria-label="REVIEW_ME">        <span class="> region</...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L71 |[90m...troke-width="2"/ aria-label="REVIEW_ME"></svg aria-label="REVIEW_ME">        <span class="> region</s...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L71 |[90m..."REVIEW_ME"></svg aria-label="REVIEW_ME">        <span class="> region</span>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L73 |[90m        <span class=">Family, Grit &amp; Honor — On and Off the Court</span>[39m
[37m                   ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L73 |[90m        <span class=">Family, Grit &amp; Honor — On and Off the Court</span>[39m
[37m                                ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L73 |[90m... Grit &amp; Honor — On and Off the Court</span>[39m
[37m                                                       ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L75 |[90m        <button[39m
[37m                   ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L79 |[90m        >[39m
[37m                   ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L81 |[90m        </button>[39m
[37m                   ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L83 |[90m    </div>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L87 |[90m...e a <span class=">family-run AAU program</span> transforming East Austin youth into[39m
[37m                                                      ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L88 |[90m      <span class=">scholar-athletes, leaders, and community champions</span>.[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L88 |[90m      <span class=">scholar-athletes, leaders, and community champions</span>.[39m
[37m                              ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L88 |[90m...hletes, leaders, and community champions</span>.[39m
[37m                                                      ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L92 |[90m    <div class="role="list"aria-label="Team Impact Stats">[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L92 |[90m...ole="list"aria-label="Team Impact Stats">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L94 |[90m      <div class="role="listitem"tabindex="0">[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L94 |[90m... <div class="role="listitem"tabindex="0">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L97 |[90m      </div>[39m
[37m                 ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L99 |[90m    </div>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L102 |[90m    <div id="sticky-progress"class=">[39m
[37m                ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L102 |[90m    <div id="sticky-progress"class=">[39m
[37m                                                ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L105 |[90m        <span class=">/ $ goal | comma</span>[39m
[37m                                                  ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L106 |[90m        <span class="> pct</span>[39m
[37m                    ^ [31mTag must be paired, missing: [ </span> ], start tag match failed [ <span class="> pct</span>
      </div>
      <div class="> ] on line 106. (tag-pair)[39m
[37m      L111 |[90m        <span class=">Live Ticker:</span>[39m
[37m                    ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L111 |[90m        <span class=">Live Ticker:</span>[39m
[37m                                 ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L111 |[90m        <span class=">Live Ticker:</span>[39m
[37m                                              ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L112 |[90m        <span id="live-ticker"class="></span>[39m
[37m                    ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L112 |[90m        <span id="live-ticker"class="></span>[39m
[37m                                                 ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L112 |[90m        <span id="live-ticker"class="></span>[39m
[37m                                                  ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L113 |[90m      </div>[39m
[37m                  ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L114 |[90m    </div>[39m
[37m                ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L117 |[90m    <a[39m
[37m                ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L121 |[90m    >[39m
[37m                ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L127 |[90m    </a>[39m
[37m                ^ [31mTag must be paired, no start tag: [ </a> ] (tag-pair)[39m
[37m      L130 |[90m    <div id="hero-confetti"class="></div>[39m
[37m                ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L130 |[90m    <div id="hero-confetti"class="></div>[39m
[37m                                              ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L130 |[90m    <div id="hero-confetti"class="></div>[39m
[37m                                               ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L131 |[90m  </div>[39m
[37m              ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L132 |[90m</section>[39m
[37m            ^ [31mTag must be paired, no start tag: [ </section> ] (tag-pair)[39m
[37m      L135 |[90m<dialog id="team-modal"class=">[39m
[37m            ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L135 |[90m<dialog id="team-modal"class=">[39m
[37m                                          ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L136 |[90m  <div class=">[39m
[37m              ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L136 |[90m  <div class=">[39m
[37m                          ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L137 |[90m    <button class="onclick="this.closest('dialog').close()"aria-label="<button class="..."onclick="th...[39m
[37m                ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L137 |[90m...s.closest('dialog').close()"aria-label="<button class="..."onclick="this.closest('dialog').close()"ar...[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L137 |[90m...').close()"aria-label="Close team modal">✖</button>">✖</button aria-label="<button class="..."onclick...[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L137 |[90m....close()"aria-label="Close team modal">✖</button>">✖</button aria-label="<button class="..."onclick="...[39m
[37m                                                        ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L137 |[90m...ria-label="Close team modal">✖</button>">✖</button aria-label="<button class="..."onclick="this.close...[39m
[37m                                                        ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L137 |[90m...a-label="Close team modal">✖</button>">✖</button aria-label="<button class="..."onclick="this.closest...[39m
[37m                                                         ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L137 |[90m...odal">✖</button>">✖</button aria-label="<button class="..."onclick="this.closest('dialog').close()"ar...[39m
[37m                                                         ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L137 |[90m...').close()"aria-label="Close team modal">✖</button>">    <h2 class=">Meet the Team</h2>[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L137 |[90m....close()"aria-label="Close team modal">✖</button>">    <h2 class=">Meet the Team</h2>[39m
[37m                                                        ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L137 |[90m...ria-label="Close team modal">✖</button>">    <h2 class=">Meet the Team</h2>[39m
[37m                                                        ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L137 |[90m...abel="Close team modal">✖</button>">    <h2 class=">Meet the Team</h2>[39m
[37m                                                        ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L137 |[90m... team modal">✖</button>">    <h2 class=">Meet the Team</h2>[39m
[37m                                                        ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L137 |[90m...</button>">    <h2 class=">Meet the Team</h2>[39m
[37m                                                       ^ [31mTag must be paired, no start tag: [ </h2> ] (tag-pair)[39m
[37m      L138 |[90m    <video src="url_forstatic, filename=videos/atx-elite-hype.mp4"controls poster="url_forstatic, fil...[39m
[37m                ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L138 |[90m... filename=images/team-rings.webp"class="></video>[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L138 |[90m...filename=images/team-rings.webp"class="></video>[39m
[37m                                                       ^ [31mTag must be paired, no start tag: [ </video> ] (tag-pair)[39m
[37m      L139 |[90m    <p class=">Get to know our players, coaches, and what drives us. #ATXFamily</p>[39m
[37m                ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L139 |[90m    <p class=">Get to know our players, coaches, and what drives us. #ATXFamily</p>[39m
[37m                          ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L140 |[90m  </div>[39m
[37m              ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L141 |[90m</dialog>[39m
[37m            ^ [31mTag must be paired, no start tag: [ </dialog> ] (tag-pair)[39m
[37m      L144 |[90m<a[39m
[37m            ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L148 |[90m>[39m
[37m            ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L150 |[90m</a>[39m
[37m            ^ [31mTag must be paired, no start tag: [ </a> ] (tag-pair)[39m

   /home/cyberboyz/connectatx-fundraiser/app/templates/partials/mission_section.html
[37m      L18 |[90m<section[39m
[37m           ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L22 |[90m>[39m
[37m           ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L23 |[90m  <div class=">[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L23 |[90m  <div class=">[39m
[37m                         ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L1 |[90m from "macros/ui.html"import render_button[39m
[37m          ^ [31mDoctype must be declared before any non-comment content. (doctype-first)[39m
[37m      L25 |[90m    <h2[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L30 |[90m    >[39m
[37m               ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L32 |[90m    </h2>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </h2> ] (tag-pair)[39m
[37m      L34 |[90m    <ul[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L38 |[90m    >[39m
[37m               ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L40 |[90m      <li[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L48 |[90m      >[39m
[37m                 ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L50 |[90m        <span id="badge-tip- loop.index"class="></span>[39m
[37m                   ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L50 |[90m... <span id="badge-tip- loop.index"class="></span>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L50 |[90m...<span id="badge-tip- loop.index"class="></span>[39m
[37m                                                      ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L51 |[90m      </li>[39m
[37m                 ^ [31mTag must be paired, no start tag: [ </li> ] (tag-pair)[39m
[37m      L53 |[90m    </ul>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </ul> ] (tag-pair)[39m
[37m      L59 |[90m      </p>[39m
[37m                 ^ [31mTag must be paired, no start tag: [ </p> ] (tag-pair)[39m
[37m      L76 |[90m        <span class="> s.v</span>[39m
[37m                                     ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L90 |[90m      <span class=">gym access, travel, and academic support</span> for our youth.[39m
[37m                 ^ [31mTag must be paired, missing: [ </span></span> ], start tag match failed [ <span class=">gym access, travel, and academic support</span> for our youth.
    </div>
    <!-- Elite CTA Button -->
    <div class="> ] on line 90. (tag-pair)[39m
[37m      L97 |[90m    <p class=">[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L97 |[90m    <p class=">[39m
[37m                         ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L102 |[90m</section>[39m
[37m            ^ [31mTag must be paired, no start tag: [ </section> ] (tag-pair)[39m

   /home/cyberboyz/connectatx-fundraiser/app/templates/partials/newsletter.html
[37m      L1 |[90m<dialog[39m
[37m          ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L8 |[90m>[39m
[37m          ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L9 |[90m  <div[39m
[37m            ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L14 |[90m  >[39m
[37m             ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L1 |[90m<dialog[39m
[37m          ^ [31mDoctype must be declared before any non-comment content. (doctype-first)[39m
[37m      L16 |[90m    <button[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L21 |[90m    >[39m
[37m               ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L22 |[90m      <span aria-hidden="true"class=">&times;</span>[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L22 |[90m      <span aria-hidden="true"class=">&times;</span>[39m
[37m                                                ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L22 |[90m... <span aria-hidden="true"class=">&times;</span>[39m
[37m                                                      ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L23 |[90m    </button>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L26 |[90m    <div[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L31 |[90m    >[39m
[37m               ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L32 |[90m      <span id="newsletter-ball"class="aria-hidden="true">[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L32 |[90m...ewsletter-ball"class="aria-hidden="true">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L33 |[90m        <svg viewBox="0 0 48 48"fill="none"class="aria-hidden="true"aria-label="REVIEW_ME">          ...[39m
[37m                   ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L33 |[90m...aria-hidden="true"aria-label="REVIEW_ME">          <circle cx="24"cy="24"r="22"fill="#FBBF24"stroke="...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L33 |[90m...="true"aria-label="REVIEW_ME">          <circle cx="24"cy="24"r="22"fill="#FBBF24"stroke="#F59E0B"str...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L33 |[90m...FBBF24"stroke="#F59E0B"stroke-width="3"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L34 |[90m          <path d="M24 2v44M2 24h44"stroke="#78350F"stroke-width="2"/>[39m
[37m                     ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L34 |[90m... 24h44"stroke="#78350F"stroke-width="2"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L35 |[90m          <path d="M10 10c9 9 19 29 28 28M38 10C29 19 9 29 10 38"stroke="#92400E"stroke-width="2"/>[39m
[37m                     ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L35 |[90m... 10 38"stroke="#92400E"stroke-width="2"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L36 |[90m        </svg>[39m
[37m                   ^ [31mTag must be paired, no start tag: [ </svg> ] (tag-pair)[39m
[37m      L37 |[90m      </span>[39m
[37m                 ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L38 |[90m    </div>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L41 |[90m    <h2[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L44 |[90m    >[39m
[37m               ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L46 |[90m      <span class="aria-live="polite">[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L46 |[90m      <span class="aria-live="polite">[39m
[37m                                                ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L48 |[90m      </span>[39m
[37m                 ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L49 |[90m      <span[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L52 |[90m      >[39m
[37m                 ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L54 |[90m      </span>[39m
[37m                 ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L55 |[90m    </h2>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </h2> ] (tag-pair)[39m
[37m      L58 |[90m...class=">exclusive updates, game invites,</strong> and ways to help <strong> team.team_name or "Connec...[39m
[37m                                                      ^ [31mTag must be paired, no start tag: [ </strong> ] (tag-pair)[39m
[37m      L59 |[90m      <span class=">One email a month, no spam.</span>[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L59 |[90m      <span class=">One email a month, no spam.</span>[39m
[37m                              ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L59 |[90m...span class=">One email a month, no spam.</span>[39m
[37m                                                      ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L63 |[90m    <form[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L72 |[90m    >[39m
[37m               ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L73 |[90m      <span id="newsletter-desc"class=">Email address field and subscribe button</span>[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L73 |[90m      <span id="newsletter-desc"class=">Email address field and subscribe button</span>[39m
[37m                                                  ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L73 |[90m...Email address field and subscribe button</span>[39m
[37m                                                      ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L74 |[90m      <div class=">[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L74 |[90m      <div class=">[39m
[37m                             ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L75 |[90m        <input[39m
[37m                   ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L87 |[90m        />[39m
[37m                    ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L88 |[90m        <span[39m
[37m                   ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L91 |[90m        >🏀</span>[39m
[37m                   ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L91 |[90m        >🏀</span>[39m
[37m                        ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L92 |[90m      </div>[39m
[37m                 ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L95 |[90m      <input[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L103 |[90m      >[39m
[37m                  ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L106 |[90m      <p[39m
[37m                  ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L111 |[90m      ></p>[39m
[37m                  ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L111 |[90m      ></p>[39m
[37m                   ^ [31mTag must be paired, no start tag: [ </p> ] (tag-pair)[39m
[37m      L114 |[90m      <button[39m
[37m                  ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L118 |[90m      >[39m
[37m                  ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L120 |[90m        <span[39m
[37m                    ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L124 |[90m        >🏆🎉</span>[39m
[37m                    ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L124 |[90m        >🏆🎉</span>[39m
[37m                             ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L125 |[90m      </button>[39m
[37m                  ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L128 |[90m      <p[39m
[37m                  ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L132 |[90m      >[39m
[37m                  ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L134 |[90m      </p>[39m
[37m                  ^ [31mTag must be paired, no start tag: [ </p> ] (tag-pair)[39m
[37m      L137 |[90m      <button[39m
[37m                  ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L142 |[90m      >[39m
[37m                  ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L144 |[90m      </button>[39m
[37m                  ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L145 |[90m    </form>[39m
[37m                ^ [31mTag must be paired, no start tag: [ </form> ] (tag-pair)[39m
[37m      L146 |[90m  </div>[39m
[37m              ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L147 |[90m</dialog>[39m
[37m            ^ [31mTag must be paired, no start tag: [ </dialog> ] (tag-pair)[39m

   /home/cyberboyz/connectatx-fundraiser/app/templates/partials/program_stats_and_calendar.html
[37m      L14 |[90m<section id="program-stats-events"class=">[39m
[37m           ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L14 |[90m...section id="program-stats-events"class=">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L1 |[90m# =================== Elite Program Stats + Events Calendar Partial =================== #[39m
[37m          ^ [31mDoctype must be declared before any non-comment content. (doctype-first)[39m
[37m      L25 |[90m    <table[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L28 |[90m    >[39m
[37m               ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L31 |[90m          <th class=">Date</th>[39m
[37m                                     ^ [31mTag must be paired, no start tag: [ </th> ] (tag-pair)[39m
[37m      L53 |[90m            <td class="aria-label="Event result">[39m
[37m                       ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L53 |[90m...    <td class="aria-label="Event result">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L58 |[90m            </td>[39m
[37m                       ^ [31mTag must be paired, no start tag: [ </td> ] (tag-pair)[39m
[37m      L36 |[90m          <th class=">Sponsor</th>[39m
[37m                     ^ [31mTag must be paired, missing: [ </th> ], start tag match failed [ <th class=">Sponsor</th>
        </tr>
      </thead>
      <tbody>
 for event in events
 set row_classes =
transition-colors,
            event.is_upcoming andbg-yellow-400/10 text-yellow-200 font-bold,
W in event.result andbg-green-500/10 text-green-200,
L in event.result andbg-red-600/10 text-red-100,
            notevent.is_upcoming orW in event.result orL in event.result andbg-zinc-950/90
 | select | join
          <tr class="> ] on line 36. (tag-pair)[39m
[37m      L73 |[90m      </tbody>[39m
[37m                 ^ [31mTag must be paired, no start tag: [ </tbody> ] (tag-pair)[39m
[37m      L74 |[90m    </table>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </table> ] (tag-pair)[39m
[37m      L75 |[90m    <div class=">[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L75 |[90m    <div class=">[39m
[37m                           ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L76 |[90m      <a[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L79 |[90m      >[39m
[37m                 ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L81 |[90m      </a>[39m
[37m                 ^ [31mTag must be paired, no start tag: [ </a> ] (tag-pair)[39m
[37m      L82 |[90m    </div>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L83 |[90m  </div>[39m
[37m             ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L84 |[90m</section>[39m
[37m           ^ [31mTag must be paired, no start tag: [ </section> ] (tag-pair)[39m
[37m      L139 |[90m[39m
[37m            ^ [31mTag must be paired, missing: [ </thead></h2> ], open tag match failed [ <thead> ] on line 29. (tag-pair)[39m

   /home/cyberboyz/connectatx-fundraiser/app/templates/partials/sponsor_form.html
[37m      L5 |[90m<form[39m
[37m          ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L12 |[90m>[39m
[37m           ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L13 |[90m  <h2 id="sponsor-form-heading"class=">[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L13 |[90m  <h2 id="sponsor-form-heading"class=">[39m
[37m                                                 ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L1 |[90m# ============================================================================= #[39m
[37m          ^ [31mDoctype must be declared before any non-comment content. (doctype-first)[39m
[37m      L15 |[90m  </h2>[39m
[37m             ^ [31mTag must be paired, no start tag: [ </h2> ] (tag-pair)[39m
[37m      L20 |[90m    <label for="donor-name"class=">[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L20 |[90m    <label for="donor-name"class=">[39m
[37m                                             ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L21 |[90m      Name or Company <span class=">*</span>[39m
[37m                                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L21 |[90m      Name or Company <span class=">*</span>[39m
[37m                                              ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L21 |[90m      Name or Company <span class=">*</span>[39m
[37m                                                ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L22 |[90m    </label>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </label> ] (tag-pair)[39m
[37m      L29 |[90m        <p class="> form.name.errors0</p>[39m
[37m                   ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L29 |[90m        <p class="> form.name.errors0</p>[39m
[37m                             ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L29 |[90m        <p class="> form.name.errors0</p>[39m
[37m                                                ^ [31mTag must be paired, no start tag: [ </p> ] (tag-pair)[39m
[37m      L32 |[90m      <input type="text"name="name"id="donor-name"required class="placeholder="Your Name or Company"/...[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L32 |[90m...me or Company"/ aria-label="Enter value"> endif[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L37 |[90m    <label for="donor-email"class=">[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L37 |[90m    <label for="donor-email"class=">[39m
[37m                                              ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L38 |[90m      Email <span class=">*</span>[39m
[37m                       ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L38 |[90m      Email <span class=">*</span>[39m
[37m                                    ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L38 |[90m      Email <span class=">*</span>[39m
[37m                                      ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L39 |[90m    </label>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </label> ] (tag-pair)[39m
[37m      L46 |[90m        <p class="> form.email.errors0</p>[39m
[37m                   ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L46 |[90m        <p class="> form.email.errors0</p>[39m
[37m                             ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L46 |[90m        <p class="> form.email.errors0</p>[39m
[37m                                                 ^ [31mTag must be paired, no start tag: [ </p> ] (tag-pair)[39m
[37m      L49 |[90m      <input type="email"name="email"id="donor-email"required class="placeholder="your@email.com"/ ar...[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L49 |[90m...our@email.com"/ aria-label="Enter value"> endif[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L54 |[90m    <label for="donation-amount"class=">[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L54 |[90m    <label for="donation-amount"class=">[39m
[37m                                                  ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L58 |[90m      <span class=">$</span>[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L58 |[90m      <span class=">$</span>[39m
[37m                              ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L65 |[90m        <input type="number"min="5"step="1"name="amount"id="donation-amount-form-2"[39m
[37m                   ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L67 |[90m          placeholder="50"required />[39m
[37m                                               ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L70 |[90m    <div class=">[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L70 |[90m    <div class=">[39m
[37m                           ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L72 |[90m      <button[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L77 |[90m      >[39m
[37m                 ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L79 |[90m      </button>[39m
[37m                 ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L81 |[90m    </div>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L83 |[90m      <span class=">Tip:</span> $50 covers a team jersey. $150 sponsors a week of practice![39m
[37m                                   ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L92 |[90m    <div class=">[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L92 |[90m    <div class=">[39m
[37m                           ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L93 |[90m      <input type="radio"id="pay-stripe"name="payment_method"value="stripe"checked class="/ aria-labe...[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L93 |[90m...hecked class="/ aria-label="Enter value">      <label for="pay-stripe"class=">💳 Credit/Debit CardStr...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L93 |[90m...class="/ aria-label="Enter value">      <label for="pay-stripe"class=">💳 Credit/Debit CardStripe</la...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L93 |[90m...ue">      <label for="pay-stripe"class=">💳 Credit/Debit CardStripe</label>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L93 |[90m...tripe"class=">💳 Credit/Debit CardStripe</label>[39m
[37m                                                        ^ [31mTag must be paired, no start tag: [ </label> ] (tag-pair)[39m
[37m      L94 |[90m      <input type="radio"id="pay-paypal"name="payment_method"value="paypal"class="/ aria-label="Enter...[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L94 |[90m...paypal"class="/ aria-label="Enter value">      <label for="pay-paypal"class=">🅿️ PayPal</label>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L94 |[90m...class="/ aria-label="Enter value">      <label for="pay-paypal"class=">🅿️ PayPal</label>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L94 |[90m...ue">      <label for="pay-paypal"class=">🅿️ PayPal</label>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L94 |[90m...label for="pay-paypal"class=">🅿️ PayPal</label>[39m
[37m                                                         ^ [31mTag must be paired, no start tag: [ </label> ] (tag-pair)[39m
[37m      L95 |[90m    </div>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L96 |[90m  </div>[39m
[37m             ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L99 |[90m  <div class=">[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L99 |[90m  <div class=">[39m
[37m                         ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L100 |[90m    <button[39m
[37m                ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L105 |[90m    >[39m
[37m                ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L107 |[90m    </button>[39m
[37m                ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L108 |[90m    <p class=">[39m
[37m                ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L108 |[90m    <p class=">[39m
[37m                          ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L111 |[90m    <div id="impact-message"class="></div>[39m
[37m                ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L111 |[90m    <div id="impact-message"class="></div>[39m
[37m                                               ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L111 |[90m    <div id="impact-message"class="></div>[39m
[37m                                                ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L112 |[90m  </div>[39m
[37m              ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L113 |[90m</form>[39m
[37m            ^ [31mTag must be paired, no start tag: [ </form> ] (tag-pair)[39m

   /home/cyberboyz/connectatx-fundraiser/app/templates/partials/sponsor_spotlight.html
[37m      L1 |[90m# --- Sponsor Card Macro --- #[39m
[37m          ^ [31mDoctype must be declared before any non-comment content. (doctype-first)[39m
[37m      L28 |[90m      <span class=">✨</span>[39m
[37m                                 ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L30 |[90m if sponsor.url<a href="sponsor.url"target="_blank"rel="noopener sponsored"tabindex="-1"aria-label="V...[39m
[37m                          ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L30 |[90m...ndex="-1"aria-label="Visit sponsor.name"> endif[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L31 |[90m      <img src="logo_src"alt="sponsor.name logo"width="96"height="96"[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L33 |[90m        loading="lazy"decoding="async"/>[39m
[37m                                                  ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L34 |[90m if sponsor.url</a> endif[39m
[37m                          ^ [31mTag must be paired, no start tag: [ </a> ] (tag-pair)[39m
[37m      L36 |[90m...<span class=">$ sponsor.amount|int|comma</span>[39m
[37m                                                      ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L37 |[90m    <span class=">[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L37 |[90m    <span class=">[39m
[37m                            ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L39 |[90m    </span>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L40 |[90m    <div id="tooltip- idx"role="tooltip"[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L41 |[90m      class=">[39m
[37m                        ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L43 |[90m    </div>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L35 |[90m    <h3 class="> sponsor.name</h3>[39m
[37m               ^ [31mTag must be paired, missing: [ </h3> ], start tag match failed [ <h3 class="> sponsor.name</h3>
    <span class="> ] on line 35. (tag-pair)[39m
[37m      L48 |[90m<section[39m
[37m           ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L54 |[90m>[39m
[37m           ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L55 |[90m  <h2[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L58 |[90m  >[39m
[37m             ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L60 |[90m    <span class="aria-live="polite"aria-atomic="true">[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L60 |[90m...ss="aria-live="polite"aria-atomic="true">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L62 |[90m    </span>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L63 |[90m  </h2>[39m
[37m             ^ [31mTag must be paired, no start tag: [ </h2> ] (tag-pair)[39m
[37m      L76 |[90m  <div class="role="list"aria-label="Top Sponsors">[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L76 |[90m...ss="role="list"aria-label="Top Sponsors">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L80 |[90m...sponsors|length if demo_sponsors|length < total_slots else total_slots[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L81 |[90m      <div class="role="listitem"tabindex="0"aria-label="Available sponsorship spot">[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L81 |[90m..."aria-label="Available sponsorship spot">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L82 |[90m        <span class="aria-hidden="true">✨</span>[39m
[37m                   ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L82 |[90m        <span class="aria-hidden="true">✨</span>[39m
[37m                                                  ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L82 |[90m...       <span class="aria-hidden="true">✨</span>[39m
[37m                                                       ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L83 |[90m        <span class=">This spot is waiting for you!</span>[39m
[37m                   ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L83 |[90m        <span class=">This spot is waiting for you!</span>[39m
[37m                                ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L83 |[90m...an class=">This spot is waiting for you!</span>[39m
[37m                                                      ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L84 |[90m        <button onclick="openSponsorModal"class="aria-label="Become a Sponsor"type="button">[39m
[37m                   ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L84 |[90m...ia-label="Become a Sponsor"type="button">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L86 |[90m        </button>[39m
[37m                   ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L87 |[90m      </div>[39m
[37m                 ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L89 |[90m  </div>[39m
[37m             ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L92 |[90m  <div class="aria-label="All sponsor logos">[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L92 |[90m...iv class="aria-label="All sponsor logos">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L93 |[90m    <img src="demo_sponsor.logo"alt="ESPN logo"title="ESPNDemo Sponsor"class="loading="lazy"decoding=...[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L93 |[90m...r"class="loading="lazy"decoding="async"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L99 |[90m      <img src="logo_src"alt="sponsor.name orSponsor logo"title="sponsor.name orSponsor"class="loadin...[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L99 |[90m...r"class="loading="lazy"decoding="async"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L101 |[90m    <span class=">+ Your Brand Here</span>[39m
[37m                ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L101 |[90m    <span class=">+ Your Brand Here</span>[39m
[37m                             ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L101 |[90m    <span class=">+ Your Brand Here</span>[39m
[37m                                               ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L102 |[90m  </div>[39m
[37m              ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L103 |[90m</section>[39m
[37m            ^ [31mTag must be paired, no start tag: [ </section> ] (tag-pair)[39m

   /home/cyberboyz/connectatx-fundraiser/app/templates/partials/sponsor_wall.html
[37m      L6 |[90m<section[39m
[37m          ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L17 |[90m>[39m
[37m           ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L19 |[90m  <header class=">[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L19 |[90m  <header class=">[39m
[37m                            ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L20 |[90m    <h2 id="sponsor-wall-title"class=">[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L20 |[90m    <h2 id="sponsor-wall-title"class=">[39m
[37m                                                 ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L21 |[90m      <span class=">🙌</span> Meet Our Champions[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L21 |[90m      <span class=">🙌</span> Meet Our Champions[39m
[37m                              ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L1 |[90m# ==============================[39m
[37m          ^ [31mDoctype must be declared before any non-comment content. (doctype-first)[39m
[37m      L21 |[90m      <span class=">🙌</span> Meet Our Champions[39m
[37m                                   ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L22 |[90m    </h2>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </h2> ] (tag-pair)[39m
[37m      L23 |[90m    <button id="sponsor-wall-close"aria-label="Close sponsor wall"[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L24 |[90m      class=">[39m
[37m                        ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L26 |[90m    </button>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L27 |[90m  </header>[39m
[37m             ^ [31mTag must be paired, no start tag: [ </header> ] (tag-pair)[39m
[37m      L30 |[90m  <div id="donation-ticker"class=">[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L30 |[90m  <div id="donation-ticker"class=">[39m
[37m                                             ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L36 |[90m  </div>[39m
[37m             ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L44 |[90m      </span>[39m
[37m                 ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L56 |[90m    <button type="button"class="[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L57 |[90m      data-type="all">All-Time</button>[39m
[37m                                ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L57 |[90m      data-type="all">All-Time</button>[39m
[37m                                         ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L58 |[90m    <button type="button"class="[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L59 |[90m      data-type="month">This Month</button>[39m
[37m                                  ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L59 |[90m      data-type="month">This Month</button>[39m
[37m                                             ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L51 |[90m    <span class=">Directly funds local youth programs!</span>[39m
[37m               ^ [31mTag must be paired, missing: [ </span> ], start tag match failed [ <span class=">Directly funds local youth programs!</span>
  </div>

# --- 4. Leaderboard Toggle --- #
  <div class="> ] on line 51. (tag-pair)[39m
[37m      L63 |[90m  <div class=">[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L63 |[90m  <div class=">[39m
[37m                         ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L67 |[90m  </div>[39m
[37m             ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L70 |[90m  <div id="sponsor-wall-list"[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L72 |[90m...st"tabindex="0"aria-label="Sponsor List">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L77 |[90m...sorted|length if sponsors_sorted|length < 12 else 0[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L79 |[90m      <div[39m
[37m                 ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L86 |[90m      >[39m
[37m                 ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L87 |[90m        <span class="aria-hidden="true">✨</span>[39m
[37m                   ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L87 |[90m        <span class="aria-hidden="true">✨</span>[39m
[37m                                                  ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L87 |[90m...       <span class="aria-hidden="true">✨</span>[39m
[37m                                                       ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L90 |[90m        <button type="button"class="aria-label="Become a Sponsor"tabindex="-1">[39m
[37m                   ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L90 |[90m...ia-label="Become a Sponsor"tabindex="-1">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L92 |[90m        </button>[39m
[37m                   ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L93 |[90m      </div>[39m
[37m                 ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L95 |[90m  </div>[39m
[37m             ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L98 |[90m  <footer class=">[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L98 |[90m  <footer class=">[39m
[37m                            ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L99 |[90m    <button type="button"onclick="openSponsorModal"[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L101 |[90m      aria-label="Become a Sponsor">[39m
[37m                                               ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L103 |[90m    </button>[39m
[37m                ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L106 |[90m      <button onclick="shareSponsorWallx"aria-label="Share on X"class=">[39m
[37m                  ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L106 |[90m...nsorWallx"aria-label="Share on X"class=">[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L107 |[90m        <svg viewBox="0 0 24 24"width="20"height="20"aria-label="REVIEW_ME"><!-- X icon -- aria-label...[39m
[37m                    ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L107 |[90m...th="20"height="20"aria-label="REVIEW_ME"><!-- X icon -- aria-label="REVIEW_ME"></svg aria-label="REVI...[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L107 |[90m..."><!-- X icon -- aria-label="REVIEW_ME"></svg aria-label="REVIEW_ME">      </button>[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L107 |[90m..."REVIEW_ME"></svg aria-label="REVIEW_ME">      </button>[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L107 |[90m..._ME"></svg aria-label="REVIEW_ME">      </button>[39m
[37m                                                       ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L108 |[90m      <button onclick="shareSponsorWallfb"aria-label="Share on Facebook"class=">[39m
[37m                  ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L108 |[90m...fb"aria-label="Share on Facebook"class=">[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L109 |[90m        <svg viewBox="0 0 24 24"width="20"height="20"aria-label="REVIEW_ME"><!-- FB icon -- aria-labe...[39m
[37m                    ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L109 |[90m...th="20"height="20"aria-label="REVIEW_ME"><!-- FB icon -- aria-label="REVIEW_ME"></svg aria-label="REV...[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L109 |[90m...><!-- FB icon -- aria-label="REVIEW_ME"></svg aria-label="REVIEW_ME">      </button>[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L109 |[90m..."REVIEW_ME"></svg aria-label="REVIEW_ME">      </button>[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L109 |[90m..._ME"></svg aria-label="REVIEW_ME">      </button>[39m
[37m                                                       ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L110 |[90m      <button onclick="shareSponsorWallln"aria-label="Share on LinkedIn"class=">[39m
[37m                  ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L110 |[90m...ln"aria-label="Share on LinkedIn"class=">[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L111 |[90m        <svg viewBox="0 0 24 24"width="20"height="20"aria-label="REVIEW_ME"><!-- LinkedIn icon -- ari...[39m
[37m                    ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L111 |[90m...th="20"height="20"aria-label="REVIEW_ME"><!-- LinkedIn icon -- aria-label="REVIEW_ME"></svg aria-labe...[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L111 |[90m...LinkedIn icon -- aria-label="REVIEW_ME"></svg aria-label="REVIEW_ME">      </button>[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L111 |[90m..."REVIEW_ME"></svg aria-label="REVIEW_ME">      </button>[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L111 |[90m..._ME"></svg aria-label="REVIEW_ME">      </button>[39m
[37m                                                       ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L113 |[90m  </footer>[39m
[37m              ^ [31mTag must be paired, no start tag: [ </footer> ] (tag-pair)[39m
[37m      L114 |[90m</section>[39m
[37m            ^ [31mTag must be paired, no start tag: [ </section> ] (tag-pair)[39m
[37m      L123 |[90m  🙌 <span class=">Sponsors</span>[39m
[37m                                         ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L124 |[90m  <span id="sponsor-nudge-dot"class="></span>[39m
[37m              ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L124 |[90m  <span id="sponsor-nudge-dot"class="></span>[39m
[37m                                                 ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L124 |[90m  <span id="sponsor-nudge-dot"class="></span>[39m
[37m                                                  ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m

   /home/cyberboyz/connectatx-fundraiser/app/templates/partials/testimonial_popover.html
[37m      L5 |[90m<section[39m
[37m          ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L13 |[90m>[39m
[37m           ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L1 |[90m set challenge = challenge if challenge is defined and challenge else[39m
[37m          ^ [31mDoctype must be declared before any non-comment content. (doctype-first)[39m
[37m      L15 |[90m  <div class=">[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L15 |[90m  <div class=">[39m
[37m                         ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L16 |[90m    <svg width="24"height="24"viewBox="0 0 24 24"fill="none"aria-label="REVIEW_ME">      <polygon poi...[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L16 |[90m... 24 24"fill="none"aria-label="REVIEW_ME">      <polygon points="12,0 24,24 0,24"fill="#facc15"opacity...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L16 |[90m...fill="none"aria-label="REVIEW_ME">      <polygon points="12,0 24,24 0,24"fill="#facc15"opacity="0.8"/...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L16 |[90m... 24,24 0,24"fill="#facc15"opacity="0.8"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L17 |[90m    </svg>[39m
[37m               ^ [31mTag must be paired, no start tag: [ </svg> ] (tag-pair)[39m
[37m      L18 |[90m  </div>[39m
[37m             ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L22 |[90m  <div class="> detail</div>[39m
[37m                                 ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L25 |[90m  <button[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L30 |[90m  >[39m
[37m             ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L32 |[90m  </button>[39m
[37m             ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L33 |[90m</section>[39m
[37m           ^ [31mTag must be paired, no start tag: [ </section> ] (tag-pair)[39m
[37m      L96 |[90m[39m
[37m           ^ [31mTag must be paired, missing: [ </strong> ], open tag match failed [ <strong class="> author</strong>
  <div class="> ] on line 21. (tag-pair)[39m

   /home/cyberboyz/connectatx-fundraiser/app/templates/partials/tiers.html
[37m      L1 |[90m<section[39m
[37m          ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L7 |[90m>[39m
[37m          ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L8 |[90m  <h2[39m
[37m            ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L13 |[90m  >[39m
[37m             ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L1 |[90m<section[39m
[37m          ^ [31mDoctype must be declared before any non-comment content. (doctype-first)[39m
[37m      L15 |[90m  </h2>[39m
[37m             ^ [31mTag must be paired, no start tag: [ </h2> ] (tag-pair)[39m
[37m      L25 |[90m  <div class="role="list">[39m
[37m             ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L25 |[90m  <div class="role="list">[39m
[37m                                    ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L29 |[90m    <article[39m
[37m               ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L40 |[90m    >[39m
[37m               ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L46 |[90m              <span class="aria-hidden="true"> tier.emoji</span>[39m
[37m                         ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L46 |[90m...         <span class="aria-hidden="true"> tier.emoji</span>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L46 |[90m...an class="aria-hidden="true"> tier.emoji</span>[39m
[37m                                                      ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L48 |[90m            <div class=">[39m
[37m                       ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L48 |[90m            <div class=">[39m
[37m                                   ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L49 |[90m              <h3 id="tier- loop.index-title"class=">[39m
[37m                         ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L49 |[90m...  <h3 id="tier- loop.index-title"class=">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L51 |[90m              </h3>[39m
[37m                         ^ [31mTag must be paired, no start tag: [ </h3> ] (tag-pair)[39m
[37m      L57 |[90m...             <span class=">$ tier.amount</span>[39m
[37m                                                      ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L76 |[90m            <ul id="tier- loop.index-benefits"class=">[39m
[37m                       ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L76 |[90m...ul id="tier- loop.index-benefits"class=">[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L78 |[90m              <li class=">[39m
[37m                         ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L78 |[90m              <li class=">[39m
[37m                                    ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L79 |[90m                <svg class="viewBox="0 0 20 20"fill="currentColor"aria-hidden="true"aria-label="REVIE...[39m
[37m                           ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L79 |[90m...aria-hidden="true"aria-label="REVIEW_ME">                  <path fill-rule="evenodd"d="M16.707 5.293a...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L79 |[90m...ria-label="REVIEW_ME">                  <path fill-rule="evenodd"d="M16.707 5.293a1 1 0 010 1.414l-7....[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L79 |[90m...43a1 1 0 011.414 0z"clip-rule="evenodd"/>[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L80 |[90m                </svg>[39m
[37m                           ^ [31mTag must be paired, no start tag: [ </svg> ] (tag-pair)[39m
[37m      L82 |[90m              </li>[39m
[37m                         ^ [31mTag must be paired, no start tag: [ </li> ] (tag-pair)[39m
[37m      L84 |[90m            </ul>[39m
[37m                       ^ [31mTag must be paired, no start tag: [ </ul> ] (tag-pair)[39m
[37m      L95 |[90m                <svg class="viewBox="0 0 20 20"fill="currentColor"aria-hidden="true"aria-label="REVIE...[39m
[37m                           ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L95 |[90m...aria-hidden="true"aria-label="REVIEW_ME">                  <path d="M12.293 4.293a1 1 0 011.414 0l4 4...[39m
[37m                                                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L96 |[90m                </svg>[39m
[37m                           ^ [31mTag must be paired, no start tag: [ </svg> ] (tag-pair)[39m
[37m      L97 |[90m              </button>[39m
[37m                         ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L106 |[90m          <span class="aria-hidden="true"> tier.emoji</span>[39m
[37m                      ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L106 |[90m...         <span class="aria-hidden="true"> tier.emoji</span>[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L98 |[90m              <p class=">[39m
[37m                         ^ [31mTag must be paired, missing: [ </p></div> ], start tag match failed [ <p class=">
                Limited spots • Quick sign-up
              </p>
            </div>
          </div>
        </div>
        <!-- Card Back -->
        <div class="> ] on line 98. (tag-pair)[39m
[37m      L107 |[90m          <h3 class="> tier.title Tier</h3>[39m
[37m                      ^ [31mTag must be paired, missing: [ </h3> ], start tag match failed [ <h3 class="> tier.title Tier</h3>
          <p class="> ] on line 107. (tag-pair)[39m
[37m      L111 |[90m          <button[39m
[37m                      ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L116 |[90m          >[39m
[37m                      ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L118 |[90m            <svg class="viewBox="0 0 20 20"fill="currentColor"aria-hidden="true"aria-label="REVIEW_ME...[39m
[37m                        ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L118 |[90m...aria-hidden="true"aria-label="REVIEW_ME">              <path d="M12.293 4.293a1 1 0 011.414 0l4 4a1 1...[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L119 |[90m            </svg>[39m
[37m                        ^ [31mTag must be paired, no start tag: [ </svg> ] (tag-pair)[39m
[37m      L120 |[90m          </button>[39m
[37m                      ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L122 |[90m      </div>[39m
[37m                  ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L123 |[90m    </article>[39m
[37m                ^ [31mTag must be paired, no start tag: [ </article> ] (tag-pair)[39m
[37m      L125 |[90m  </div>[39m
[37m              ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L130 |[90m      Every sponsorship powers <span class=">gym access, travel, and academic support</span> for our ...[39m
[37m                                           ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L130 |[90m...  Every sponsorship powers <span class=">gym access, travel, and academic support</span> for our team...[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L130 |[90m...gym access, travel, and academic support</span> for our team.[39m
[37m                                                       ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L131 |[90m    </p>[39m
[37m                ^ [31mTag must be paired, no start tag: [ </p> ] (tag-pair)[39m
[37m      L135 |[90m  <button[39m
[37m              ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L142 |[90m  >[39m
[37m              ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L143 |[90m    <span id="tiers-faq-icon"class="aria-hidden="true">▶</span>[39m
[37m                ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L143 |[90m...tiers-faq-icon"class="aria-hidden="true">▶</span>[39m
[37m                                                       ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L143 |[90m...ers-faq-icon"class="aria-hidden="true">▶</span>[39m
[37m                                                        ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L144 |[90m    <span class=">Frequently Asked Questions</span>[39m
[37m                ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L144 |[90m    <span class=">Frequently Asked Questions</span>[39m
[37m                             ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L144 |[90m...<span class=">Frequently Asked Questions</span>[39m
[37m                                                       ^ [31mTag must be paired, no start tag: [ </span> ] (tag-pair)[39m
[37m      L145 |[90m  </button>[39m
[37m              ^ [31mTag must be paired, no start tag: [ </button> ] (tag-pair)[39m
[37m      L146 |[90m  <div[39m
[37m              ^ [31mSpecial characters must be escaped : [ < ]. (spec-char-escape)[39m
[37m      L151 |[90m  >[39m
[37m              ^ [31mSpecial characters must be escaped : [ > ]. (spec-char-escape)[39m
[37m      L155 |[90m  </div>[39m
[37m              ^ [31mTag must be paired, no start tag: [ </div> ] (tag-pair)[39m
[37m      L156 |[90m</section>[39m
[37m            ^ [31mTag must be paired, no start tag: [ </section> ] (tag-pair)[39m

Scanned 29 files, found 1233 errors in 28 files (73 ms)
