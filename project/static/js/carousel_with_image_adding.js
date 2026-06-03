document.addEventListener('DOMContentLoaded', function () {


    // Динамическая логика карусели
    var fileInput = document.querySelector('#tab-image input[type="file"]');
    var carouselContainer = document.getElementById('dynamic-carousel-container');

    if (fileInput && carouselContainer) {
        var carouselEl = carouselContainer.querySelector('.carousel');

        // Создаем специальное хранилище, которое будет накапливать файлы
        var accumulatedFiles = new DataTransfer();

        fileInput.addEventListener('change', function (event) {

            if (this.files && this.files.length > 0) {

                // 1. Добавляем новые файлы в наше хранилище
                Array.from(this.files).forEach(function (file) {
                    // Защита: добавляем только картинки
                    if (file.type.startsWith('image/')) {
                        accumulatedFiles.items.add(file);
                    }
                });

                // запист файликов обратно в input
                this.files = accumulatedFiles.files;

                // Уничтожаем старую карусель
                var instance = M.Carousel.getInstance(carouselEl);
                if (instance) {
                    instance.destroy();
                }

                // Очищаем внутренности карусели
                carouselEl.innerHTML = '';

                // 3. Строим слайды
                Array.from(this.files).forEach(function (file, index) {
                    var imageUrl = URL.createObjectURL(file);
                    var newSlide = document.createElement('div');
                    newSlide.className = 'carousel-item white-text';
                    newSlide.href = '#slide-' + index + '!';

                    newSlide.innerHTML = `
                    <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100%; padding: 10px; box-sizing: border-box; user-select: none">                     
                        <img src="${imageUrl}" class="image-preview" style="max-width: 100%; max-height: 80%; object-fit: contain;">
                        <div style="margin-top: 10px;">
                            <span style="background: rgba(0,0,0,0.5); padding: 4px 10px; border-radius: 4px; font-size: 0.8rem; user-select: none;">
                                ${file.name}
                            </span>
                        </div>            
                    </div>`;

                    carouselEl.appendChild(newSlide);
                });

                // Запускаем карусель, если есть хотя бы один слайд
                if (carouselEl.children.length > 0) {
                    carouselContainer.style.display = 'block';
                    M.Carousel.init(carouselEl, {
                        fullWidth: true,
                        indicators: true
                    });
                }

            }
        });
    }
});