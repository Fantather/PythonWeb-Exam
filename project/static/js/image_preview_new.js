function setupImagePreview(inputId, previewContainerSelector, imageClass = '') {
    const fileInput = document.getElementById(inputId);
    const previewContainer = document.querySelector(previewContainerSelector);

    if (fileInput && previewContainer) {
        fileInput.addEventListener('change', function (event) {
            const file = event.target.files[0];

            if (file) {
                let imgElement = previewContainer.querySelector('img');

                if (!imgElement) {
                    imgElement = document.createElement('img');

                    // Если передан класс, применяем его
                    if (imageClass) {
                        imgElement.className = imageClass;
                    } else {
                        // Иначе применяем дефолтные стили (круглый аватар 150х150)
                        imgElement.style.maxWidth = '150px';
                        imgElement.style.height = '150px';
                        imgElement.style.objectFit = 'cover';
                        imgElement.style.marginTop = '15px';
                        imgElement.style.borderRadius = '50%';
                    }

                    previewContainer.appendChild(imgElement);
                }

                imgElement.src = URL.createObjectURL(file);

                imgElement.onload = function () {
                    URL.revokeObjectURL(imgElement.src);
                }
            }
        });
    }
}

