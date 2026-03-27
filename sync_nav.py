import os
import re

html_files = [f for f in os.listdir('.') if f.endswith('.html')]

# 1. Read index.html to get the master nav
with open('index.html', 'r', encoding='utf-8') as f:
    index_content = f.read()

# Extract exactly everything between <body> and <main> from index.html
master_nav_match = re.search(r'<body[^>]*>\s*(.*?)\s*<main[^>]*>', index_content, flags=re.DOTALL)
if not master_nav_match:
    print("Could not find master nav in index.html")
    exit(1)

master_nav = master_nav_match.group(1)

active_class = "text-primary font-bold border-b-2 border-primary pb-1"
inactive_class = "text-background opacity-80 hover:text-primary transition-colors duration-300"

# Neutralize the master nav (make all links inactive) by stripping Home's active class
neutral_nav = master_nav.replace(
    f'<a class="{active_class}" href="index.html">',
    f'<a class="{inactive_class}" href="index.html">'
)

for file in html_files:
    if file == 'index.html':
        continue # index.html already has the perfect layout

    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Personalize the neutral nav for this specific file
    personalized_nav = neutral_nav
    target_link = f'<a class="{inactive_class}" href="{file}">'
    replacement_link = f'<a class="{active_class}" href="{file}">'
    
    personalized_nav = personalized_nav.replace(target_link, replacement_link)
    
    # Inject it into the file: replacing whatever was between <body> and <main>
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
        print(f"Synced nav layout to {file}")

print("Done synchronizing top navigations globally.")
