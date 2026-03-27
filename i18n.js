// i18n.js (Google Translate AI Engine Integration)

// 0. Aggressively Hide Google's native UI popups
(function hideGoogleUI() {
    const style = document.createElement('style');
    style.innerHTML = `
        iframe.goog-te-banner-frame { display: none !important; visibility: hidden !important; }
        .goog-te-banner-frame { display: none !important; visibility: hidden !important; }
        iframe[id^=":1.container"] { display: none !important; visibility: hidden !important; }
        body { top: 0px !important; position: static !important; }
        #goog-gt-tt { display: none !important; }
        .goog-text-highlight { background-color: transparent !important; box-shadow: none !important; }
    `;
    document.head.appendChild(style);
})();

// 1. Inject Google Translate Library seamlessly
if (!document.getElementById('google-translate-script')) {
    const script = document.createElement('script');
    script.id = 'google-translate-script';
    script.src = "//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit";
    document.head.appendChild(script);

    const gtDiv = document.createElement('div');
    gtDiv.id = 'google_translate_element';
    gtDiv.style.display = 'none';
    document.body.appendChild(gtDiv);
}

// Required by Google
window.googleTranslateElementInit = function() {
    new google.translate.TranslateElement({
        pageLanguage: 'en',
        includedLanguages: 'fr,fa,ps', // French, Persian (Dari), Pashto
        autoDisplay: false
    }, 'google_translate_element');
};

// 2. Custom Language Switcher Logic
window.changeLanguage = function(langCode) {
    // If English, clear the Translation cookie
    if (langCode === 'en') {
        document.cookie = "googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
        document.cookie = "googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; domain=" + location.hostname + "; path=/;";
    } else {
        // Set the Translation cookie to force Google to translate automatically
        document.cookie = `googtrans=/en/${langCode}; path=/`;
        document.cookie = `googtrans=/en/${langCode}; domain=${location.hostname}; path=/`;
    }
    
    // Save UI preference
    localStorage.setItem('site_lang', langCode);
    
    // Reload page to apply full DOM machine-translation
    location.reload();
}

// 3. Update Visual UI and Cleanup Google's Default Styles
document.addEventListener('DOMContentLoaded', () => {

    const currentLang = localStorage.getItem('site_lang') || 'en';
    
    // Handle Right-To-Left Layouts for Dari & Pashto
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
        
        btn.classList.remove('text-primary', 'font-bold');
        if (isMobile) {
            btn.classList.add('text-background', 'opacity-80', 'hover:text-primary');
        } else {
            btn.classList.add('opacity-60', 'hover:opacity-100', 'hover:text-primary');
        }

        if (btnLang === currentLang) {
            btn.classList.add('text-primary', 'font-bold');
            if (isMobile) btn.classList.remove('text-background', 'opacity-80', 'hover:text-primary');
            else btn.classList.remove('opacity-60', 'hover:opacity-100', 'hover:text-primary');
        }
    });

    // Mobile menu fallback close
    const mobileMenu = document.getElementById('mobile-menu');
    const menuBtnIcon = document.querySelector('#mobile-menu-btn .material-symbols-outlined');
    if (mobileMenu && !mobileMenu.classList.contains('hidden') && window.innerWidth > 1024) {
         mobileMenu.classList.add('hidden');
         if(menuBtnIcon) menuBtnIcon.textContent = 'menu';
    }
});
