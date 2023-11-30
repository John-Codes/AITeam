document.addEventListener('DOMContentLoaded', function() {
    const inputs = document.querySelectorAll('.form-control');
  
    inputs.forEach(input => {
      handleInputBackground(input);
  
      input.addEventListener('input', function() {
        handleInputBackground(input);
      });
    });
  
    function handleInputBackground(input) {
      if (input.value) {
        input.classList.add('input-filled');
      } else {
        input.classList.remove('input-filled');
      }
    }
  });

  // Initialize event listeners.
document.addEventListener("DOMContentLoaded", function() {
    // Toggle hamburger menu.
    const hamburgerToggle = document.querySelector("#hamburgerToggle");
    const menuItems = document.querySelector(".menu-items");
    const hamburgerIcon = document.querySelector(".hamburger-lines i");
    console.log('aquii esta')
    hamburgerToggle.addEventListener("change", function() {

      hamburgerIcon.className = this.checked ? 'bi bi-x-lg' : 'bi bi-list';

      menuItems.style.transform = this.checked ? 'translateX(0)' : 'translateX(-100%)';
    });
});
