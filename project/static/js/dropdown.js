document.addEventListener('DOMContentLoaded', function() {
    const avatarBtn = document.getElementById('avatarBtn');
    const dropdownMenu = document.getElementById('dropdownMenu');
    const userDropdown = document.getElementById('userDropdown');
    
    if (avatarBtn && dropdownMenu && userDropdown) {
        let hideTimeout = null;
        
        function showDropdown() {
            if (hideTimeout) {
                clearTimeout(hideTimeout);
                hideTimeout = null;
            }
            dropdownMenu.classList.add('show');
        }
        
        function hideDropdown() {
            hideTimeout = setTimeout(function() {
                dropdownMenu.classList.remove('show');
                hideTimeout = null;
            }, 150);
        }
        
        function cancelHide() {
            if (hideTimeout) {
                clearTimeout(hideTimeout);
                hideTimeout = null;
            }
        }
        
        userDropdown.addEventListener('mouseenter', showDropdown);
        userDropdown.addEventListener('mouseleave', hideDropdown);
        dropdownMenu.addEventListener('mouseenter', cancelHide);
        dropdownMenu.addEventListener('mouseenter', showDropdown);
        dropdownMenu.addEventListener('mouseleave', hideDropdown);
        
        const avatarLink = document.querySelector('.avatar-link');
        if (avatarLink) {
            avatarLink.addEventListener('click', function(e) {
                if (dropdownMenu.classList.contains('show')) {
                    dropdownMenu.classList.remove('show');
                } else {
                    e.preventDefault();
                    dropdownMenu.classList.add('show');
                }
            });
        }
        
        document.addEventListener('click', function(e) {
            if (!dropdownMenu.contains(e.target) && !userDropdown.contains(e.target)) {
                dropdownMenu.classList.remove('show');
                if (hideTimeout) {
                    clearTimeout(hideTimeout);
                    hideTimeout = null;
                }
            }
        });
    }
});

