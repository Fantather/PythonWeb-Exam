document.addEventListener('DOMContentLoaded', function() {
    var sidenavElems = document.querySelectorAll('.sidenav');
    M.Sidenav.init(sidenavElems, {});

    console.log('Sidenav initialized');
    
    var desktopToggle = document.getElementById('desktop-toggle');
    
    if (desktopToggle) {
        var toggleIcon = desktopToggle.querySelector('i');
        
        desktopToggle.addEventListener('click', function(e) {

            e.preventDefault(); 
            
            document.body.classList.toggle('sidebar-collapsed');
            

            if (document.body.classList.contains('sidebar-collapsed')) {
                toggleIcon.textContent = 'menu'; 
            } else {
                toggleIcon.textContent = 'menu_open';
            }
        });
    }
});