document.addEventListener('DOMContentLoaded', function() {
    if (typeof M !== 'undefined') {
        M.updateTextFields();
        var selects = document.querySelectorAll('select');
        M.FormSelect.init(selects);
    }
});
