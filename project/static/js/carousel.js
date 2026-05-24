document.addEventListener('DOMContentLoaded', function() {
    var elems = document.querySelectorAll('.carousel');
    
    elems.forEach(function(carouselEl) {
        // если есть крарточки то карусель
        if (carouselEl.querySelectorAll('.carousel-item').length > 0) {
            M.Carousel.init(carouselEl, {
                dist: -50,
                shift: 10,   
                padding: 10,    
                numVisible: 5  
            });
        }
    });
});