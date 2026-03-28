// i18n.js (Smart Static AI Dictionary Engine)

// 1. Language Swapper Function (Triggered by Buttons)
window.changeLanguage = function(langCode) {
    // Save UI preference
    localStorage.setItem('site_lang', langCode);
    
    // Clear old Google Translate cookies just in case they linger
    document.cookie = "googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    document.cookie = "googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; domain=" + location.hostname + "; path=/;";
    
    // Reload page to re-init with new language
    location.reload();
}

// 2. Core Translation Engine & UI Updates
document.addEventListener('DOMContentLoaded', () => {

    const currentLang = localStorage.getItem('site_lang') || 'en';
    
    // Apply Translations using the global `translations` object (loaded from translations.js)
    if (typeof translations !== 'undefined' && translations[currentLang]) {
        const dict = translations[currentLang];
        
        // Find all elements looking for a translation
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (dict[key]) {
                el.innerHTML = dict[key];
            }
        });

        // Translate placeholder attributes
        document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
            const key = el.getAttribute('data-i18n-placeholder');
            if (dict[key]) {
                el.setAttribute('placeholder', dict[key]);
            }
        });
    }

    // Handle Right-To-Left Layouts dynamically for Dari & Pashto
    if (currentLang === 'fa' || currentLang === 'ps') {
        document.documentElement.setAttribute('dir', 'rtl');
    } else {
        document.documentElement.setAttribute('dir', 'ltr');
    }

    // Bold the active selected language button beautifully
    const allBtns = document.querySelectorAll('.lang-switcher-btn');
    allBtns.forEach(btn => {
        const btnLang = btn.getAttribute('data-lang');
        const isMobile = btn.classList.contains('mobile-lang-btn');
        
        // Reset styles first
        btn.classList.remove('text-primary', 'font-bold');
        if (isMobile) {
            btn.classList.add('text-background', 'opacity-80', 'hover:text-primary');
        } else {
            btn.classList.add('opacity-60', 'hover:opacity-100', 'hover:text-primary');
        }

        // Apply active styles
        if (btnLang === currentLang) {
            btn.classList.add('text-primary', 'font-bold');
            if (isMobile) btn.classList.remove('text-background', 'opacity-80', 'hover:text-primary');
            else btn.classList.remove('opacity-60', 'hover:opacity-100', 'hover:text-primary');
        }
    });

});
