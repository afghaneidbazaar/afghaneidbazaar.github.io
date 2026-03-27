import os
import re

html_files = [f for f in os.listdir('.') if f.endswith('.html')]

base_classes_inactive = "opacity-80 hover:text-primary transition-colors duration-300"
base_classes_active = "text-primary font-bold border-b-2 border-primary pb-1"

nav_items = [
    ("Home", "index.html"),
    ("Vendors", "vendors.html"),
    ("Sponsors", "sponsors.html"),
    ("About Eid", "about.html"),
    ("Gallery", "gallery.html"),
    ("FAQ", "faq.html"),
    ("Team", "team.html"),
    ("Contact", "contact.html")
]

for file in html_files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()

    color_class = "text-white"
    if "text-background" in content and "bg-on-surface" in content:
        color_class = "text-background"
    
    nav_html_parts = []
    
    for label, link in nav_items:
        is_active = (link == file)
        
        if is_active:
            classes = base_classes_active
        else:
            classes = f"{color_class} {base_classes_inactive}"
            
        nav_html_parts.append(f'<a class="{classes}" href="{link}">{label}</a>')
        
    nav_html = "\n".join(nav_html_parts)
    
    container_pattern = r'(<div class="hidden md:flex items-center[^>]*>)(.*?)(</div>)'
    
    new_content = re.sub(
        container_pattern, 
        lambda m: f"{m.group(1)}\n{nav_html}\n{m.group(3)}", 
        content, 
        count=1,
        flags=re.DOTALL
    )
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Updated nav in {file}")
