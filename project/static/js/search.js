document.addEventListener('DOMContentLoaded', function() {
    const searchToggle = document.querySelector('.search-toggle-icon');
    const searchWidget = document.getElementById('searchWidget');
    const searchClose = document.getElementById('searchClose');
    const searchInput = document.getElementById('searchInput');
    const searchInputField = document.getElementById('searchInputField');
    
    // Функция для выполнения поиска
    function performSearch(query) {
        if (query.trim()) {
            console.log('[Search.js]:', query);

        }
    }
    
    function syncSearchFields() {
        const searchInputField = document.getElementById('searchInputField');
        const searchInput = document.getElementById('searchInput');
        
        if (searchInputField && searchInput) {
            searchInput.addEventListener('input', function() {
                searchInputField.value = this.value;
            });
            
            searchInputField.addEventListener('input', function() {
                searchInput.value = this.value;
            });
        }
    }
    
    // Обработка изменения размера окна
    function handleResize() {
        const searchWidget = document.getElementById('searchWidget');
        const searchInputField = document.getElementById('searchInputField');
        const searchInput = document.getElementById('searchInput');
        
        // Если окно стало широким (десктоп) и виджет открыт
        if (window.innerWidth >= 769 && searchWidget.classList.contains('active')) {
            if (searchInput && searchInputField) {
                searchInputField.value = searchInput.value;
            }
            searchWidget.classList.remove('active');
            if (searchInput) {
                searchInput.value = '';
            }
        }
        
        // Если окно стало узким (мобильная версия) и есть текст в поле шапки
        if (window.innerWidth < 769 && searchInputField && searchInputField.value.trim()) {
            if (searchInput) {
                searchInput.value = searchInputField.value;
            }
            searchWidget.classList.add('active');
            searchInputField.value = '';
        }
    }
    
    searchToggle.addEventListener('click', function() {
        if (searchInputField && searchInputField.value.trim() && searchInput) {
            searchInput.value = searchInputField.value;
            searchInputField.value = '';
        }
        
        searchWidget.classList.add('active');
        setTimeout(() => {
            searchInput.focus();
        }, 100);
    });
    
    searchClose.addEventListener('click', function() {
        searchWidget.classList.remove('active');
        searchInput.value = '';
    });
    
    searchWidget.addEventListener('click', function(e) {
        if (e.target === searchWidget) {
            searchWidget.classList.remove('active');
            searchInput.value = '';
        }
    });
    
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && searchWidget.classList.contains('active')) {
            searchWidget.classList.remove('active');
            searchInput.value = '';
        }
    });
    
    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            const query = searchInput.value.trim();
            performSearch(query);
        }
    });
    
    searchInputField.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            const query = searchInputField.value.trim();
            performSearch(query);
        }
    });
    
    
    syncSearchFields();
    window.addEventListener('resize', handleResize);
});
