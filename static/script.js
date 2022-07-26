// Loading message handler 
let exitLoading = document.getElementsByClassName('close')[0]; 
let modalLoading = document.getElementsByClassName('modal')[0];

exitLoading.addEventListener('click', () => {
    modalLoading.style.display = "none";
});

// Error message handler
let exit = document.getElementsByClassName('close')[1]; 
let modal = document.getElementsByClassName('modal')[1];

exit.addEventListener('click', () => {
    modal.style.display = "none";
});


let submit = document.getElementById("submit"); 
let field = document.getElementById("ticker"); 
let form = document.querySelector("form"); 

submit.addEventListener('click', (event) => {

    // Automatically return if the form is empty
    if(!form.checkValidity()) {
        return; 
    } 

    // Get and validate the submitted value 
    let ticker = field.value;

    let re = /^[A-Za-z]+$/; 
    if(!re.test(ticker)) {
        alert("Please enter a valid ticker symbol"); 
        event.preventDefault(); 
        field.value = ""; 
        return; 
    }

    // Display a loading message 
    modalLoading.style.display = "block"; 
    submit.disabled = true; 

    // Make API call 
    event.preventDefault(); 
    fetch(`/?ticker=${ticker}`)
    .then((res) => {

        // If there was a server error, display an error message 
        if(res.status == 500) {
            return Promise.reject("Server error"); 
        }

        // Otherwise process the returned file 
        return res.blob(); 
    })
    .then((blob) => {

        // Blob stuff
        const newBlob = new Blob([blob]); 
        const blobUrl = window.URL.createObjectURL(newBlob);
  
        // Download sent file 
        const link = document.createElement('a');
        link.href = blobUrl;
        link.setAttribute('download', `DCF_${ticker}.xlsx`);
        document.body.appendChild(link);
        link.click();
        link.parentNode.removeChild(link);

        window.URL.revokeObjectURL(blobUrl);

        // Remove loading display once file has been downloaded
        modalLoading.style.display = "none"; 
        field.value = ''; 
        submit.disabled = false;
    })
    .catch((err) => {
        // Display an error message if something went wrong
        modalLoading.style.display = "none"; 
        modal.style.display = "block"; 
        field.value = ''; 
        submit.disabled = false;
    }); 

}); 

