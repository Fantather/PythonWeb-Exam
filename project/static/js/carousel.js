document.addEventListener('DOMContentLoaded', function() {
        var elems = document.querySelectorAll('.carousel');
        var instances = M.Carousel.init(elems, {
            dist: -50,
            shift: 10,   
            padding: 10,    
            numVisible: 5  
        });
    });
