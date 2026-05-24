document.addEventListener('DOMContentLoaded', ()=> {
    
    var elems = document.querySelectorAll('select');
    var options = document.querySelectorAll('option');
    var instances = M.FormSelect.init(elems, options);

    
    const myButton = document.getElementById('myButton');
    if (myButton) {
        myButton.addEventListener('click', ()=> {
            alert('Clicked!');
        });
    }
    


    
});

console.log("Hello from index.js!");