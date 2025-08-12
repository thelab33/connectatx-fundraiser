import glob
import shutil
from bs4 import BeautifulSoup

# Patch all HTML/Jinja files in templates/
for path in glob.glob('templates/**/*.html', recursive=True) + glob.glob('templates/**/*.jinja2', recursive=True):
    backup = path + '.bak'
    shutil.copyfile(path, backup)

    with open(path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # 1. Elite main container
    main = soup.find('main')
    if main and 'container' not in main.get('class', []):
        main['class'] = (main.get('class', []) +
                         ['container', 'mx-auto', 'max-w-3xl', 'px-4', 'md:px-8', 'py-6'])

    # 2. Pro polish: upgrade hero/card/content sections
    for tag in soup.find_all(['section', 'div']):
        classes = tag.get('class', [])
        if any(x in classes for x in [
            'hero', 'card', 'content', 'about', 'stats', 'sponsor', 'wall'
        ]):
            tag['class'] = list(set(classes + [
                'rounded-3xl', 'bg-zinc-900/95', 'shadow-xl', 'mb-10', 'p-6', 'md:p-8'
            ]))

    # 3. Readable text in <p>
    for p in soup.find_all('p'):
        p['class'] = list(set(p.get('class', []) + [
            'text-yellow-100', 'mb-3', 'text-base', 'leading-relaxed'
        ]))

    with open(path, 'w', encoding='utf-8') as f:
        f.write(str(soup))

    print(f"✅ Elite SaaS polish applied to {path} (backup: {backup})")
