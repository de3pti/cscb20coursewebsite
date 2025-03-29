function ButtontoTextBox(assessment_name){
    var container = document.getElementById('regradeFormContainer-' + assessment_name);
    if (container.className === "hide") {
        container.className = "show";
    } else {
        container.className = "hide";
    }
}