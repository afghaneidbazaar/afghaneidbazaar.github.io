import os
import re

html_files = [f for f in os.listdir('.') if f.endswith('.html')]

with open('index.html', 'r', encoding='utf-8') as f:
    index_content = f.read()

master_nav_match = re.search(r'<body[^>]*>\s*(.*?)\s*<main[^>]*>', index_content, flags=re.DOTALL)
if not master_nav_match:
    print("Could not find master nav in index.html")
    exit(1)

master_nav = master_nav_match.group(1)

# Desktop Classes
active_dp = "text-primary font-bold border-b-2 border-primary pb-1"
inactive_dp = "text-background opacity-80 hover:text-primary transition-colors duration-300"

# Mobile Classes
active_mob = "text-primary font-bold border-l-4 border-primary pl-4 text-xl"
inactive_mob = "text-background opacity-80 hover:text-primary transition-colors pl-4 text-xl"

# 1. Neutralize master nav
neutral_nav = master_nav.replace(
    f'<a class="{active_dp}" href="index.html">',
    f'<a class="{inactive_dp}" href="index.html">'
).replace(
    f'<a class="{active_mob}" href="index.html">',
    f'<a class="{inactive_mob}" href="index.html">'
)

for file in html_files:
    if file == 'index.html':
        continue
        
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    personalized_nav = neutral_nav.replace(
        f'<a class="{inactive_dp}" href="{file}">',
        f'<a class="{active_dp}" href="{file}">'
    ).replace(
        f'<a class="{inactive_mob}" href="{file}">',
        f'<a class="{active_mob}" href="{file}">'
    )
    
    new_content = re.sub(
        r'(<body[^>]*>)\s*.*?\s*(<main[^>]*>)',
        lambda m: f"{m.group(1)}\n{personalized_nav}\n{m.group(2)}",
        content,
        count=1,
        flags=re.DOTALL
    )
    
    if new_content != content:
        with open(file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Synced responsive nav layout to {file}")

print("Done synchronizing responsive navigations globally.")
