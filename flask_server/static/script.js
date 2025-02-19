const dropZone = document.getElementById("drop-zone");

// Highlight the drop zone on dragover
dropZone.addEventListener("dragover", (event) => {
    event.preventDefault();
    dropZone.classList.add("dragover");
});

// Remove highlight when dragging leaves the drop zone
dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("dragover");
});

// Handle dropped files
dropZone.addEventListener("drop", (event) => {
    event.preventDefault();
    dropZone.classList.remove("dragover");

    const files = Array.from(event.dataTransfer.files);
    if (files.length === 0) {
        alert("No files dropped.");
        return;
    }

    const formData = new FormData();
    files.forEach((file) => {
        formData.append("files", file);
    });

    uploadFiles(formData);
});

// Upload files to the backend
function uploadFiles(formData) {
    fetch("/upload", {
        method: "POST",
        body: formData,
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.message) {
                alert(data.message);
            } else if (data.error) {
                alert(`Error: ${data.error}`);
            }
        })
        .catch((error) => {
            alert("An error occurred while uploading the files.");
            console.error(error);
        });
}
