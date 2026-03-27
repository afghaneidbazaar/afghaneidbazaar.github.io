document.addEventListener('DOMContentLoaded', () => {
    // 1. Get user language
    const currentLang = localStorage.getItem('site_lang') || 'en';
    
    // 2. Apply instantly
    window.applyTranslations(currentLang);
});

window.applyTranslations = function(lang) {
    if (!window.siteTranslations || !window.siteTranslations[lang]) return;
    
    // RTL Support for Dari & Pashto
    if (lang === 'da' || lang === 'ps') {
        document.documentElement.setAttribute('dir', 'rtl');
    } else {
        document.documentElement.setAttribute('dir', 'ltr');
    }

    // Inject Text
    const elements = document.querySelectorAll('[data-i18n]');
    elements.forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (window.siteTranslations[lang][key]) {
            el.textContent = window.siteTranslations[lang][key];
        }
    });

    // Update UI Active States
    updateLanguageUI(lang);
}

function updateLanguageUI(activeLang) {
    const allBtns = document.querySelectorAll('.lang-switcher-btn');
    
    allBtns.forEach(btn => {
        const btnLang = btn.getAttribute('data-lang');
        const isMobile = btn.classList.contains('mobile-lang-btn');
        
        // Strip active classes completely
        btn.classList.remove('text-primary', 'font-bold');
        
        // Reapply inactive classes
        if (isMobile) {
            btn.classList.add('text-background', 'opacity-80', 'hover:text-primary');
        } else {
            btn.classList.add('opacity-60', 'hover:opacity-100', 'hover:text-primary');
        }

        // Apply clean active state
        if (btnLang === activeLang) {
            btn.classList.add('text-primary', 'font-bold');
            
            // Remove the inactive classes that were just assigned
            if (isMobile) {
                btn.classList.remove('text-background', 'opacity-80', 'hover:text-primary');
            } else {
                btn.classList.remove('opacity-60', 'hover:opacity-100', 'hover:text-primary');
            }
        }
    });
}

window.changeLanguage = function(lang) {
    // Save locally
    localStorage.setItem('site_lang', lang);
    
    // Translate the DOM live
    window.applyTranslations(lang);
    
    // Close mobile menu if open
    const mobileMenu = document.getElementById('mobile-menu');
    const menuBtnIcon = document.querySelector('#mobile-menu-btn .material-symbols-outlined');
    if (mobileMenu && !mobileMenu.classList.contains('hidden')) {
        mobileMenu.classList.add('hidden');
        if(menuBtnIcon) menuBtnIcon.textContent = 'menu';
    }
}
