document.addEventListener('DOMContentLoaded', function () {
    var fileInput = document.querySelector('#tab-image input[type="file"]');
    var carouselContainer = document.getElementById('dynamic-carousel-container');

    // Хранилище для URL картинок, чтобы освобождать память
    var objectUrls = [];

    if (fileInput && carouselContainer) {
        var carouselEl = carouselContainer.querySelector('.carousel');
        var accumulatedFiles = new DataTransfer();

        // Выносим логику рендеринга в отдельную функцию
        function renderCarousel() {
            // Очищаем память от старых ссылок
            objectUrls.forEach(function (url) {
                URL.revokeObjectURL(url);
            });
            objectUrls = [];

            var instance = M.Carousel.getInstance(carouselEl);
            if (instance) {
                instance.destroy();
            }

            carouselEl.innerHTML = '';

            // Строим новые слайды
            Array.from(accumulatedFiles.files).forEach(function (file, index) {
                var imageUrl = URL.createObjectURL(file);
                objectUrls.push(imageUrl); // Сохраняем для последующей очистки

                var newSlide = document.createElement('div');
                newSlide.className = 'carousel-item white-text';
                newSlide.href = '#slide-' + index + '!';

                // Добавлена кнопка удаления с атрибутом data-index
                newSlide.innerHTML = `
                <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100%; padding: 10px; box-sizing: border-box; user-select: none; position: relative;">                     
                    <button type="button" class="btn-floating red remove-image-btn" data-index="${index}" style="position: absolute; top: 10px; right: 10px; z-index: 10;">
                        <span style="font-size: 1.5rem; font-weight: bold; line-height: 40px;">&times;</span>
                    </button>
                    <img src="${imageUrl}" class="image-preview" style="max-width: 100%; max-height: 80%; object-fit: contain;">
                    <div style="margin-top: 10px;">
                        <span style="background: rgba(0,0,0,0.5); padding: 4px 10px; border-radius: 4px; font-size: 0.8rem; user-select: none;">
                            ${file.name}
                        </span>
                    </div>            
                </div>`;

                carouselEl.appendChild(newSlide);
            });

            // Инициализация или скрытие карусели
            if (carouselEl.children.length > 0) {
                carouselContainer.style.display = 'block';
                M.Carousel.init(carouselEl, {
                    fullWidth: true,
                    indicators: true
                });
            } else {
                carouselContainer.style.display = 'none';
            }

            // Навешиваем обработчики кликов на новые кнопки удаления
            var removeBtns = carouselEl.querySelectorAll('.remove-image-btn');
            removeBtns.forEach(function (btn) {
                btn.addEventListener('click', function (e) {
                    e.preventDefault();
                    var removeIndex = parseInt(this.getAttribute('data-index'), 10);
                    removeFile(removeIndex);
                });
            });
        }

        // Логика удаления файла из DataTransfer
        function removeFile(indexToRemove) {
            var newTransfer = new DataTransfer();

            // Копируем все файлы, кроме того, чей индекс совпадает с удаляемым
            Array.from(accumulatedFiles.files).forEach(function (file, index) {
                if (index !== indexToRemove) {
                    newTransfer.items.add(file);
                }
            });

            accumulatedFiles = newTransfer;
            fileInput.files = accumulatedFiles.files; // Синхронизируем с <input>
            renderCarousel(); // Перерисовываем интерфейс
        }


        fileInput.addEventListener('change', function (event) {
            if (this.files && this.files.length > 0) {
                Array.from(this.files).forEach(function (file) {
                    if (file.type.startsWith('image/')) {
                        accumulatedFiles.items.add(file);
                    }
                });

                this.files = accumulatedFiles.files;
                renderCarousel();
            }
        });
    }
});