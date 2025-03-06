document.addEventListener("DOMContentLoaded", function () {
    // Navbar Scroll Effect
    const mainNav = document.getElementById('mainNav');
    if (mainNav) {
        let scrollPos = 0;
        const headerHeight = mainNav.clientHeight;
        window.addEventListener('scroll', function () {
            const currentTop = document.body.getBoundingClientRect().top * -1;
            if (currentTop < scrollPos) {
                if (currentTop > 0 && mainNav.classList.contains('is-fixed')) {
                    mainNav.classList.add('is-visible');
                } else {
                    mainNav.classList.remove('is-visible', 'is-fixed');
                }
            } else {
                mainNav.classList.remove('is-visible');
                if (currentTop > headerHeight && !mainNav.classList.contains('is-fixed')) {
                    mainNav.classList.add('is-fixed');
                }
            }
            scrollPos = currentTop;
        });
    }

    // Dashboard Modal
    const plantImages = document.querySelectorAll('.card-img-top');
    const plantDetailsModal = document.getElementById('plantDetailsModal');
    if (plantImages.length > 0 && plantDetailsModal) {
        plantImages.forEach(image => {
            image.addEventListener('click', () => {
                document.getElementById('plantImage').src = image.getAttribute('data-image-url') || '/static/images/default_plant.jpg';
                document.getElementById('plantName').textContent = image.getAttribute('data-name') || 'Unknown';
                document.getElementById('plantScientificName').textContent = image.getAttribute('data-scientific-name') || 'N/A';
                document.getElementById('plantRank').textContent = image.getAttribute('data-rank') || 'N/A';
                document.getElementById('plantFamily').textContent = image.getAttribute('data-family') || 'N/A';
                document.getElementById('plantGenus').textContent = image.getAttribute('data-genus') || 'N/A';
                document.getElementById('plantEdible').textContent = image.getAttribute('data-edible') || 'N/A';
                document.getElementById('plantSaplingDescription').textContent = image.getAttribute('data-sapling-description') || 'N/A';
                document.getElementById('modalPlantId').value = image.getAttribute('data-id');
                new bootstrap.Modal(plantDetailsModal).show();
            });
        });
    }

    // Select Garden Dropdown
    // const gardenSelector = document.getElementById('gardenSelector');
    // if (gardenSelector) {
    //     gardenSelector.addEventListener('change', function () {
    //         if (this.value === "add") {
    //             var addGardenModal = new bootstrap.Modal(document.getElementById("addGardenModal"));
    //             addGardenModal.show();
    //             this.value = "";
    //         } else {
    //             const gardenForm = document.getElementById("gardenForm");
    //             if (gardenForm) gardenForm.submit();
    //         }
    //     });
    // }
    const gardenSelector = document.getElementById('gardenSelector');

if (gardenSelector) {
    gardenSelector.addEventListener('change', function () {
        if (this.value === "add") {
            var addGardenModal = new bootstrap.Modal(document.getElementById("addGardenModal"));
            addGardenModal.show();
            this.value = "";
        } else {
            document.getElementById("selectedGardenId").value = this.value;
            document.getElementById("gardenForm").submit();
        }
    });
}


    // Profile Edit
    const saveButton = document.getElementById('save-button');
    const editButton = document.querySelector('[onclick="toggleEdit()"]');
    if (editButton && saveButton) {
        window.toggleEdit = function () {
            const fields = document.querySelectorAll('.profile-details input');
            fields.forEach(field => field.readOnly = !field.readOnly);
            saveButton.classList.toggle('d-none');
            editButton.textContent = fields[0].readOnly ? "Edit Profile" : "Cancel Editing";
        };
    }

    // Chat Auto-scroll
    function scrollToBottom() {
        const chatBody = document.getElementById('chat-body');
        if (chatBody) chatBody.scrollTop = chatBody.scrollHeight;
    }

    scrollToBottom(); // Scroll when the page loads

    const chatForm = document.querySelector('form');
    if (chatForm) {
        chatForm.onsubmit = scrollToBottom;
    }
   
});

function filterPlants() {
    let garden_id = document.getElementById("gardenSelector").value;
    window.location.href = `/dashboard?garden_id=${garden_id}`;
}


document.addEventListener("DOMContentLoaded", function () {
    const plantDropdownButton = document.getElementById("plantDropdownButton");
    const plantDropdownMenu = document.getElementById("plantDropdownMenu");
    const plantSearch = document.getElementById("plantSearch");
    const plantList = document.getElementById("plantList");
    const selectedPlantInput = document.getElementById("selectedPlant");
    const modal = document.getElementById("addPlantModal");

    // Open dropdown on button click
    plantDropdownButton.addEventListener("click", function () {
        plantDropdownMenu.classList.toggle("show");
    });

    // Close dropdown when clicking outside
    document.addEventListener("click", function (event) {
        if (!plantDropdownButton.contains(event.target) && !plantDropdownMenu.contains(event.target)) {
            plantDropdownMenu.classList.remove("show");
        }
    });

    // Filter plants dynamically based on search input
    plantSearch.addEventListener("input", function () {
        const searchValue = plantSearch.value.toLowerCase();
        const plantOptions = plantList.getElementsByClassName("plant-option");

        for (let i = 0; i < plantOptions.length; i++) {
            let text = plantOptions[i].innerText.toLowerCase();
            plantOptions[i].style.display = text.includes(searchValue) ? "block" : "none";
        }
    });

    // Select a plant and update button text and hidden input
    plantList.addEventListener("click", function (event) {
        if (event.target.classList.contains("plant-option")) {
            event.preventDefault();
            let selectedPlantName = event.target.innerText;
            let selectedPlantId = event.target.getAttribute("data-value");

            // Update button text
            plantDropdownButton.innerText = selectedPlantName;

            // Update hidden input
            selectedPlantInput.value = selectedPlantId;

            // Close the dropdown
            plantDropdownMenu.classList.remove("show");
        }
    });

    // Ensure dropdown closes when the modal closes
    modal.addEventListener("hidden.bs.modal", function () {
        plantDropdownMenu.classList.remove("show");
    });
});