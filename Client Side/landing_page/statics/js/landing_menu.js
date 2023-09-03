const hamburgerToggle = document.getElementById('hamburgerToggle');
        const menuItems = document.querySelector('.menu-items');

        hamburgerToggle.addEventListener('change', () => {
            if (hamburgerToggle.checked) {
                menuItems.style.transform = 'translateX(0)';
            } else {
                menuItems.style.transform = 'translateX(-100%)';
            }
        });