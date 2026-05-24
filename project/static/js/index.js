document.addEventListener('DOMContentLoaded', ()=> {
    
    // var elems = document.querySelectorAll('select');
    // var options = document.querySelectorAll('option');
    // var instances = M.FormSelect.init(elems, options);

    
    // const myButton = document.getElementById('myButton');
    // if (myButton) {
    //     myButton.addEventListener('click', ()=> {
    //         alert('Clicked!');
    //     });
    // }
    

    var elems = document.querySelectorAll('.sidenav');
    var instances = M.Sidenav.init(elems, options);
    });

    // Initialize collapsible (uncomment the lines below if you use the dropdown variation)
    // var collapsibleElem = document.querySelector('.collapsible');
    // var collapsibleInstance = M.Collapsible.init(collapsibleElem, options);
    // Or with jQuery
    $(document).ready(function(){
    $('.sidenav').sidenav();
    });

    


console.log("Hello from index.js!");