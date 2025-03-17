// user_profile
document.addEventListener("DOMContentLoaded", function () {
    const editButton = document.getElementById("edit-button");
    const saveButton = document.getElementById("save-button");
    const cancelButton = document.getElementById("cancel-button");
    const inputs = ["full_name", "username", "phone_no"].map(id => document.getElementById(id));

    if (editButton) {
        editButton.addEventListener("click", function () {
            inputs.forEach(input => input.removeAttribute("disabled"));
            editButton.classList.add("d-none");
            saveButton.classList.remove("d-none");
            cancelButton.classList.remove("d-none");
        });
    }

    if (cancelButton) {
        cancelButton.addEventListener("click", function () {
            inputs.forEach(input => {
                input.setAttribute("disabled", "true");
                input.value = input.defaultValue; // Reset to original values
            });
            editButton.classList.remove("d-none");
            saveButton.classList.add("d-none");
            cancelButton.classList.add("d-none");
        });
    }
});
