class AccessibilityControls {
    constructor() {
        this.initializeElements();
        this.initializeEvents();
        this.loadSavedSettings();
        this.fontSizeBase = 16;
        this.maxFontSize = 24;
        this.minFontSize = 12;
    }

    initializeElements() {
        this.buttons = document.querySelectorAll('.accessibility-btn');
    }

    initializeEvents() {
        this.buttons.forEach(button => {
            button.addEventListener('click', (e) => {
                const action = button.dataset.action;
                this.handleAction(action, button);
            });
        });
    }

    handleAction(action, button) {
        switch(action) {
            case 'contrast':
                this.toggleFilter('high-contrast', button);
                break;
            case 'invert':
                this.toggleFilter('inverted', button);
                break;
            case 'grayscale':
                this.toggleFilter('grayscale', button);
                break;
            case 'animations':
                this.toggleFilter('no-animations', button);
                break;
            case 'increase-font':
                this.changeFontSize(1);
                break;
            case 'decrease-font':
                this.changeFontSize(-1);
                break;
            case 'read-page':
                this.readPage();
                break;
        }
        this.saveSettings();
    }

    toggleFilter(className, button) {
        // Remove conflicting filters first
        const filters = ['high-contrast', 'inverted', 'grayscale'];
        if (filters.includes(className)) {
            filters.forEach(filter => {
                if (filter !== className) {
                    document.body.classList.remove(filter);
                    const otherButton = document.querySelector(`[data-action="${filter.replace('high-', '').replace('ed', '')}"]`);
                    if (otherButton) otherButton.classList.remove('active');
                }
            });
        }

        // Toggle current filter
        document.body.classList.toggle(className);
        button.classList.toggle('active');
    }

    changeFontSize(direction) {
        const html = document.documentElement;
        let currentSize = parseFloat(window.getComputedStyle(html).fontSize);
        let newSize = currentSize + (direction * 2);

        if (newSize >= this.minFontSize && newSize <= this.maxFontSize) {
            html.style.fontSize = `${newSize}px`;
        }
    }

    readPage() {
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();

            const text = Array.from(document.body.querySelectorAll('p, h1, h2, h3, h4, h5, h6, li, td, th, a'))
                .map(element => element.textContent)
                .join('. ')
                .trim();

            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'pt-BR';
            window.speechSynthesis.speak(utterance);
        }
    }

    saveSettings() {
        const settings = {
            highContrast: document.body.classList.contains('high-contrast'),
            inverted: document.body.classList.contains('inverted'),
            grayscale: document.body.classList.contains('grayscale'),
            noAnimations: document.body.classList.contains('no-animations'),
            fontSize: document.documentElement.style.fontSize
        };
        localStorage.setItem('accessibility-settings', JSON.stringify(settings));
    }

    loadSavedSettings() {
        const settings = JSON.parse(localStorage.getItem('accessibility-settings'));
        if (settings) {
            if (settings.highContrast) this.toggleFilter('high-contrast', document.querySelector('[data-action="contrast"]'));
            if (settings.inverted) this.toggleFilter('inverted', document.querySelector('[data-action="invert"]'));
            if (settings.grayscale) this.toggleFilter('grayscale', document.querySelector('[data-action="grayscale"]'));
            if (settings.noAnimations) this.toggleFilter('no-animations', document.querySelector('[data-action="animations"]'));
            if (settings.fontSize) document.documentElement.style.fontSize = settings.fontSize;
        }
    }
}

// Inicializar os controles quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', () => {
    new AccessibilityControls();
});