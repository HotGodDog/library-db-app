// Main JavaScript for Library Management System

document.addEventListener('DOMContentLoaded', function() {
    
    // Confirm actions (delete, return, etc.)
    const confirmButtons = document.querySelectorAll('button[data-confirm], [data-confirm]');
    confirmButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm');
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
    
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.5s';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
    
    // Search focus on page load
    const searchInput = document.querySelector('.search-box input');
    if (searchInput && !searchInput.value) {
        searchInput.focus();
    }
    
    // Auth tabs on login page
    const authTabs = document.querySelectorAll('.auth-tab');
    const panelLogin = document.getElementById('panel-login');
    const panelRegister = document.getElementById('panel-register');
    if (authTabs.length && panelLogin && panelRegister) {
        authTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const isRegister = tab.dataset.mode === 'register';
                authTabs.forEach(t => t.classList.toggle('active', t === tab));
                panelLogin.classList.toggle('hidden', isRegister);
                panelRegister.classList.toggle('hidden', !isRegister);
            });
        });
    }

    console.log('Library App initialized');
});