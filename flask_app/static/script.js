function openModal() {
    document.getElementById("companyModal").style.display = "block";
}

function closeModal() {
    document.getElementById("companyModal").style.display = "none";
}

document.getElementById("company-create-btn").addEventListener("click", openModal);

document.getElementById("companyForm").addEventListener("submit", function (event) {
    event.preventDefault();  // Prevent the form from submitting traditionally

    // Handle form submission (you can use AJAX to send the form data to the server)
    // For simplicity, we'll just log the form data for now
    const formData = new FormData(event.target);
    for (const [key, value] of formData.entries()) {
        console.log(`${key}: ${value}`);
    }

    // Close the modal after form submission (you can customize this behavior)
    closeModal();
});
