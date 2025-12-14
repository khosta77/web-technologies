document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.auth-form');
    
    if (!form) {
        return;
    }
    
    // Получаем элементы формы
    const usernameField = form.querySelector('#id_username');
    const emailField = form.querySelector('#id_email');
    const passwordField = form.querySelector('#id_password1');
    const repeatPasswordField = form.querySelector('#id_password2');
    
    // Функция для отображения ошибки под полем
    function showFieldError(field, message) {
        if (!field) {
            return;
        }
        
        hideFieldError(field);
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message field-error';
        errorDiv.textContent = message;
        
        const formGroup = field.closest('.form-group');
        if (formGroup) {
            formGroup.appendChild(errorDiv);
        } else {
            field.parentNode.appendChild(errorDiv);
        }
        
        field.classList.add('error');
    }
    
    function hideFieldError(field) {
        if (!field) {
            return;
        }
        
        const formGroup = field.closest('.form-group');
        if (formGroup) {
            const errorDiv = formGroup.querySelector('.field-error');
            if (errorDiv) {
                errorDiv.remove();
            }
        } else {
            const errorDiv = field.parentNode.querySelector('.field-error');
            if (errorDiv) {
                errorDiv.remove();
            }
        }
        
        field.classList.remove('error');
    }
    
    // Функция для валидации email
    function validateEmail(email) {
        const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        return emailRegex.test(email);
    }
    
    // Функция валидации формы
    function validateForm() {
        let isValid = true;
        
        // Валидация username
        if (usernameField) {
            const username = usernameField.value.trim();
            if (!username) {
                showFieldError(usernameField, 'Это поле обязательно для заполнения');
                isValid = false;
            } else {
                hideFieldError(usernameField);
            }
        }
        
        // Валидация email
        if (emailField) {
            const email = emailField.value.trim();
            if (!email) {
                showFieldError(emailField, 'Это поле обязательно для заполнения');
                isValid = false;
            } else if (!validateEmail(email)) {
                showFieldError(emailField, 'Некорректный формат email');
                isValid = false;
            } else {
                hideFieldError(emailField);
            }
        }
        
        // Валидация password
        if (passwordField) {
            const password = passwordField.value;
            if (!password) {
                showFieldError(passwordField, 'Это поле обязательно для заполнения');
                isValid = false;
            } else if (password.length < 5) {
                showFieldError(passwordField, 'Пароль должен содержать минимум 5 символов');
                isValid = false;
            } else {
                hideFieldError(passwordField);
            }
        }
        
        // Валидация repeat_password
        if (repeatPasswordField) {
            const repeatPassword = repeatPasswordField.value;
            const password = passwordField ? passwordField.value : '';
            if (!repeatPassword) {
                showFieldError(repeatPasswordField, 'Это поле обязательно для заполнения');
                isValid = false;
            } else if (password && repeatPassword && password !== repeatPassword) {
                showFieldError(repeatPasswordField, 'Пароли не совпадают');
                isValid = false;
            } else if (password && repeatPassword && password === repeatPassword) {
                hideFieldError(repeatPasswordField);
            }
        }
        
        return isValid;
    }
    
    // Обработчик отправки формы
    form.addEventListener('submit', function(e) {
        const isValid = validateForm();
        if (!isValid) {
            e.preventDefault();
            e.stopPropagation();
            return false;
        }
    });
    
    function hideServerErrors(field) {
        if (!field) {
            return;
        }
        
        const formGroup = field.closest('.form-group');
        if (formGroup) {
            const serverErrors = formGroup.querySelectorAll('.error-message.server-error');
            serverErrors.forEach(error => error.remove());
            
            field.classList.remove('error');
        }
    }
    
    // Очистка ошибок при вводе (и серверных, и клиентских)
    if (usernameField) {
        usernameField.addEventListener('input', function() {
            hideFieldError(usernameField);
            hideServerErrors(usernameField);
        });
    }
    
    if (emailField) {
        emailField.addEventListener('input', function() {
            hideFieldError(emailField);
            hideServerErrors(emailField);
        });
    }
    
    if (passwordField) {
        passwordField.addEventListener('input', function() {
            hideFieldError(passwordField);
            hideServerErrors(passwordField);
            // Если есть repeat_password, проверяем совпадение в реальном времени
            if (repeatPasswordField && repeatPasswordField.value) {
                if (passwordField.value === repeatPasswordField.value) {
                    hideFieldError(repeatPasswordField);
                    hideServerErrors(repeatPasswordField);
                } else {
                    showFieldError(repeatPasswordField, 'Пароли не совпадают');
                }
            }
        });
    }
    
    if (repeatPasswordField) {
        repeatPasswordField.addEventListener('input', function() {
            hideServerErrors(repeatPasswordField);
            if (passwordField && passwordField.value) {
                if (passwordField.value === repeatPasswordField.value) {
                    hideFieldError(repeatPasswordField);
                } else {
                    showFieldError(repeatPasswordField, 'Пароли не совпадают');
                }
            } else {
                hideFieldError(repeatPasswordField);
            }
        });
    }
});

