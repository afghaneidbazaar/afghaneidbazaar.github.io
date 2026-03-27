import os
import re

html_files = [f for f in os.listdir('.') if f.endswith('.html')]

replacements = {
    r'href="#"([^>]*)>\s*Marketplace\s*</a>': r'href="vendors_festive_heritage_edition.html"\1>Marketplace</a>',
    r'href="#"([^>]*)>\s*Cultural Gallery\s*</a>': r'href="gallery_festive_heritage_edition.html"\1>Cultural Gallery</a>',
    r'href="#"([^>]*)>\s*Live Events\s*</a>': r'href="team_management_festive_heritage_edition.html"\1>Live Events</a>',
    r'href="#"([^>]*)>\s*About Eid\s*</a>': r'href="faq_festive_heritage_edition.html"\1>About Eid</a>',
    r'href="#"([^>]*)>\s*Contact Us\s*</a>': r'href="contact_us_festive_heritage_edition.html"\1>Contact Us</a>',
    r'href="#"([^>]*)>\s*Privacy Policy\s*</a>': r'href="index.html"\1>Privacy Policy</a>',
    r'href="#"([^>]*)>\s*Terms of Service\s*</a>': r'href="index.html"\1>Terms of Service</a>',
    r'href="#"([^>]*)>\s*Cultural Heritage\s*</a>': r'href="index.html"\1>Cultural Heritage</a>',
}

for file in html_files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = content
    for pattern, repl in replacements.items():
        new_content = re.sub(pattern, repl, new_content)
        
    # Link the brand logo to home as well:
    new_content = re.sub(
        r'<div class="text-[0-9xl]* font-headline text-primary.*?>\s*Afghan Eid Bazaar\s*</div>',
        r'<a href="index.html" class="text-2xl font-headline text-primary tracking-tight font-bold">Afghan Eid Bazaar</a>',
        new_content
    )
    
    if content != new_content:
        with open(file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated links in {file}")
