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
function getLanguagePrefix() {
    const path = window.location.pathname;
    const languageCode = path.split('/')[1]; // Obtiene el segmento de idioma del path
    return languageCode;
}

// Function to send the user's message and receive the response.
function sendMessage() {
    console.log("Función sendMessage invocada");
    const message = document.getElementById("userMessage").value.trim();  // Obtiene el mensaje y elimina espacios en blanco
    let formData = new FormData();
    formData.append("phase", "user_message");
    if (message !== "") {
        formData.append("message", message);
    }
    const fileInput = document.getElementById("fileInput");
    let hasFiles = fileInput && fileInput.files.length > 0;
    if (hasFiles) {
        const files = fileInput.files;
        for (let i = 0; i < files.length; i++) {
            formData.append("uploaded_files", files[i]);
        }
    }
    if (message !== "" || hasFiles) {
        toggleDotsAnimation(true); // Activar animaciones
        const csrfToken = getCookie('csrftoken');
        const languagePrefix = getLanguagePrefix();
        let urlEndpoint = `/${languagePrefix}/ai-team/chat/${currentContext}/`;
        fetch(urlEndpoint, {
            method: "POST",
            body: formData,
            headers: {
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
            if (fileInput) {
                fileInput.value = "";
            }
            chatBox.scrollTop = chatBox.scrollHeight;
            toggleDotsAnimation(false); // Desactivar animaciones
            
            chatBox.scrollTop = chatBox.scrollHeight;
            // Solo realiza la solicitud a la IA si hay un mensaje
            if (message !== "") {
                let urlEndpoint = `/${languagePrefix}/ai-team/chat/${currentContext}/`;
                return fetch(urlEndpoint, {
                    method: "POST",
                    body: new URLSearchParams({ "message": message, "phase": "ai_response" }),
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded",
                        "X-CSRFToken": csrfToken
                    }
                });
            } else {
                // No hay mensaje para enviar a la IA, así que resuelve la promesa aquí
                return Promise.resolve();
            }
        })
        .then(response => {
            if (response) {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            } else {
                // No hubo respuesta porque no se realizó la solicitud a la IA
                return {};
            }
        })
        .then(data => {
            if (data.ia_message_div) {
                const chatBox = document.getElementById("chatBox");
                chatBox.insertAdjacentHTML('beforeend', data.ia_message_div);
                chatBox.scrollTop = chatBox.scrollHeight;
            }
            if (data.total_cost !== undefined) {
                const totalCostDisplay = document.getElementById("totalCostDisplay");
                totalCostDisplay.textContent = "Costo Total: $" + data.total_cost;
            }
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
        //console.log("Tecla presionada", event.keyCode);
        event.preventDefault();  // Prevents the Enter action from triggering a page reload.
    }
}

//handle default messages
document.addEventListener("DOMContentLoaded", function() {
    var templateLinks = document.querySelectorAll("[data-template]");

    templateLinks.forEach(function(link) {
        link.addEventListener("click", function(e) {
            e.preventDefault();
            var templateName = e.target.getAttribute("data-template");

            toggleDotsAnimation(true);
            const csrfToken = getCookie('csrftoken');
            const languagePrefix = getLanguagePrefix();
            

            let urlEndpoint = `/${languagePrefix}/ai-team/chat/${currentContext}/`;

            fetch(urlEndpoint, {
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
                const chatBox = document.getElementById("chatBox");
                chatBox.insertAdjacentHTML('beforeend', data.template_message_div);
                chatBox.scrollTop = chatBox.scrollHeight;
            })
            .catch(error => {
                console.error('Error:', error);
            })
            .finally(() => {
                toggleDotsAnimation(false);
            });
        });
    });
});

document.addEventListener("DOMContentLoaded", function() {
    const cancelSubscriptionForm = document.getElementById('cancel-subscription-form');
    const chatBox = document.getElementById("chatBox");
    
    if (cancelSubscriptionForm) {
        cancelSubscriptionForm.addEventListener('submit', function(e) {
            e.preventDefault();  // Evita la recarga de la página

            toggleDotsAnimation(true);
            const csrfToken = getCookie('csrftoken');
            const languagePrefix = getLanguagePrefix();
            let urlEndpoint = `/${languagePrefix}/ai-team/chat/${currentContext}/`;

            // Envía los datos del formulario al servidor
            fetch(urlEndpoint, {
                method: "POST",
                body: new URLSearchParams(new FormData(cancelSubscriptionForm)),
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
                chatBox.insertAdjacentHTML('beforeend', data.template_message_div);
                chatBox.scrollTop = chatBox.scrollHeight;
            })
            .catch(error => {
                console.error('Error:', error);
            })
            .finally(() => {
                toggleDotsAnimation(false);
            });
        });
    }
});

// Initialize event listeners.
//document.getElementById("userMessage").addEventListener("input", checkAndAutocomplete);

document.addEventListener("DOMContentLoaded", function() {

    // Toggle hamburger menu.
    const hamburgerToggle = document.querySelector("#hamburgerToggle");
    const menuItems = document.querySelector(".menu-items");

    hamburgerToggle.addEventListener("change", function() {
        menuItems.style.transform = this.checked ? 'translateX(0)' : 'translateX(-100%)';
    });
});