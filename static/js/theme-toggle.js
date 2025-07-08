// theme-toggle.js

// Theme Toggle
const themeToggle = document.getElementById('theme-toggle');
const themeIcon = document.getElementById('theme-icon');

const updateIcon = (isDark) => {
    themeIcon.innerHTML = isDark
        ? `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z" />`
        : `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 3v2m0 14v2m9-9h-2M5 12H3m15.364-6.364l-1.414 1.414M6.05 17.95l-1.414-1.414M17.95 17.95l-1.414-1.414M6.05 6.05L4.636 7.464M12 8a4 4 0 100 8 4 4 0 000-8z" />`;
};

const savedTheme = localStorage.getItem('theme');
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
    document.documentElement.classList.add('dark');
    updateIcon(true);
} else {
    updateIcon(false);
}

themeToggle.addEventListener('click', () => {
    const isDark = document.documentElement.classList.toggle('dark');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    updateIcon(isDark);
});

// Search Toggle
const searchToggle = document.getElementById('search-toggle');
const searchContainer = document.getElementById('search-container');
let searchOpen = false;

searchToggle.addEventListener('click', () => {
    searchOpen = !searchOpen;
    if (searchOpen) {
        searchContainer.classList.remove('max-w-0');
        searchContainer.classList.add('max-w-xs', 'ml-2');
        searchContainer.querySelector('input').focus();
    } else {
        searchContainer.classList.remove('max-w-xs', 'ml-2');
        searchContainer.classList.add('max-w-0');
    }
});
