document.addEventListener('DOMContentLoaded', () => {
    const userMenuButton = document.getElementById('user-menu-button');
    const userMenu = document.getElementById('user-menu');
    const triangleIcon = document.getElementById('triangle-icon');

    if (userMenuButton) {
        userMenuButton.addEventListener('click', () => {
            const isMenuHidden = userMenu.classList.contains('hidden');
            userMenu.classList.toggle('hidden', !isMenuHidden);
            triangleIcon.innerHTML = isMenuHidden
                ? '<polygon points="0,7 14,7 7,0"></polygon>'
                : '<polygon points="0,0 14,0 7,7"></polygon>';
        });
    }

    document.addEventListener('click', (event) => {
        if (
            userMenu &&
            userMenuButton &&
            !userMenuButton.contains(event.target) &&
            !userMenu.contains(event.target)
        ) {
            userMenu.classList.add('hidden');
            triangleIcon.innerHTML = '<polygon points="0,0 14,0 7,7"></polygon>';
        }
    });
});
