document.addEventListener("DOMContentLoaded", function () {
    // Function to toggle password visibility
    function togglePassword(fieldId) {
        var field = document.getElementById(fieldId);
        var button = field.nextElementSibling; // Get the button next to the input

        if (field.type === "password") {
            field.type = "text";
            button.textContent = "Hide";
        } else {
            field.type = "password";
            button.textContent = "Show";
        }
    }

    // Attach togglePassword function to buttons
    document.querySelectorAll(".password-container button").forEach(function (button) {
        button.addEventListener("click", function () {
            var field = this.previousElementSibling; // Get the input field before the button
            togglePassword(field.id);
        });
    });

    // Validate password on form submission
    document.querySelector("form").addEventListener("submit", function (event) {
        var password = document.getElementById("password").value;
        var confirmPassword = document.getElementById("confirm_password").value;
        var passwordError = document.getElementById("password-error");

        var regex = /^(?=.*[A-Za-z])(?=.*\d).{8,}$/; // At least one letter and one number

        if (!regex.test(password)) {
            passwordError.style.display = "block";
            event.preventDefault(); // Stop form submission
            return false;
        } else {
            passwordError.style.display = "none";
        }

        if (password !== confirmPassword) {
            alert("Passwords do not match!");
            event.preventDefault(); // Stop form submission
            return false;
        }

        return true; // Allow form submission
    });

    // Flash message timeout
    setTimeout(function () {
        let alerts = document.querySelectorAll(".alert");
        alerts.forEach(function (alert) {
            alert.classList.remove("show");
            alert.classList.add("fade");
            setTimeout(() => alert.remove(), 500);
        });
    }, 5000);
});
