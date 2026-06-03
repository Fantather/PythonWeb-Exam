document.addEventListener('DOMContentLoaded', function () {

    // 1. Инициализация вкладок
    var tabsElems = document.querySelectorAll('.tabs');
    M.Tabs.init(tabsElems);

    // 2. Авторасширение текстовых полей
    var textareas = document.querySelectorAll('.materialize-textarea');
    textareas.forEach(function (textarea) {
        M.textareaAutoResize(textarea);
    });

    
})