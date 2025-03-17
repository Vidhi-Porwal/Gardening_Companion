
    document.addEventListener('DOMContentLoaded', function () {
        const form = document.getElementById('signupForm');
        const password = document.getElementById('password');
        const confirmPassword = document.getElementById('confirm_password');
        const errorDiv = document.getElementById('password_error');

        form.addEventListener('submit', function (event) {
            if (password.value !== confirmPassword.value) {
                errorDiv.style.display = 'block';
                event.preventDefault();  // Stop form submission
            } else {
                errorDiv.style.display = 'none';
            }
        });
    });

    function togglePasswordVisibility(fieldId) {
        const field = document.getElementById(fieldId);
        field.type = field.type === 'password' ? 'text' : 'password';
    }

    //flash message timeout
document.addEventListener("DOMContentLoaded", function () {
    setTimeout(function () {
        let alerts = document.querySelectorAll(".alert");
        alerts.forEach(function (alert) {
            alert.classList.remove("show"); 
            alert.classList.add("fade");
            setTimeout(() => alert.remove(), 500); 
        });
    }, 5000);
});
