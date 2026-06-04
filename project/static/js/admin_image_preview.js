function setupImagePreview(inputId = 'id_icon', previewContainerSelector = '.field-icon', imageElement = '.live-preview-img') {
    const iconInput = document.getElementById(inputId);
    const fieldContainer = document.querySelector(previewContainerSelector);

    if (iconInput && fieldContainer) {
        iconInput.addEventListener('change', function (event) {
            const file = event.target.files[0];

            if (file) {
                let imgElement = fieldContainer.querySelector(imageElement);

                if (!imgElement) {
                    imgElement = document.createElement('img');
                    imgElement.className = imageElement.replace('.', '');

                    imgElement.style.maxWidth = '100px';
                    imgElement.style.maxHeight = '100px';
                    imgElement.style.display = 'block';
                    imgElement.style.marginTop = '10px';

                    iconInput.parentNode.appendChild(imgElement);
                }

                imgElement.src = URL.createObjectURL(file);

                imgElement.onload = function () {
                    URL.revokeObjectURL(imgElement.src);
                }
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', function () {
    setupImagePreview('id_icon', '.field-icon', '.live-preview-img');
    setupImagePreview('id_avatar', '.field-avatar', '.live-preview-img');
});