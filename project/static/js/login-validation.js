document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.auth-form');
    const errorMessages = document.querySelector('.error-messages');
    
    if (!form || !errorMessages) return;
        
    function showError(message) {
        errorMessages.innerHTML = `
            <div class="alert alert-error">
                ${message}
            </div>
        `;
        errorMessages.style.display = 'block';
    }
    
    function hideError() {
        errorMessages.style.display = 'none';
    }
    
    const submitButton = form.querySelector('button[type="submit"]');
    if (submitButton) {
        submitButton.addEventListener('click', function(e) {
            e.preventDefault();
            
            const formData = new FormData(form);
            const login = formData.get('login');
            const password = formData.get('password');
            
            let hasError = false;
            let errorMessage = '';
            
            if (!login || login.trim() === '') {
                errorMessage = 'Поле "Login" не может быть пустым';
                hasError = true;
            }
            else if (!password || password.trim() === '') {
                errorMessage = 'Поле "Password" не может быть пустым';
                hasError = true;
            }
            
            if (hasError) {
                showError(errorMessage);
            } else {
                hideError();
            }
        });
    }
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
    });
    
    const inputs = form.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            hideError();
        });
    });
});