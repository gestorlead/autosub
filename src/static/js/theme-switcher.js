/**
 * Gerenciador de temas para o AutoSub
 * Permite alternar entre temas claro, escuro e baseado na preferência do sistema
 */

(function() {
    // Constantes para os temas
    const THEME_LIGHT = 'light';
    const THEME_DARK = 'dark';
    const THEME_AUTO = 'auto';
    
    // Chave para armazenamento da preferência
    const STORAGE_KEY = 'autosub-theme-preference';
    
    // Inicializa o tema ao carregar a página
    document.addEventListener('DOMContentLoaded', () => {
        initTheme();
        setupThemeToggle();
    });
    
    /**
     * Inicializa o tema baseado na preferência salva ou na configuração do sistema
     */
    function initTheme() {
        const savedTheme = localStorage.getItem(STORAGE_KEY);
        
        if (savedTheme === THEME_LIGHT) {
            setTheme(THEME_LIGHT);
        } else if (savedTheme === THEME_DARK) {
            setTheme(THEME_DARK);
        } else {
            // Se for 'auto' ou null, usa a preferência do sistema
            setThemeBasedOnSystemPreference();
            
            // Adiciona listener para mudanças na preferência do sistema
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
                if (localStorage.getItem(STORAGE_KEY) === THEME_AUTO || !localStorage.getItem(STORAGE_KEY)) {
                    setTheme(e.matches ? THEME_DARK : THEME_LIGHT, false);
                }
            });
        }
    }
    
    /**
     * Configura o controle de alternância de tema na interface
     */
    function setupThemeToggle() {
        const themeToggleContainer = document.createElement('div');
        themeToggleContainer.className = 'theme-toggle-container';
        themeToggleContainer.innerHTML = `
            <div class="dropdown">
                <button class="btn btn-sm theme-toggle-btn" type="button" data-bs-toggle="dropdown" aria-expanded="false">
                    <i class="fas fa-sun theme-icon-light"></i>
                    <i class="fas fa-moon theme-icon-dark"></i>
                    <i class="fas fa-desktop theme-icon-auto"></i>
                </button>
                <ul class="dropdown-menu dropdown-menu-end">
                    <li><button class="dropdown-item theme-option" data-theme="${THEME_LIGHT}"><i class="fas fa-sun me-2"></i>Modo Claro</button></li>
                    <li><button class="dropdown-item theme-option" data-theme="${THEME_DARK}"><i class="fas fa-moon me-2"></i>Modo Escuro</button></li>
                    <li><button class="dropdown-item theme-option" data-theme="${THEME_AUTO}"><i class="fas fa-desktop me-2"></i>Automático</button></li>
                </ul>
            </div>
        `;
        
        // Adiciona o controle na barra de navegação
        const navbarNav = document.querySelector('.navbar-nav');
        if (navbarNav) {
            navbarNav.appendChild(themeToggleContainer);
            
            // Adiciona estilos CSS para o controle
            const styleElement = document.createElement('style');
            styleElement.textContent = `
                .theme-toggle-container {
                    margin-left: 10px;
                    display: flex;
                    align-items: center;
                }
                .theme-toggle-btn {
                    background-color: transparent;
                    border: none;
                    color: rgba(255, 255, 255, 0.85);
                    padding: 0.25rem 0.5rem;
                    font-size: 1rem;
                }
                .theme-toggle-btn:hover {
                    color: rgba(255, 255, 255, 1);
                }
                
                /* Mostrar apenas o ícone apropriado com base no tema atual */
                .theme-icon-light, .theme-icon-dark, .theme-icon-auto {
                    display: none;
                }
                html[data-theme="light"] .theme-icon-light,
                html[data-theme="dark"] .theme-icon-dark,
                html:not([data-theme]),
                html[data-theme="auto"] .theme-icon-auto {
                    display: inline-block;
                }
                
                /* Garantir que o texto do dropdown seja sempre visível */
                .dropdown-item {
                    color: var(--bs-body-color) !important;
                    white-space: nowrap;
                }
                
                [data-theme="dark"] .dropdown-item {
                    color: #ffffff !important;
                }
            `;
            document.head.appendChild(styleElement);
            
            // Adiciona eventos de clique para as opções de tema
            document.querySelectorAll('.theme-option').forEach(option => {
                option.addEventListener('click', () => {
                    const theme = option.getAttribute('data-theme');
                    if (theme === THEME_AUTO) {
                        localStorage.setItem(STORAGE_KEY, THEME_AUTO);
                        setThemeBasedOnSystemPreference();
                    } else {
                        setTheme(theme);
                    }
                });
            });
        }
    }
    
    /**
     * Define o tema com base na preferência do sistema
     */
    function setThemeBasedOnSystemPreference() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            setTheme(THEME_DARK, false);
        } else {
            setTheme(THEME_LIGHT, false);
        }
        
        // Define o atributo data-theme no HTML para 'auto'
        document.documentElement.setAttribute('data-theme-source', THEME_AUTO);
    }
    
    /**
     * Define o tema da aplicação
     * @param {string} theme - O tema a ser aplicado ('light' ou 'dark')
     * @param {boolean} savePreference - Se deve salvar a preferência (true por padrão)
     */
    function setTheme(theme, savePreference = true) {
        if (theme === THEME_DARK) {
            document.documentElement.setAttribute('data-theme', THEME_DARK);
        } else {
            document.documentElement.setAttribute('data-theme', THEME_LIGHT);
        }
        
        if (savePreference) {
            localStorage.setItem(STORAGE_KEY, theme);
        }
    }
})(); 