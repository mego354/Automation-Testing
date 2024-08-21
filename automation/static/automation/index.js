// Load preference
document.addEventListener('DOMContentLoaded', () => {
    const highContrast = localStorage.getItem('highContrast') === 'true';
    if (highContrast) {
        document.body.classList.add('high-contrast');
        var dark_icon = document.getElementById('dark_icon');
        dark_icon.classList.remove('fa-sun');
        dark_icon.classList.add('fa-moon');                
    }

    // Load Font Size Preference
    const savedFontSize = localStorage.getItem('fontSize') || 'medium';
    document.getElementById('font-size-switcher').value = savedFontSize;
    changeFontSize(); // Apply saved font size
});

// High Contrast Mode Toggle
document.getElementById('toggle-contrast').addEventListener('click', function() {
    document.body.classList.toggle('high-contrast');
    const isHighContrast = document.body.classList.contains('high-contrast');
    localStorage.setItem('highContrast', isHighContrast);
    var dark_icon = document.getElementById('dark_icon');
    if (dark_icon.classList.contains('fa-sun')) {
        dark_icon.classList.remove('fa-sun');
        dark_icon.classList.add('fa-moon');
    } else {
        dark_icon.classList.remove('fa-moon');
        dark_icon.classList.add('fa-sun');
    }
});    

// Font Size Change Function
function changeFontSize() {
    const fontSize = document.getElementById('font-size-switcher').value;
    const fontSizeMap = {
        'small': {
            '--font-size-h1': 'var(--font-size-h1-small)',
            '--font-size-h2': 'var(--font-size-h2-small)',
            '--font-size-h3': 'var(--font-size-h3-small)',
            '--font-size-p': 'var(--font-size-p-small)',
            '--font-size-a': 'var(--font-size-a-small)',
        },
        'medium': {
            '--font-size-h1': 'var(--font-size-h1-medium)',
            '--font-size-h2': 'var(--font-size-h2-medium)',
            '--font-size-h3': 'var(--font-size-h3-medium)',
            '--font-size-p': 'var(--font-size-p-medium)',
            '--font-size-a': 'var(--font-size-a-medium)',
        },
        'large': {
            '--font-size-h1': 'var(--font-size-h1-large)',
            '--font-size-h2': 'var(--font-size-h2-large)',
            '--font-size-h3': 'var(--font-size-h3-large)',
            '--font-size-p': 'var(--font-size-p-large)',
            '--font-size-a': 'var(--font-size-a-large)',
        },
        'vlarge': {
            '--font-size-h1': 'var(--font-size-h1-vlarge)',
            '--font-size-h2': 'var(--font-size-h2-vlarge)',
            '--font-size-h3': 'var(--font-size-h3-vlarge)',
            '--font-size-p': 'var(--font-size-p-vlarge)',
            '--font-size-a': 'var(--font-size-a-vlarge)',
        }
    };

    const sizes = fontSizeMap[fontSize] || fontSizeMap['medium'];
    for (const [key, value] of Object.entries(sizes)) {
        document.documentElement.style.setProperty(key, value);
    }

    // Save user preference
    localStorage.setItem('fontSize', fontSize);
}


