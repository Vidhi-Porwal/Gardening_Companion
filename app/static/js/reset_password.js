
    document.addEventListener("DOMContentLoaded", function () {
        // Attach event listeners to show/hide password buttons
        document.querySelectorAll(".toggle-password").forEach(function (button) {
            button.addEventListener("click", function () {
                var field = document.getElementById(this.dataset.target);
                if (field.type === "password") {
                    field.type = "text";
                    this.textContent = "Hide";
                } else {
                    field.type = "password";
                    this.textContent = "Show";
                }
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
    });

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

