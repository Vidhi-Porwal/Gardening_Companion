window.onload = function() {
    const urlParams = new URLSearchParams(window.location.search);
    document.getElementById('commonName').value = urlParams.get('commonName') || '';
    document.getElementById('saplingDescription').value = urlParams.get('saplingDescription') || '';
};


function addPlant() {
    const urlParams = new URLSearchParams(window.location.search);
    const requestId = urlParams.get('request_id'); // Get request_id from URL
    console.log("request_id",requestId)
    const plantData = {
        commonName: document.getElementById('commonName').value,
        scientificName: document.getElementById('scientificName').value,
        rank: document.getElementById('rank').value,
        familyCommonName: document.getElementById('familyCommonName').value,
        genus: document.getElementById('genus').value,
        imageURL: document.getElementById('imageURL').value,
        edible: document.getElementById('edible').checked,
        saplingDescription: document.getElementById('saplingDescription').value
    };

    let apiUrl = '/dashboard/add_plant';
    if (requestId) {
        apiUrl += `?request_id=${requestId}`; // Append request_id if available
    }

    fetch(apiUrl, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(plantData)
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        window.location.href = '/dashboard/admin/pending_plants'; // Redirect to pending plants
    })
    .catch(error => console.error('Error:', error));
}

        function searchTable(inputId, tableId) {
            let input = document.getElementById(inputId);
            let filter = input.value.toLowerCase();
            let table = document.getElementById(tableId);
            let rows = table.getElementsByTagName("tr");

            for (let i = 1; i < rows.length; i++) { // Start from 1 to skip table header
                let cells = rows[i].getElementsByTagName("td");
                let match = false;

                for (let j = 0; j < cells.length; j++) {
                    if (cells[j].innerText.toLowerCase().includes(filter)) {
                        match = true;
                        break;
                    }
                }

                rows[i].style.display = match ? "" : "none";
            }
        }

        function deleteUser(userId) {
            if (confirm("Are you sure you want to delete this user?")) {
                console.log("delete user")
                fetch(`/dashboard/delete_user/${userId}`, { method: "DELETE" })
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    location.reload();
                });
            }
        }

        function deletePlant(plantId) {
            if (confirm("Are you sure you want to delete this plant?")) {
                fetch(`/dashboard/delete_plant/${plantId}`, { method: "DELETE" })
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    location.reload();
                });
            }
        }
        function updateUserRole(userId) {
        const newRole = prompt("Enter new role (admin/user):").trim().toLowerCase();

        if (!newRole || (newRole !== "admin" && newRole !== "user")) {
            alert("Invalid role! Please enter 'admin' or 'user'.");
            return;
        }

        fetch(`/dashboard/update_user_role/${userId}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ role: newRole })
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            location.reload();  // ✅ Refresh page to reflect changes
        })
        .catch(error => {
            console.error("Error updating user role:", error);
            alert("Failed to update user role.");
        });
}
let currentPlantId = null;

function openEditForm(plantId) {
    currentPlantId = plantId;
    document.getElementById("editPlantModal").style.display = "block";

    // Fetch plant details and pre-fill the form
    fetch(`/dashboard/get_plant/${plantId}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById("editCommonName").value = data.commonName;
            document.getElementById("editScientificName").value = data.scientificName;
            document.getElementById("editRank").value = data.rank;
            document.getElementById("editFamilyCommonName").value = data.familyCommonName;
            document.getElementById("editGenus").value = data.genus;
            document.getElementById("editImageURL").value = data.imageURL;
            document.getElementById("editEdible").checked = data.edible;
            document.getElementById("editSaplingDescription").value = data.saplingDescription;
        });
}

function closeEditForm() {
    document.getElementById("editPlantModal").style.display = "none";
}
function editPlant(plantId) {
    const plantData = {
        commonName: document.getElementById('editCommonName').value,
        scientificName: document.getElementById('editScientificName').value,
        rank: document.getElementById('editRank').value,
        familyCommonName: document.getElementById('editFamilyCommonName').value,
        genus: document.getElementById('editGenus').value,
        imageURL: document.getElementById('editImageURL').value,
        edible: document.getElementById('editEdible').checked,
        saplingDescription: document.getElementById('editSaplingDescription').value
    };

    fetch(`/dashboard/edit_plant/${plantId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(plantData)
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        location.reload();
    })
    .catch(error => console.error("Error:", error));
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

