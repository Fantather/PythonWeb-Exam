document.addEventListener('DOMContentLoaded', function() {
    // 1. Инициализация всех Dropdown меню на странице
    var dropdowns = document.querySelectorAll('.dropdown-trigger');
    M.Dropdown.init(dropdowns, {
        alignment: 'right', // Меню будет открываться влево от кнопки
        constrainWidth: false,
        coverTrigger: false // Меню появится ПОД кнопкой, а не перекроет ее
    });

    // Универсальный скрипт удаления (для постов, топиков, сообществ)
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const deleteButtons = document.querySelectorAll('.ajax-delete-btn');

    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            if (!confirm('Вы уверены, что хотите удалить этот элемент? Действие необратимо.')) {
                return; 
            }

            // Достаем URL для удаления прямо из атрибута кнопки
            const url = this.dataset.deleteUrl;
            const targetId = this.dataset.targetId; // Например: 'post-5' или 'topic-12'

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            })
            .then(response => {
                if (!response.ok) throw new Error('Ошибка удаления');
                return response.json();
            })
            .then(data => {
                if (data.status === 'success') {
                    
                    // Если есть ссылка для редиректа - переходим
                    if (data.redirect_url) {
                        window.location.href = data.redirect_url;
                        return;
                    }
                    
                    // Иначе просто удаляем коммент
                    const elementToRemove = document.getElementById(targetId);
                    if (elementToRemove) {
                        elementToRemove.style.transition = "opacity 0.3s ease";
                        elementToRemove.style.opacity = "0";
                        setTimeout(() => elementToRemove.remove(), 300);
                    }
                }
            })
            .catch(error => M.toast({html: 'Ошибка при удалении'}));
        });
    });
});