function toggleMenu() {
    var menu = document.querySelector('.menu-right');
    if (menu.style.display === 'block' || menu.style.display === '') {
        menu.style.display = 'none';
    } else {
        menu.style.display = 'block';
    }
}
