/*!
* Start Bootstrap - Clean Blog v6.0.9 (https://startbootstrap.com/theme/clean-blog)
* Copyright 2013-2023 Start Bootstrap
* Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-clean-blog/blob/master/LICENSE)
*/
window.addEventListener('DOMContentLoaded', () => {
    let scrollPos = 0;
    const mainNav = document.getElementById('mainNav');
    const headerHeight = mainNav.clientHeight;
    window.addEventListener('scroll', function() {
        const currentTop = document.body.getBoundingClientRect().top * -1;
        if ( currentTop < scrollPos) {
            // Scrolling Up
            if (currentTop > 0 && mainNav.classList.contains('is-fixed')) {
                mainNav.classList.add('is-visible');
            } else {
                console.log(123);
                mainNav.classList.remove('is-visible', 'is-fixed');
            }
        } else {
            // Scrolling Down
            mainNav.classList.remove(['is-visible']);
            if (currentTop > headerHeight && !mainNav.classList.contains('is-fixed')) {
                mainNav.classList.add('is-fixed');
            }
        }
        scrollPos = currentTop;
    });
})
// dashboard modal
    document.addEventListener('DOMContentLoaded', () => {
const plantDetailsModal = document.getElementById('plantDetailsModal');

document.addEventListener('click', (event) => {
    if (event.target.classList.contains('plant-card-image')) {
        const image = event.target;

        // Fetch data attributes
        const plantId = image.dataset.id;
        const plantName = image.dataset.name;
        const plantScientificName = image.dataset.scientificName;
        const plantRank = image.dataset.rank;
        const plantFamily = image.dataset.family;
        const plantGenus = image.dataset.genus;
        const plantEdible = image.dataset.edible;
        const plantSaplingDescription = image.dataset.saplingDescription;
        const plantImageUrl = image.dataset.imageUrl;

        // Populate modal content
        document.getElementById('plantImage').src = plantImageUrl;
        document.getElementById('plantName').textContent = plantName;
        document.getElementById('plantScientificName').textContent = plantScientificName;
        document.getElementById('plantRank').textContent = plantRank;
        document.getElementById('plantFamily').textContent = plantFamily;
        document.getElementById('plantGenus').textContent = plantGenus;
        document.getElementById('plantEdible').textContent = plantEdible;
        document.getElementById('plantSaplingDescription').textContent = plantSaplingDescription;

        // Show the modal
        const bootstrapModal = new bootstrap.Modal(plantDetailsModal);
        bootstrapModal.show();
    }
});
});


// select garden dropdown
document.getElementById('gardenSelector').addEventListener('change', function () {
    const selectedGarden = this.value;
    document.querySelectorAll('.col-md-4').forEach(plantCard => {
        const gardenId = plantCard.dataset.gardenId;
        plantCard.style.display = (selectedGarden === 'all' || gardenId === selectedGarden) ? '' : 'none';
    });
});

//add garden
function handleGardenSelection(select) {
    if (select.value === "add") {
        // Show the "Add Garden" modal
        new bootstrap.Modal(document.getElementById('addGardenModal')).show();
        select.value = "default"; // Reset dropdown selection after showing modal
    }
}


// profile
    function toggleEdit() {
        const fields = document.querySelectorAll('.profile-details input');
        const saveButton = document.getElementById('save-button');
        const editButton = document.querySelector('[onclick="toggleEdit()"]');
        
        fields.forEach(field => field.readOnly = !field.readOnly);
        saveButton.classList.toggle('d-none');
        editButton.textContent = fields[0].readOnly ? "Edit Profile" : "Cancel Editing";
    }
    function scrollToBottom() {
        var chatBody = document.getElementById('chat-body');
        chatBody.scrollTop = chatBody.scrollHeight;
    }
    
    // Ensure we scroll on page load and when a new message is sent
    window.onload = scrollToBottom; // Scroll when the page is loaded
    document.querySelector('form').onsubmit = scrollToBottom;