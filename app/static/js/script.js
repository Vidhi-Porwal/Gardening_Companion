document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('modal');
    const addPlantBtn = document.getElementById('add-plant-btn');
    const closeBtn = document.querySelector('.close');

    addPlantBtn.addEventListener('click', () => {
        modal.style.display = 'flex';
    });

    closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
});
