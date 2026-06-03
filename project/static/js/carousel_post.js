document.addEventListener('DOMContentLoaded', function(){
    var elems = document.querySelectorAll('.carousel')
    
    elems.forEach(function(carolselEl){
        if (carolselEl.querySelectorAll('.carousel-item').length > 0){
            M.Carousel.init(carolselEl,{
                fullWidth: true,
                indicators: true
            });
        }
    })
    


})