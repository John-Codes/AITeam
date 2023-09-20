// Function to toggle the animation of dots.
function toggleDotsAnimation(shouldShow) {
    const loadingDots = document.querySelector('.loading-dots-container');
    const metallicText = document.querySelector('.metallic-text');
    const displayValue = shouldShow ? 'flex' : 'none';

    loadingDots.style.display = displayValue;
    metallicText.style.display = displayValue;
}

// Helper function to retrieve a cookie value by name.
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

// Function to send the user's message and receive the response.
function sendMessage() {
    console.log("Función sendMessage invocada");
    const message = document.getElementById("userMessage").value.trim();  // Obtiene el mensaje y elimina espacios en blanco

    // Luego, verifica si el mensaje es idéntico al anterior.
    if (message.trim() !== "") {

        toggleDotsAnimation(true); // Activar animaciones
        const csrfToken = getCookie('csrftoken');
        console.log("Enviando solicitud 'user_message'...");

        fetch("/aiteam/", {
            method: "POST",
            body: new URLSearchParams({ "message": message, "phase": "user_message" }),
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": csrfToken
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const chatBox = document.getElementById("chatBox");
            chatBox.insertAdjacentHTML('beforeend', data.user_message_div);
            document.getElementById("userMessage").value = "";
            console.log("Enviando solicitud 'ai_response'...");
            chatBox.scrollTop = chatBox.scrollHeight;
            // Now make a request for the AI's response here, inside the .then()
            return fetch("/aiteam/", {
                method: "POST",
                body: new URLSearchParams({ "message": message, "phase": "ai_response" }),
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-CSRFToken": csrfToken
                }
            });
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const chatBox = document.getElementById("chatBox");
            chatBox.insertAdjacentHTML('beforeend', data.ia_message_div);
            chatBox.scrollTop = chatBox.scrollHeight;
        })
        .catch(error => {
            console.error('Error:', error);
        })
        .finally(() => {
            toggleDotsAnimation(false); // Desactivar animaciones
        });
    }
}

// Handle Enter key press to send the message.
function handleKeyDown(event) {
    if (event.keyCode === 13) {  // 13 is the keyCode for Enter key.
        sendMessage();
        console.log("Tecla presionada", event.keyCode);
        event.preventDefault();  // Prevents the Enter action from triggering a page reload.
    }
}

function checkAndAutocomplete() {
    const message = document.getElementById("userMessage");
    const value = message.value;

    // Si el primer carácter es "@" y no contiene "@myemail" al principio
    if (value.charAt(0) === "@" && !value.startsWith("@myemail")) {
        message.value = "@myemail: (replace these parenteses with your email)" + value.slice(1); // Eliminamos el "@" inicial para evitar duplicados
    }
}

document.addEventListener("DOMContentLoaded", function() {
    var templateLinks = document.querySelectorAll("[data-template]");

    templateLinks.forEach(function(link) {
        link.addEventListener("click", function(e) {
            e.preventDefault();
            var templateName = e.target.getAttribute("data-template");

            toggleDotsAnimation(true); // Activar animaciones
            const csrfToken = getCookie('csrftoken');
            console.log("Enviando solicitud del template...");

            fetch("/aiteam/", {
                method: "POST",
                body: new URLSearchParams({ "template_name": templateName }),
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-CSRFToken": csrfToken
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log('this is the data response ai', data.template_message_div)
                const chatBox = document.getElementById("chatBox");
                chatBox.insertAdjacentHTML('beforeend', data.template_message_div);
                chatBox.scrollTop = chatBox.scrollHeight;
            })
            .catch(error => {
                console.error('Error:', error);
            })
            .finally(() => {
                toggleDotsAnimation(false); // Desactivar animaciones
            });
        });
    });
});



// Initialize event listeners.
document.getElementById("userMessage").addEventListener("input", checkAndAutocomplete);

document.addEventListener("DOMContentLoaded", function() {
    console.log("DOMContentLoaded ejecutado");

    // Toggle hamburger menu.
    const hamburgerToggle = document.querySelector("#hamburgerToggle");
    const menuItems = document.querySelector(".menu-items");

    hamburgerToggle.addEventListener("change", function() {
        menuItems.style.transform = this.checked ? 'translateX(0)' : 'translateX(-100%)';
    });
});
