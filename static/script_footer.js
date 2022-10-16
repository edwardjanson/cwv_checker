// Check for user input of radio on Index and display filter fields accordingly
if(window.location.pathname == '/') {
    let radioFilter = document.querySelectorAll('.radio-filter');

    for (let i = 0; i < radioFilter.length; i++) {
        radioFilter[i].addEventListener("change", function() {
            const filterInputs = document.querySelectorAll(".filter-inputs");
            if (this.value === "filter") {
                for (var i=0;i<filterInputs.length;i+=1) {
                    filterInputs[i].style.display = "flex";
                }
            } else {
                for (var i=0;i<filterInputs.length;i+=1) {
                    filterInputs[i].style.display = "none";
                }
            }
        });
    }
}

// Show loading div once form has been successfully submitted
// if(window.location.pathname == '/') {
//     const indexForm = document.getElementById("indexForm")
//     const loading = document.getElementById("loading")

//     indexForm.addEventListener("submit", function() {
//             loading.style.display = "block";
//             indexForm.style.display = "none";
//         }
//     );
// }

// Change domain label on index form to red if domain returns an error
if (window.location.search.indexOf('error=domain') === 1) {
    document.getElementById('domainHelp').style.setProperty('color', 'red', 'important');
}