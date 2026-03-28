#!/usr/bin/env python3
"""
sync_i18n.py — Automated i18n sync for Afghan Eid Bazaar
=========================================================
Detects new/changed English content across all HTML pages,
auto-tags untagged elements, and rebuilds translations.js.

Usage:
  python sync_i18n.py              # Scan, tag, and report what needs translating
  python sync_i18n.py --apply      # Apply new translations from new_translations.json into translations.js
"""

import os
import sys
import json
import re
import html as html_mod
from bs4 import BeautifulSoup, NavigableString

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
HTML_DIR = '.'
TRANSLATIONS_FILE = 'translations.js'
NEEDS_FILE = 'needs_translation.json'
NEW_TRANS_FILE = 'new_translations.json'
LANGUAGES = ['fr', 'fa', 'ps']

TAGS_TO_CHECK = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'button', 'a', 'label', 'li', 'td', 'th', 'span']

# Language button labels — these are handled by common.button.lang.* keys, skip per-page duplicates
LANG_BUTTON_LABELS = {'English', 'French', 'Persian Dari', 'Pashto',
                      'انګلیسي', 'فرانسوي', 'فارسي دري', 'پښتو',
                      'Anglais', 'Français', 'Persan Dari', 'Pachto'}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
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

def parse_translations_js(filepath):
    """Parse translations.js into a Python dict."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    # Strip "const translations = " and trailing ";"
    json_str = content.strip()
    json_str = re.sub(r'^const\s+translations\s*=\s*', '', json_str)
    json_str = re.sub(r';\s*$', '', json_str)
    # Remove JS single-line comments
    json_str = re.sub(r'//[^\n]*', '', json_str)
    # Remove trailing commas before } or ]
    json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
    return json.loads(json_str)

def write_translations_js(filepath, data):
    """Write translations dict back to translations.js with clean formatting."""
    lines = ['const translations = {']
    lang_order = ['en', 'fr', 'fa', 'ps']

    for li, lang in enumerate(lang_order):
        if lang not in data:
            continue
        lines.append(f'  "{lang}": {{')

        keys = list(data[lang].keys())
        # Group keys by page prefix for comments
        current_page = None
        page_labels = {
            'nav': 'Navigation', 'about': 'About Page', 'contact': 'Contact Page',
            'faq': 'FAQ Page', 'gallery': 'Gallery Page', 'index': 'Homepage',
            'home': 'Homepage Hero/Sections', 'sponsors': 'Sponsors Page',
            'team': 'Team Page', 'vendors': 'Vendors Page', 'footer': 'Footer',
            'common': 'Common/Shared'
        }

        for ki, key in enumerate(keys):
            page = key.split('.')[0]
            if page != current_page:
                if current_page is not None:
                    lines.append('')
                label = page_labels.get(page, page.title() + ' Page')
                lines.append(f'    // {label}')
                current_page = page

            val = data[lang][key]
            # Escape for JS string
            val_escaped = val.replace('\\', '\\\\').replace('"', '\\"')
            comma = ',' if ki < len(keys) - 1 else ''
            lines.append(f'    "{key}": "{val_escaped}"{comma}')

        comma = ',' if li < len(lang_order) - 1 else ''
        lines.append(f'  }}{comma}')

    lines.append('};')
    lines.append('')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

# ---------------------------------------------------------------------------
# Phase 1: Scan & Tag
# ---------------------------------------------------------------------------
def scan_and_tag():
    """Scan all HTML files, auto-tag new elements, extract all i18n keys."""
    all_keys = {}  # key -> english text from HTML
    new_keys = []  # keys that were just auto-tagged

    # Get current highest counter per page
    counter = {}

    html_files = sorted([f for f in os.listdir(HTML_DIR) if f.endswith('.html')])

    for filename in html_files:
        filepath = os.path.join(HTML_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            html = f.read()

        soup = BeautifulSoup(html, 'html.parser')
        page_name = filename.replace('.html', '')

        # First pass: collect existing keys and find max counter
        max_counter = 0
        for tag in soup.find_all(True):
            if tag.has_attr('data-i18n'):
                key = tag['data-i18n']
                val = tag.decode_contents().strip()
                val = re.sub(r'\s+', ' ', val)
                all_keys[key] = val
                # Extract counter from key
                parts = key.split('.')
                if len(parts) >= 3:
                    try:
                        num = int(parts[-1])
                        if num > max_counter:
                            max_counter = num
                    except ValueError:
                        pass

        counter[page_name] = max_counter

        # Second pass: find untagged elements and auto-tag them
        modified = False
        for tag_name in TAGS_TO_CHECK:
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
                all_keys[key] = val
                new_keys.append(key)
                modified = True

        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                formatted = str(soup)
                formatted = formatted.replace('></meta>', '/>').replace('></link>', '/>').replace('></img>', '/>')
                f.write(formatted)

    return all_keys, new_keys

# ---------------------------------------------------------------------------
# Phase 2: Diff against translations.js
# ---------------------------------------------------------------------------
def normalize_text(text):
    """Normalize text for comparison: decode HTML entities, normalize whitespace, strip year."""
    t = html_mod.unescape(text)
    t = re.sub(r'\s+', ' ', t).strip()
    # Normalize copyright symbol variations
    t = t.replace('\u00a9', '©').replace('&copy;', '©')
    # Normalize year in copyright lines so "2024" vs "2026" doesn't trigger false diff
    t = re.sub(r'©\s*\d{4}', '© YYYY', t)
    t = re.sub(r'\b20\d{2}\b', 'YYYY', t)
    return t

def is_lang_button(key, text):
    """Check if a key is a per-page language switcher button (handled by common.button.lang.*)."""
    return text.strip() in LANG_BUTTON_LABELS and '.button.' in key

def find_changes(html_keys, translations):
    """Compare HTML keys against translations.js to find new/changed entries."""
    en_dict = translations.get('en', {})

    new_keys = []       # In HTML but not in translations.js
    changed_keys = []   # English text changed
    removed_keys = []   # In translations.js but not in HTML

    for key, html_text in html_keys.items():
        # Skip language switcher buttons — handled by common.button.lang.*
        if is_lang_button(key, html_text):
            continue
        if key not in en_dict:
            new_keys.append(key)
        elif normalize_text(en_dict[key]) != normalize_text(html_text):
            changed_keys.append(key)

    for key in en_dict:
        if key not in html_keys:
            # Check if it's a non-HTML key (like home.hero.*, footer.*, common.*)
            prefix = key.split('.')[0]
            if prefix in ('home', 'footer', 'common'):
                continue  # These are manual keys, keep them
            removed_keys.append(key)

    return new_keys, changed_keys, removed_keys

# ---------------------------------------------------------------------------
# Phase 3: Generate needs_translation.json
# ---------------------------------------------------------------------------
def generate_needs_file(html_keys, new_keys, changed_keys):
    """Generate a JSON file listing what needs to be translated."""
    needs = {}
    for key in new_keys + changed_keys:
        needs[key] = {
            "en": html_keys[key],
            "fr": "",
            "fa": "",
            "ps": "",
            "status": "new" if key in new_keys else "changed"
        }

    with open(NEEDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(needs, f, indent=2, ensure_ascii=False)

    return needs

# ---------------------------------------------------------------------------
# Phase 4: Apply translations from new_translations.json
# ---------------------------------------------------------------------------
def apply_translations():
    """Merge new_translations.json into translations.js."""
    if not os.path.exists(NEW_TRANS_FILE):
        print(f"Error: {NEW_TRANS_FILE} not found. Create it with translations first.")
        return False

    with open(NEW_TRANS_FILE, 'r', encoding='utf-8') as f:
        new_trans = json.load(f)

    translations = parse_translations_js(TRANSLATIONS_FILE)

    for key, entry in new_trans.items():
        # Update English
        if 'en' in entry and entry['en']:
            translations['en'][key] = entry['en']
        # Update other languages
        for lang in LANGUAGES:
            if lang in entry and entry[lang]:
                if lang not in translations:
                    translations[lang] = {}
                translations[lang][key] = entry[lang]

    write_translations_js(TRANSLATIONS_FILE, translations)
    print(f"Applied {len(new_trans)} translation(s) to {TRANSLATIONS_FILE}")

    # Clean up
    os.remove(NEW_TRANS_FILE)
    if os.path.exists(NEEDS_FILE):
        os.remove(NEEDS_FILE)

    return True

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    if '--apply' in sys.argv:
        apply_translations()
        return

    print("Phase 1: Scanning HTML files and auto-tagging new elements...")
    html_keys, auto_tagged = scan_and_tag()
    print(f"  Found {len(html_keys)} total i18n keys across all HTML files.")
    if auto_tagged:
        print(f"  Auto-tagged {len(auto_tagged)} NEW elements:")
        for k in auto_tagged:
            print(f"    + {k}")
    else:
        print("  No new untagged elements found.")

    print("\nPhase 2: Comparing against translations.js...")
    translations = parse_translations_js(TRANSLATIONS_FILE)
    new_keys, changed_keys, removed_keys = find_changes(html_keys, translations)

    if not new_keys and not changed_keys:
        print("  Everything is in sync! No translations needed.")
        return

    if new_keys:
        print(f"\n  NEW keys ({len(new_keys)}):")
        for k in new_keys:
            print(f"    + {k}: \"{html_keys[k][:60]}...\"" if len(html_keys[k]) > 60 else f"    + {k}: \"{html_keys[k]}\"")

    if changed_keys:
        print(f"\n  CHANGED keys ({len(changed_keys)}):")
        for k in changed_keys:
            print(f"    ~ {k}: \"{html_keys[k][:60]}...\"" if len(html_keys[k]) > 60 else f"    ~ {k}: \"{html_keys[k]}\"")

    print(f"\nPhase 3: Generating {NEEDS_FILE}...")
    needs = generate_needs_file(html_keys, new_keys, changed_keys)
    print(f"  Written {len(needs)} entries to {NEEDS_FILE}")

    print(f"""
=== NEXT STEPS ===
1. Fill in the translations in '{NEEDS_FILE}'
   (or copy the contents and ask any AI to translate them)
2. Save the completed translations as '{NEW_TRANS_FILE}'
3. Run: python sync_i18n.py --apply
   This will merge them into translations.js automatically.
""")

if __name__ == '__main__':
    main()
