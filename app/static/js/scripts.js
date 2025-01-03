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
        const plantImages = document.querySelectorAll('.card-img-top');
        const plantDetailsModal = document.getElementById('plantDetailsModal');

        plantImages.forEach(image => {
            image.addEventListener('click', () => {
                // Fetch data attributes
                const plantId = image.dataset.id;
                const plantName = image.dataset.name;
                const plantScientificName = image.dataset.scientificName;
                const plantYear = image.dataset.year;
                const plantAuthor = image.dataset.author;
                const plantStatus = image.dataset.status;
                const plantRank = image.dataset.rank;
                const plantFamily = image.dataset.family;
                const plantGenus = image.dataset.genus;
                const plantEdible = image.dataset.edible;
                const plantSaplingDescription = image.dataset.saplingDescription;
                const plantPlantDescription = image.dataset.plantDescription;
                const plantImageUrl = image.dataset.imageUrl;

                // Populate modal content
                document.getElementById('plantImage').src = plantImageUrl;
                document.getElementById('plantName').textContent = plantName;
                document.getElementById('plantScientificName').textContent = plantScientificName;
                document.getElementById('plantYear').textContent = plantYear;
                document.getElementById('plantAuthor').textContent = plantAuthor;
                document.getElementById('plantStatus').textContent = plantStatus;
                document.getElementById('plantRank').textContent = plantRank;
                document.getElementById('plantFamily').textContent = plantFamily;
                document.getElementById('plantGenus').textContent = plantGenus;
                document.getElementById('plantEdible').textContent = plantEdible;
                document.getElementById('plantSaplingDescription').textContent = plantSaplingDescription;
                document.getElementById('plantPlantDescription').textContent = plantPlantDescription;
                document.getElementById('modalPlantId').value = plantId;

                // Show modal
                const bootstrapModal = new bootstrap.Modal(plantDetailsModal);
                bootstrapModal.show();
            });
        });
    });

// profile
    function toggleEdit() {
        const fields = document.querySelectorAll('.profile-details input');
        const saveButton = document.getElementById('save-button');
        const editButton = document.querySelector('[onclick="toggleEdit()"]');
        
        fields.forEach(field => field.readOnly = !field.readOnly);
        saveButton.classList.toggle('d-none');
        editButton.textContent = fields[0].readOnly ? "Edit Profile" : "Cancel Editing";
    }