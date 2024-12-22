document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search');
    const plantCards = document.querySelectorAll('.card');

    searchInput.addEventListener('input', (event) => {
        const query = event.target.value.toLowerCase();
        plantCards.forEach((card) => {
            const plantName = card.querySelector('.card-title').textContent.toLowerCase();
            card.style.display = plantName.includes(query) ? '' : 'none';
        });
    });

    // Initialize Bootstrap modal
    const modal = new bootstrap.Modal(document.getElementById('modal'));
    const addPlantBtn = document.getElementById('add-plant-btn');
    addPlantBtn.addEventListener('click', () => {
        modal.show();
    });
});
