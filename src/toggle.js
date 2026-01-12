// theme-toggle.js
document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.createElement('button');
    themeToggle.id = 'themeToggle';
    themeToggle.textContent = 'Switch to Night Mode';
    document.body.appendChild(themeToggle);

    const body = document.body;

    // Check for saved theme in localStorage
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        body.classList.add(savedTheme);
        themeToggle.textContent = savedTheme === 'night' ? 'Switch to Day Mode' : 'Switch to Night Mode';
    } else {
        body.classList.add('day'); // Default to day mode
    }

    themeToggle.addEventListener('click', () => {
        if (body.classList.contains('day')) {
            body.classList.remove('day');
            body.classList.add('night');
            themeToggle.textContent = 'Switch to Day Mode';
            localStorage.setItem('theme', 'night'); // Save theme preference
        } else {
            body.classList.remove('night');
            body.classList.add('day');
            themeToggle.textContent = 'Switch to Night Mode';
            localStorage.setItem('theme', 'day'); // Save theme preference
        }
    });
});