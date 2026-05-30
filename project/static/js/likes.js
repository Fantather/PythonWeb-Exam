document.addEventListener('DOMContentLoaded', function() {

    const likeButtons = document.querySelectorAll('.like-btn');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    likeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const postId = this.dataset.postId;
            const requestUrl = this.dataset.url;
            const icon = this.querySelector('.material-icons');
            const countSpan = this.querySelector('.likes-count');

            // Делаю фоновый POST-запрос к ToggleLikeView
            fetch(requestUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json'
                },
            })
            .then(response => {
                // Если сервер ответил 401 (Не авторизован)
                if (response.status === 401) {
                    // Используем всплывающее уведомление Materialize (Toast)
                    M.toast({html: 'Пожалуйста, войдите в аккаунт, чтобы ставить лайки', classes: 'red rounded'});
                    throw new Error('Unauthorized');
                }
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.status === 'success') {
                    countSpan.textContent = data.likes_count;
                    
                    // Меняем иконку в зависимости от состояния (is_liked)
                    if (data.is_liked) {
                        icon.textContent = 'favorite'; // Закрашенное сердце
                    } else {
                        icon.textContent = 'favorite_border'; // Пустое сердце
                    }
                }
            })
            .catch(error => console.error('Ошибка при лайке:', error));
        });
    });
});