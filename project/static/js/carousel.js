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
    const carouselItems = document.querySelectorAll('.carousel-item[data-url]');
        
        carouselItems.forEach(item => {

            item.addEventListener('click', (e) => {

                const carouselEl = item.closest('.carousel');

                const instance = M.Carousel.getInstance(carouselEl);

                if (instance && instance.dragged) {
                    e.preventDefault();
                    return;
                }

                if (item.classList.contains('active')) {
                    window.location.href = item.getAttribute('data-url');
                }
            });
        });
});
