// Function to toggle the animation of dots.

const urlDictionary = {
    'main': 'main-query-temp-rag',
    'subscription': 'stream-chat',
    'panel-admin': 'main-query-perm-rag'
};
var list_messages = [];
function toggleDotsAnimation(shouldShow) {
    const loadingDots = document.querySelector('.loading-dots-container');
    const metallicText = document.querySelector('.metallic-text');
    const chatBox = document.getElementById('chatBox');
    const displayValue = shouldShow ? 'flex' : 'none';
    if (shouldShow) {
        // Disminuye la altura en 30px
        chatBox.style.height = `calc(${chatBox.style.height} - 100)`;
    } else {
        // Restaura la altura original (asumiendo que la altura original es 100vh - 160px)
        chatBox.style.height = 'calc(100vh - 160px)';
    }
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


// Function async to streaming chat responses.
async function sendMessageStream() {
    const csrfToken = getCookie('csrftoken');
    const message = document.getElementById("userMessage").value;
    const chatBox = document.getElementById("chatBox");
    const languagePrefix = getLanguagePrefix();
    const urlEndpoint = `/${languagePrefix}/chat/${currentContext}/`;

    //const async_chat = `/${languagePrefix}/${urlDictionary[currentContext]}/`;


    chatBox.insertAdjacentHTML('beforeend', `
        <div class="message-right glass float-end">
            <p class="message-content">${message}</p>
        </div>
        <div class="clearfix"></div>
    `);
    toggleDotsAnimation(true); // Activar animaciones
    document.getElementById("userMessage").value = "";
    const aiMessageId = 'aiMessage' + Date.now(); // Generar un ID único para el elemento
    list_messages.push({"role": "user", "content": message});
    var response = await fetch(urlEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 'list_messages': list_messages, 'current_chat':currentContext, 'action': 'call-stream-ia' })
            });
    
    var reader = response.body.getReader();
    var decoder = new TextDecoder('utf-8');
    toggleDotsAnimation(false); // Activar animaciones
    chatBox.insertAdjacentHTML('beforeend', `
        <div class="message-left glass">
            <p class="message-content" id="${aiMessageId}"> </p>
            <div class="mt-2">
                <button class="btn btn-light btn-sm me-2" title="Copiar"><i class="bi bi-clipboard"></i></button>
                <button class="btn btn-light btn-sm me-2" title="Me gusta"><i class="bi bi-hand-thumbs-up"></i></button>
                <button class="btn btn-light btn-sm" title="No me gusta"><i class="bi bi-hand-thumbs-down"></i></button>
            </div>
        </div>
        <div class="clearfix"></div>
    `);
    let aiMessage = '';

    reader.read().then(function processResult(result) {
        if (result.done) {
            // Add AI message to history after the entire response is received
            list_messages.push({"role": "assistant", "content": aiMessage});
            return;
        }
        let token = decoder.decode(result.value);
        aiMessage += token;
        if (token.endsWith(':') || token.endsWith('!') || token.endsWith('?')) {
            document.getElementById(aiMessageId).innerHTML += token + "<br>";
            chatBox.scrollTop = chatBox.scrollHeight;
        } else {
            document.getElementById(aiMessageId).innerHTML += token;
            chatBox.scrollTop = chatBox.scrollHeight;
        }
        return reader.read().then(processResult);
    });
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
        sendMessageStream();
        //console.log("Tecla presionada", event.keyCode);
        event.preventDefault();  // Prevents the Enter action from triggering a page reload.
    }
}

function uploadFile(event) {
    toggleDotsAnimation(true);
    const file = event.target.files[0]; // Obtener el primer archivo seleccionado
    const formData = new FormData();
    
    // Agregar el archivo al FormData si está presente
    if (file) {
        formData.append("uploaded_files", file);
        formData.append("context_value", currentContext); // Asumiendo que currentContext está definido globalmente
        //if currentContext == main: action == create-rag
        if (currentContext == "main") {
            formData.append("action", "create-temp-rag");
        } else if (currentContext == "panel-admin") {
            formData.append("action", "create-perm-rag");
        }
        

        // Realizar la solicitud para procesar el archivo
        const csrfToken = getCookie('csrftoken');
        const languagePrefix = getLanguagePrefix();
        let urlEndpoint = `/${languagePrefix}/chat/${currentContext}/`;
        
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
            if (data.message) {
                chatBox.insertAdjacentHTML('beforeend', data.message);
            } else  if (data.error) {
                chatBox.insertAdjacentHTML('beforeend', `
                    <div class="message-left glass">
                        <p class="message-content">File upload failed.</p>
                        <div class="mt-2">
                            <button class="btn btn-light btn-sm me-2" title="Copiar"><i class="bi bi-clipboard"></i></button>
                            <button class="btn btn-light btn-sm me-2" title="Me gusta"><i class="bi bi-hand-thumbs-up"></i></button>
                            <button class="btn btn-light btn-sm" title="No me gusta"><i class="bi bi-hand-thumbs-down"></i></button>
                        </div>
                    </div>
                    <div class="clearfix"></div>
                `);
            }
            chatBox.scrollTop = chatBox.scrollHeight; 
            list_messages = [];
        })
        .catch(error => {
            console.error('Error:', error);
        })
        .finally(() => {
            toggleDotsAnimation(false); // Desactivar animaciones
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
            

            let urlEndpoint = `/${languagePrefix}/static-messages/`;

            fetch(urlEndpoint, {
                method: "POST",
                body: JSON.stringify({ "template_name": templateName }),
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie('csrftoken') 
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
                console.log(data);
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