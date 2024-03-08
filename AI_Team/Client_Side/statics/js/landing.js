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
    const message = document.getElementById("userMessage").value.trim();
    let formData = new FormData();
    
    // Agregar el mensaje del usuario al FormData si está presente
    if (message !== "") {
        formData.append("message", message);
        // Agregar el mensaje del usuario al chatBox directamente
        const chatBox = document.getElementById("chatBox");
        const userMessageDiv = `<div class="message-right glass float-end"><p class="message-content">${message}</p></div><div class="clearfix"></div>`;
        chatBox.insertAdjacentHTML('beforeend', userMessageDiv);
        document.getElementById("userMessage").value = "";
    }

    // Agregar archivos al FormData si están presentes
    // const fileInput = document.getElementById("fileInput");
    // let hasFiles = fileInput && fileInput.files.length > 0;
    // if (hasFiles) {
    //     const files = fileInput.files;
    //     for (let i = 0; i < files.length; i++) {
    //         formData.append("uploaded_files", files[i]);
    //     }
    // }

    // Solo realiza la solicitud si hay un mensaje o archivos
    if (message !== "" || hasFiles) {
        toggleDotsAnimation(true); // Activar animaciones
        const csrfToken = getCookie('csrftoken');
        const languagePrefix = getLanguagePrefix();
        let urlEndpoint = `/${languagePrefix}/chat/${currentContext}/`;
        formData.append("phase", "ai_response"); // Añadir phase para la solicitud

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
            if (data.combined_response) {
                chatBox.insertAdjacentHTML('beforeend', data.combined_response);
            }
            if (fileInput) {
                fileInput.value = ""; // Limpiar el botón de archivos
            }
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
        //console.log("Tecla presionada", event.keyCode);
        event.preventDefault();  // Prevents the Enter action from triggering a page reload.
    }
}

// Función para cargar un solo archivo
function uploadFile(event) {
    const file = event.target.files[0]; // Obtener el primer archivo seleccionado
    const formData = new FormData();
    
    // Agregar el archivo al FormData si está presente
    if (file) {
        formData.append("uploaded_files", file);
        // Realizar la solicitud para procesar el archivo
        const csrfToken = getCookie('csrftoken');
        const languagePrefix = getLanguagePrefix();
        let urlEndpoint = `/${languagePrefix}/chat/${currentContext}/`;
        console.log(urlEndpoint);
        
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
            // Realizar acciones adicionales después de cargar el archivo
            console.log('File uploaded successfully:', data);
            const chatBox = document.getElementById("chatBox");
            if (data.combined_response) {
                chatBox.insertAdjacentHTML('beforeend', data.combined_response);
            }
            chatBox.scrollTop = chatBox.scrollHeight;
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
}
//handle default messages
document.addEventListener("DOMContentLoaded", function() {
    var templateLinks = document.querySelectorAll("[data-template]");

    templateLinks.forEach(function(link) {
        link.addEventListener("click", function(e) {
            e.preventDefault();
            var templateName = e.target.getAttribute("data-template");
            console.log(templateName);
            toggleDotsAnimation(true);
            const csrfToken = getCookie('csrftoken');
            const languagePrefix = getLanguagePrefix();
            

            let urlEndpoint = `/${languagePrefix}/chat/${currentContext}/`;

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
                chatBox.insertAdjacentHTML('beforeend', data.combined_response);
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
            let urlEndpoint = `/${languagePrefix}/chat/${currentContext}/`;

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
                chatBox.insertAdjacentHTML('beforeend', data.combined_response);
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
    const hamburgerIcon = document.querySelector(".hamburger-lines i");

    hamburgerToggle.addEventListener("change", function() {

      hamburgerIcon.className = this.checked ? 'bi bi-x-lg' : 'bi bi-list';

        menuItems.style.transform = this.checked ? 'translateX(0)' : 'translateX(-100%)';
    });
});