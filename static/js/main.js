document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', (e) => {
            const password = document.querySelector('input[type="password"]').value;
            if (password.length < 6) {
                alert('పాస్‌వర్డ్ కనీసం 6 అక్షరాలు ఉండాలి!');
                e.preventDefault();
            }
        });
    }
});