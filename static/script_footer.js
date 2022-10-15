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

// Show loading div once form has been successfully submitted and update progress bar

// function updateProgress() {
//     return new Promise(resolve => {
//         let myInterval = setInterval(async function() {
//             console.log("new")
//             let response = await fetch("/progress");
//             let currentProgress = await response.text();
//             if(currentProgress === true) {
//                 document.querySelector('main').innerHTML = currentProgress;
//                 console.log(currentProgress)
//                 clearInterval(myInterval);
//                 resolve()
//             }
//         },1000);        
//     })
// }

if(window.location.pathname == '/') {
    const indexForm = document.getElementById("indexForm")

    indexForm.addEventListener("submit", async function() {
        setInterval(async function() {
            console.log("new")
            // updateProgress();
            let response = await fetch("/progress");
            let currentProgress = await response.text();
            console.log('FUNCTION OUTPUT: ', currentProgress)
            document.querySelector('main').innerHTML = currentProgress;
            console.log('FUNCTION OUTPUT: ', document.querySelector('main').innerHTML)
        }, 1000);
    });
}


// Change domain label on index form to red if domain returns an error
if (window.location.search.indexOf('error=domain') === 1) {
    document.getElementById('domainHelp').style.setProperty('color', 'red', 'important');
}




// async function updateProgress() {
//     console.log("new")
//     let response = await fetch("/progress");
//     let currentProgress = await response.text();
//     console.log('FUNCTION OUTPUT: ', currentProgress)
//     return currentProgress;
// }

// if(window.location.pathname == '/') {
//     const indexForm = document.getElementById("indexForm")

//     indexForm.addEventListener("submit", function() {
//         // setInterval(function() {
//             updateProgress().then(value => {
//                 document.querySelector('main').innerHTML = value;
//             });
//         // }, 1000);
//     });
// }