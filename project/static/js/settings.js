/**
 * Обработка формы настроек профиля
 */
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.querySelector('input[type="file"][name="avatar"]');
    const newAvatarPreview = document.getElementById('new-avatar-preview');
    
    if (fileInput && newAvatarPreview) {
        // Делаем блок превью кликабельным
        newAvatarPreview.addEventListener('click', function() {
            fileInput.click();
        });
        
        // Обработка выбора файла
        fileInput.addEventListener('change', function(e) {
            if (this.files && this.files.length > 0) {
                const file = this.files[0];
                
                // Проверяем, что это изображение
                if (file.type.startsWith('image/')) {
                    const reader = new FileReader();
                    
                    reader.onload = function(e) {
                        // Создаем изображение для превью
                        const img = document.createElement('img');
                        img.src = e.target.result;
                        img.className = 'avatar-preview-img';
                        img.alt = 'New avatar preview';
                        
                        // Очищаем контейнер и добавляем изображение
                        newAvatarPreview.innerHTML = '';
                        newAvatarPreview.appendChild(img);
                        newAvatarPreview.classList.remove('avatar-preview-placeholder', 'clickable-avatar-preview');
                    };
                    
                    reader.readAsDataURL(file);
                } else {
                    alert('Пожалуйста, выберите файл изображения');
                    this.value = '';
                    newAvatarPreview.innerHTML = '<span>Select file</span>';
                    newAvatarPreview.classList.add('avatar-preview-placeholder', 'clickable-avatar-preview');
                }
            } else {
                // Если файл не выбран, возвращаем к исходному состоянию
                newAvatarPreview.innerHTML = '<span>Select file</span>';
                newAvatarPreview.classList.add('avatar-preview-placeholder', 'clickable-avatar-preview');
            }
        });
    }
    
    // Проверка перед отправкой формы
    const form = document.querySelector('.settings-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            const fileInput = this.querySelector('input[type="file"][name="avatar"]');
            if (fileInput && fileInput.files && fileInput.files.length > 0) {
                console.log('Файл выбран:', fileInput.files[0].name);
            } else {
                console.log('Файл не выбран');
            }
        });
    }
});

