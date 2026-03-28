import os
import json
import re
from bs4 import BeautifulSoup, NavigableString

def has_direct_text(tag):
    for child in tag.children:
        if isinstance(child, NavigableString):
            if re.search(r'[A-Za-z0-9]', str(child)):
                return True
    return False

def has_i18n_parent(tag):
    for parent in tag.parents:
        if parent.has_attr('data-i18n'):
            return True
    return False

i18n_dict = {}
counter = {}

# REMOVED div, article, section, etc. Only leaf text nodes.
tags_to_check = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'button', 'a', 'label', 'li', 'td', 'th']

# We treat span very carefully, if it's a structural wrapper we avoid it, but typically we want it.
# Actually, if a 'span' is inside an 'a', and the 'a' has text, the 'a' gets tagged and the span is part of innerHTML.
# That is perfect. So we add span, but only tag it if no parent is tagged.
tags_to_check.append('span')

for filename in os.listdir('.'):
    if filename.endswith('.html'):
        with open(filename, 'r', encoding='utf-8') as f:
            html = f.read()
            
        soup = BeautifulSoup(html, 'html.parser')
        page_name = filename.replace('.html', '')
        if page_name not in counter:
            counter[page_name] = 0
            
        for tag in soup.find_all(True):
            if tag.has_attr('data-i18n'):
                key = tag['data-i18n']
                i18n_dict[key] = tag.decode_contents().strip()
                
        for tag_name in tags_to_check:
            for tag in soup.find_all(tag_name):
                if tag.has_attr('data-i18n'):
                    continue
                if has_i18n_parent(tag):
                    continue
                if tag.has_attr('translate') and tag['translate'] == 'no':
                    continue
                classes = tag.get('class', [])
                if 'notranslate' in classes or 'material-symbols-outlined' in classes:
                    continue
                if not has_direct_text(tag):
                    continue
                    
                counter[page_name] += 1
                key = f"{page_name}.{tag_name}.{counter[page_name]}"
                
                tag['data-i18n'] = key
                val = tag.decode_contents().strip()
                val = re.sub(r'\s+', ' ', val)
                i18n_dict[key] = val
                
        with open(filename, 'w', encoding='utf-8') as f:
            formatted = str(soup)
            formatted = formatted.replace('></meta>', '/>').replace('></link>', '/>').replace('></img>', '/>')
            f.write(formatted)

with open('full_clean_i18n.json', 'w', encoding='utf-8') as f:
    json.dump(i18n_dict, f, indent=2, ensure_ascii=False)

print(f"Extraction successful. {len(i18n_dict)} keys saved.")
