// accessibility.js
class AccessibilityWidget {
    constructor() {
        this.init();
        this.loadPreferences();
    }

    init() {
        // Criar e adicionar o widget ao DOM
        const widget = document.createElement('div');
        widget.className = 'accessibility-widget';
        widget.innerHTML = this.createWidgetHTML();
        document.body.appendChild(widget);

        // Inicializar eventos
        this.initializeEvents();

        // Inicializar sintetizador de voz
        this.speechSynth = window.speechSynthesis;
    }

    createWidgetHTML() {
        return `
            <button class="accessibility-button" aria-label="Opções de Acessibilidade">
                <i class="fas fa-universal-access"></i>
            </button>
            <div class="accessibility-menu">
                <div class="accessibility-option" data-action="contrast">
                    <i class="fas fa-adjust"></i> Alto Contraste
                </div>
                <div class="accessibility-option" data-action="invert">
                    <i class="fas fa-circle"></i> Cores Invertidas
                </div>
                <div class="accessibility-option" data-action="grayscale">
                    <i class="fas fa-gray"></i> Escala de Cinza
                </div>
                <div class="accessibility-option" data-action="animations">
                    <i class="fas fa-running"></i> Desativar Animações
                </div>
                <div class="accessibility-option" data-action="increase-font">
                    <i class="fas fa-plus"></i> Aumentar Fonte
                </div>
                <div class="accessibility-option" data-action="decrease-font">
                    <i class="fas fa-minus"></i> Diminuir Fonte
                </div>
                <div class="accessibility-option" data-action="read-page">
                    <i class="fas fa-volume-up"></i> Ler Página
                </div>
            </div>
        `;
    }

    initializeEvents() {
        const button = document.querySelector('.accessibility-button');
        const menu = document.querySelector('.accessibility-menu');
        const options = document.querySelectorAll('.accessibility-option');

        button.addEventListener('click', () => {
            menu.classList.toggle('active');
        });

        options.forEach(option => {
            option.addEventListener('click', (e) => {
                const action = e.currentTarget.dataset.action;
                this.handleAction(action);
            });
        });

        // Fechar menu quando clicar fora
        document.addEventListener('click', (e) => {
            if (!widget.contains(e.target)) {
                menu.classList.remove('active');
            }
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
                this.adjustFontSize(1);
                break;
            case 'decrease-font':
                this.adjustFontSize(-1);
                break;
            case 'read-page':
                this.readPage();
                break;
        }
        this.savePreferences();
    }

    toggleClass(className) {
        document.body.classList.toggle(className);
    }

    adjustFontSize(direction) {
        const body = document.body;
        let currentSize = parseInt(window.getComputedStyle(body).fontSize);
        const newSize = currentSize + (direction * 2);

        if (newSize >= 12 && newSize <= 24) {
            body.style.fontSize = `${newSize}px`;
        }
    }

    readPage() {
        if (this.speechSynth.speaking) {
            this.speechSynth.cancel();
            return;
        }

        const text = this.getPageContent();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'pt-BR';
        this.speechSynth.speak(utterance);
    }

    getPageContent() {
        const mainContent = document.querySelector('main') || document.body;
        return mainContent.innerText;
    }

    savePreferences() {
        const preferences = {
            highContrast: document.body.classList.contains('high-contrast'),
            inverted: document.body.classList.contains('inverted'),
            grayscale: document.body.classList.contains('grayscale'),
            noAnimations: document.body.classList.contains('no-animations'),
            fontSize: document.body.style.fontSize
        };
        localStorage.setItem('accessibility-preferences', JSON.stringify(preferences));
    }

    loadPreferences() {
        const saved = localStorage.getItem('accessibility-preferences');
        if (saved) {
            const preferences = JSON.parse(saved);
            if (preferences.highContrast) document.body.classList.add('high-contrast');
            if (preferences.inverted) document.body.classList.add('inverted');
            if (preferences.grayscale) document.body.classList.add('grayscale');
            if (preferences.noAnimations) document.body.classList.add('no-animations');
            if (preferences.fontSize) document.body.style.fontSize = preferences.fontSize;
        }
    }
}