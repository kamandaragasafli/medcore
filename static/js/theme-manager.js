(function () {
    if (window.themeManager) {
        return;
    }

    const themes = {
        light: {
            name: 'Light Mode',
            icon: 'fa-sun',
            appBg: '#f6f7fb',
            background: '#f6f7fb',
            surface: '#ffffff',
            surfaceAlt: '#eef2ff',
            surfaceMuted: '#f3f6ff',
            primary: '#2563eb',
            primarySoft: '#dbe4ff',
            secondary: '#22d3ee',
            success: '#10b981',
            warning: '#f97316',
            danger: '#ef4444',
            text: '#0f172a',
            textMuted: '#8a93a6',
            border: '#e4e7ec',
            shadowLg: '0 30px 60px rgba(15, 23, 42, 0.08)'
        },
        dark: {
            name: 'Dark Mode',
            icon: 'fa-moon',
            appBg: '#050a1f',
            background: '#050a1f',
            surface: '#0b152c',
            surfaceAlt: '#1e293b',
            surfaceMuted: '#0f172a',
            primary: '#3b82f6',
            primarySoft: '#1e3a8a',
            secondary: '#8b5cf6',
            success: '#2dd4bf',
            warning: '#db6007',
            danger: '#ef4444',
            text: '#e2e8f0',
            textMuted: '#94a3b8',
            border: 'rgba(148, 163, 184, 0.2)',
            shadowLg: '0 20px 50px rgba(3, 7, 18, 0.55)'
        },
        blue: {
            name: 'Ocean Blue',
            icon: 'fa-water',
            appBg: '#e0f2fe',
            background: '#e0f2fe',
            surface: '#ffffff',
            surfaceAlt: '#bae6fd',
            surfaceMuted: '#f0f9ff',
            primary: '#0284c7',
            primarySoft: '#bae6fd',
            secondary: '#06b6d4',
            success: '#10b981',
            warning: '#f59e0b',
            danger: '#ef4444',
            text: '#0c4a6e',
            textMuted: '#64748b',
            border: '#7dd3fc',
            shadowLg: '0 30px 60px rgba(2, 132, 199, 0.15)'
        },
        purple: {
            name: 'Purple Dream',
            icon: 'fa-star',
            appBg: '#faf5ff',
            background: '#faf5ff',
            surface: '#ffffff',
            surfaceAlt: '#f3e8ff',
            surfaceMuted: '#faf5ff',
            primary: '#9333ea',
            primarySoft: '#e9d5ff',
            secondary: '#d946ef',
            success: '#10b981',
            warning: '#f59e0b',
            danger: '#ef4444',
            text: '#581c87',
            textMuted: '#94a3b8',
            border: '#e9d5ff',
            shadowLg: '0 30px 60px rgba(147, 51, 234, 0.15)'
        },
        green: {
            name: 'Nature Green',
            icon: 'fa-leaf',
            appBg: '#f0fdf4',
            background: '#f0fdf4',
            surface: '#ffffff',
            surfaceAlt: '#dcfce7',
            surfaceMuted: '#f7fee7',
            primary: '#16a34a',
            primarySoft: '#bbf7d0',
            secondary: '#84cc16',
            success: '#22c55e',
            warning: '#f59e0b',
            danger: '#ef4444',
            text: '#14532d',
            textMuted: '#6b7280',
            border: '#bbf7d0',
            shadowLg: '0 30px 60px rgba(22, 163, 74, 0.15)'
        },
        darkgreen: {
            name: 'Dark Green',
            icon: 'fa-tree',
            appBg: '#0a2817',
            background: '#0a2817',
            surface: '#0f3d23',
            surfaceAlt: '#15492b',
            surfaceMuted: '#1a5535',
            primary: '#10b981',
            primarySoft: '#064e3b',
            secondary: '#34d399',
            success: '#6ee7b7',
            warning: '#fbbf24',
            danger: '#f87171',
            text: '#d1fae5',
            textMuted: '#86efac',
            border: 'rgba(16, 185, 129, 0.3)',
            shadowLg: '0 20px 50px rgba(6, 78, 59, 0.5)'
        },
        red: {
            name: 'Red Passion',
            icon: 'fa-fire',
            appBg: '#fef2f2',
            background: '#fef2f2',
            surface: '#ffffff',
            surfaceAlt: '#fee2e2',
            surfaceMuted: '#fef2f2',
            primary: '#dc2626',
            primarySoft: '#fecaca',
            secondary: '#f87171',
            success: '#10b981',
            warning: '#f59e0b',
            danger: '#b91c1c',
            text: '#7f1d1d',
            textMuted: '#94a3b8',
            border: '#fecaca',
            shadowLg: '0 30px 60px rgba(220, 38, 38, 0.15)'
        }
    };

    let currentTheme = localStorage.getItem('selectedTheme') || 'light';
    if (!themes[currentTheme]) {
        currentTheme = 'light';
    }

    function notify(message) {
        if (window.showNotification) {
            window.showNotification(message);
        }
    }

    function applyTheme(theme) {
        if (!theme) {
            return;
        }

        const root = document.documentElement;

        if (currentTheme === 'dark') {
            root.setAttribute('data-theme', 'dark');
        } else {
            root.removeAttribute('data-theme');
        }

        Object.keys(theme).forEach(key => {
            if (key === 'name' || key === 'icon') {
                return;
            }
            const cssVarName = '--' + key.replace(/([A-Z])/g, '-$1').toLowerCase();
            root.style.setProperty(cssVarName, theme[key]);
        });
    }

    function selectTheme(themeKey) {
        if (!themes[themeKey]) {
            return;
        }
        currentTheme = themeKey;
        applyTheme(themes[themeKey]);
        initColorPicker();
    }

    function initColorPicker() {
        const colorOptions = document.getElementById('colorOptions');
        if (!colorOptions) {
            return;
        }

        colorOptions.innerHTML = '';

        Object.keys(themes).forEach(themeKey => {
            const theme = themes[themeKey];
            const colorOption = document.createElement('div');
            colorOption.className = 'color-option' + (currentTheme === themeKey ? ' active' : '');
            colorOption.onclick = () => selectTheme(themeKey);

            colorOption.innerHTML = `
                <div class="color-preview" style="background: linear-gradient(135deg, ${theme.primary}, ${theme.secondary})">
                    <i class="fas ${theme.icon}"></i>
                </div>
                <div class="color-info">
                    <div class="color-name">${theme.name}</div>
                    <div class="color-value">${theme.primary}</div>
                </div>
                ${currentTheme === themeKey ? '<i class="fas fa-check-circle check-icon"></i>' : ''}
            `;

            colorOptions.appendChild(colorOption);
        });
    }

    function resetColors() {
        selectTheme('light');
        localStorage.removeItem('selectedTheme');
        notify('<i class="fas fa-check"></i> Standart rəngə qaytarıldı!');
    }

    function saveColors() {
        localStorage.setItem('selectedTheme', currentTheme);
        notify('<i class="fas fa-check"></i> Tema yadda saxlandı!');
        if (window.closeColorPicker) {
            window.closeColorPicker();
        }
    }

    function loadSavedTheme() {
        const savedTheme = localStorage.getItem('selectedTheme');
        if (savedTheme && themes[savedTheme]) {
            currentTheme = savedTheme;
        }
        applyTheme(themes[currentTheme]);
    }

    // Theme is already applied by inline script in head, so we don't need to load it again on DOMContentLoaded
    // This prevents the flash of light mode. The function is kept for manual theme switching.

    window.themeManager = {
        themes,
        selectTheme,
        initColorPicker,
        applyTheme,
        resetColors,
        saveColors,
        loadSavedTheme
    };

    window.resetColors = resetColors;
    window.saveColors = saveColors;
    window.selectTheme = selectTheme;
    window.initColorPicker = initColorPicker;
})();

