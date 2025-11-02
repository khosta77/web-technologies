document.addEventListener('DOMContentLoaded', function() {
    const avatarBtn = document.getElementById('avatarBtn');
    const dropdownMenu = document.getElementById('dropdownMenu');
    const userDropdown = document.getElementById('userDropdown');
    
    if (avatarBtn && dropdownMenu && userDropdown) {
        userDropdown.addEventListener('mouseenter', function() {
            dropdownMenu.classList.add('show');
        });
        
        userDropdown.addEventListener('mouseleave', function() {
            dropdownMenu.classList.remove('show');
        });
        
        userDropdown.addEventListener('click', function(e) {
            const avatarLink = document.querySelector('.avatar-link');
            if (avatarLink && !avatarLink.contains(e.target)) {
                e.preventDefault();
                e.stopPropagation();
                dropdownMenu.classList.toggle('show');
            }
        });
        
        document.addEventListener('click', function(e) {
            if (!dropdownMenu.contains(e.target) && !userDropdown.contains(e.target)) {
                dropdownMenu.classList.remove('show');
            }
        });
    }
});

