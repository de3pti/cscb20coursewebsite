function openForm(assessmentId) {
    var form = document.getElementById("myForm" + assessmentId);
    form.style.display = "block"; 
}

function closeForm(assessmentId) {
    var form = document.getElementById("myForm" + assessmentId);
    form.style.display = "none";  
}