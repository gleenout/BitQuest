// static/js/accessibility_widget.js
class BitQuestAccessibility {
    constructor() {
        this.widget = document.querySelector('.bitquest-accessibility-widget');
        this.toggle = document.querySelector('.bitquest-accessibility-toggle');
        this.menu = document.querySelector('.bitquest-accessibility-menu');
        this.fontSizeBase = 16;
        this.maxFontSize = 24;
        this.minFontSize = 12;

        this.initializeEvents();
        this.loadSavedSettings();
    }

    initializeEvents() {
        // Toggle menu
        this.toggle.addEventListener('click', () => {
            this.menu.classList.toggle('active');
        });

        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!this.widget.contains(e.target)) {
                this.menu.classList.remove('active');
            }
        });

        // Handle accessibility options
        document.querySelectorAll('.bitquest-accessibility-option').forEach(option => {
            option.addEventListener('click', (e) => {
                const action = option.dataset.action;
                this.handleAction(action);
            });
        });
    }

    handleAction(action) {
        switch(action) {
            case 'contrast':
                this.toggleClass('high-contrast');
                break;
            case 'invert':
                this.toggleClass('inverted');
                break;
            case 'grayscale':
                this.toggleClass('grayscale');
                break;
            case 'animations':
                this.toggleClass('no-animations');
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

    toggleClass(className) {
        document.body.classList.toggle(className);
    }

    changeFontSize(direction) {
        let currentSize = parseInt(window.getComputedStyle(document.documentElement).fontSize);
        let newSize = currentSize + (direction * 2);

        if (newSize >= this.minFontSize && newSize <= this.maxFontSize) {
            document.documentElement.style.fontSize = `${newSize}px`;
            localStorage.setItem('bitquest-font-size', newSize);
        }
    }

    readPage() {
        const text = document.body.textContent.trim();
        if ('speechSynthesis' in window) {
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

        localStorage.setItem('bitquest-accessibility-settings', JSON.stringify(settings));
    }

    loadSavedSettings() {
        const settings = JSON.parse(localStorage.getItem('bitquest-accessibility-settings'));
        if (settings) {
            if (settings.highContrast) document.body.classList.add('high-contrast');
            if (settings.inverted) document.body.classList.add('inverted');
            if (settings.grayscale) document.body.classList.add('grayscale');
            if (settings.noAnimations) document.body.classList.add('no-animations');
            if (settings.fontSize) document.documentElement.style.fontSize = settings.fontSize;
        }

        const savedFontSize = localStorage.getItem('bitquest-font-size');
        if (savedFontSize) {
            document.documentElement.style.fontSize = `${savedFontSize}px`;
        }
    }
}

// Inicializar o widget quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', () => {
    new BitQuestAccessibility();
});