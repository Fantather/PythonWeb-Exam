document.addEventListener("DOMContentLoaded", function() {
    const avatarInput = document.getElementById('id_avatar');
    
    const previewContainer = document.querySelector('.field-avatar_preview');

    if (avatarInput && previewContainer) {
        avatarInput.addEventListener('change', function(event) {
            const file = event.target.files[0];
            
            if (file) {
                let imgElement = previewContainer.querySelector('img');
                
                if (!imgElement) {
                    imgElement = document.createElement('img');
                    
                    imgElement.style.maxWidth = '150px'; 
                    imgElement.style.height = '150px';
                    imgElement.style.objectFit = 'cover'; 
                    imgElement.style.marginTop = '15px';
                    imgElement.style.borderRadius = '50%'; 
                    
                    previewContainer.appendChild(imgElement);
                }
                
                imgElement.src = URL.createObjectURL(file);
                
                imgElement.onload = function() {
                    URL.revokeObjectURL(imgElement.src);
                }
            }
        });
    }
});