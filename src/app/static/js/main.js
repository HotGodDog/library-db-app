// Main JavaScript for Library Management System

document.addEventListener('DOMContentLoaded', function() {
    
    // Confirm actions (delete, return, etc.)
    const confirmButtons = document.querySelectorAll('[data-confirm]');
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
    
    console.log('Library App initialized');
});