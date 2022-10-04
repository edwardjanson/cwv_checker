// Check for user input of radio on Index and display filter fields accordingly
// document.querySelector("#radio-domain").addEventListener("click", filterCheck(this));
// document.querySelector("#radio-filter").addEventListener("click", filterCheck(this));

// function filterCheck(e) {
//     const filterInputs = document.querySelector("#filter-inputs");
//     if (e.value === "filter")
//     {
//         alert("yes");
//         filterInputs.style.display = "block";
//     } else {
//         filterInputs.style.display = "none";
//     }
// }

// let radioFilter = document.querySelectorAll('.radio-filter');

// for (let i = 0; i < radioFilter.length; i++) {
//     radioFilter[i].addEventListener("change", function() {
//         const filterInputs = document.querySelector("#filter-inputs");
//         if (this.value === "filter") {
//             filterInputs.style.display = "block";
//         } else {
//             filterInputs.style.display = "none";
//         }
//   });
// }


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