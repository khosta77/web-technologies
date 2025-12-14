document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.auth-form');
    const errorMessages = document.querySelector('.error-messages');
    
    if (!form || !errorMessages) {
        return;
    }
    
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
    
    function validateEmail(email) {
        const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        return emailRegex.test(email);
    }
    
    const submitButton = form.querySelector('button[type="submit"]');
    if (submitButton) {
        submitButton.addEventListener('click', function(e) {
            e.preventDefault();
            
            const formData = new FormData(form);
            const login = formData.get('login');
            const email = formData.get('email');
            const nickname = formData.get('nickname');
            const password = formData.get('password');
            const repeatPassword = formData.get('repeat_password');
            
            let hasError = false;
            let errorMessage = '';
            
            if (!login || login.trim() === '') {
                errorMessage = 'Поле "Login" не может быть пустым';
                hasError = true;
            }
            else if (!email || email.trim() === '') {
                errorMessage = 'Поле "Email" не может быть пустым';
                hasError = true;
            }
            else if (!email.includes('@')) {
                errorMessage = 'Email должен содержать символ @';
                hasError = true;
            }
            else if (!validateEmail(email)) {
                errorMessage = 'Некорректно введен email';
                hasError = true;
            }
            else if (!nickname || nickname.trim() === '') {
                errorMessage = 'Поле "NickName" не может быть пустым';
                hasError = true;
            }
            else if (!password || password.trim() === '') {
                errorMessage = 'Поле "Password" не может быть пустым';
                hasError = true;
            }
            else if (!repeatPassword || repeatPassword.trim() === '') {
                errorMessage = 'Поле "Repeat password" не может быть пустым';
                hasError = true;
            }
            else if (password !== repeatPassword) {
                errorMessage = 'Пароли не совпадают';
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