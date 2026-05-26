document.addEventListener("DOMContentLoaded", function() {
    const iconInput = document.getElementById('id_icon');
    
    // Ищем контейнер-обертку всего поля icon
    const fieldContainer = document.querySelector('.field-icon');
    
    if (iconInput && fieldContainer) {
        iconInput.addEventListener('change', function(event) {
            const file = event.target.files[0];
            
            if (file) {
                let imgElement = fieldContainer.querySelector('.live-preview-img');
                
                // Если тега нет, создаем его
                if (!imgElement) {
                    imgElement = document.createElement('img');
                    imgElement.className = 'live-preview-img';
                    
                    imgElement.style.maxWidth = '100px'; 
                    imgElement.style.maxHeight = '100px';
                    imgElement.style.display = 'block';
                    imgElement.style.marginTop = '10px';
                    
                    iconInput.parentNode.appendChild(imgElement);
                }
                
                imgElement.src = URL.createObjectURL(file);
                
                imgElement.onload = function() {
                    URL.revokeObjectURL(imgElement.src);
                }
            }
        });
    }
});