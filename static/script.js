function openForm(assessmentId) {
    var form = document.getElementById("myForm" + assessmentId);
    form.style.display = "block";  // Open the form
}

function closeForm(assessmentId) {
    var form = document.getElementById("myForm" + assessmentId);
    form.style.display = "none";  // Close the form
}