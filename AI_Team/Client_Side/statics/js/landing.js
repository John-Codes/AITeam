
const urlDictionary = {
    'main': 'main-query-temp-rag',
    'subscription': 'stream-chat',
    'panel-admin': 'main-query-perm-rag'
};
var list_messages = [];
function toggleDotsAnimation(shouldShow) {
    const loadingDots = document.querySelector('.loading-dots-container');
    const body = document.body;
    const metallicText = document.querySelector('.metallic-text');
    const chatBox = document.getElementById('chatBox');
    const chatContainer = document.querySelector('.chat-content');

    const displayValue = shouldShow ? 'flex' : 'none';
    console.log('toggleDotsAnimation called, shouldShow:', shouldShow, 'displayValue:', displayValue);
    if (shouldShow) {
        // Disminuye la altura en 30px
        chatBox.style.height = `calc(${chatBox.style.height} - 100)`;
    } else {
        chatBox.style.height = 'calc(80px + 100vh);';
    }
    loadingDots.style.display = displayValue;
    document.body.scrollTo({
        top: document.body.scrollHeight,
        behavior: 'smooth' // Desplazamiento suave
    });
    //metallicText.style.display = displayValue;
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

    // Verificar si estamos esperando el correo del usuario
    if (sessionStorage.getItem('awaitingContactEmail') === 'true') {
        // Enviar el correo a un nuevo endpoint
        document.getElementById("userMessage").value = "";
        const emailEndpoint = `/${languagePrefix}/send-contact-email/`;
        const response = await fetch(emailEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ 'email': message })
        });
        const responseData = await response.json();
        if (response.ok) {
            // Limpiar la marca de la sesión
            sessionStorage.removeItem('awaitingContactEmail');
        }
        chatBox.insertAdjacentHTML('beforeend', responseData.message);
        document.body.scrollTo({
            top: document.body.scrollHeight,
            behavior: 'smooth' // Desplazamiento suave
        });
        // chatBox.scrollTop = chatBox.scrollHeight;
        return;
    }

    chatBox.insertAdjacentHTML('beforeend', `
        <div class="message-right glass float-end">
            <p class="message-content">${message}</p>
        </div>
        <div class="clearfix"></div>
    `);
    // chatBox.scrollTop = chatBox.scrollHeight;
    document.body.scrollTo({
        top: document.body.scrollHeight,
        behavior: 'smooth' // Desplazamiento suave
    });
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
        <div class="card card_background_static"  >
            
            <div class="card-content card-stream"  >
            
                <p class="message-content" id="${aiMessageId}" style="padding: rem !important;"  > </p>
            
            </div>
                    <footer class="card-footer" style="border-top: none; background-color: transparent;" >
                        <div style="display: flex; align-items: center;">
                            <button class="is-small no-border no-outline" style="margin-left: 1rem;" title="Copiar"> 
                                    <span class="icon is-small">
                                        <i class="fas fa-clipboard"></i>
                                </span>
                            </button>
                            <button class=" is-small no-border no-outline"  style="margin-left: 1rem;" title="Me gusta"> 
                                <span class="icon is-small">    
                                    <i class="fas fa-thumbs-up"></i>
                                    
                                </span>
                            </button>
                            <button class=" is-small no-border no-outline"  style="margin-left: 1rem;" title="No me gusta"> 
                                <span class="icon is-small">    
                                    
                                    <i class="fas fa-thumbs-down"></i>
                                </span>
                            </button>
                        </div>
                    </footer>
        </div>
        
    `);
    document.body.scrollTo({
        top: document.body.scrollHeight,
        behavior: 'smooth' // Desplazamiento suave
    });
    let aiMessage = '';

    reader.read().then(function processResult(result) {
        if (result.done) {
            // Add AI message to history after the entire response is received
            list_messages.push({"role": "assistant", "content": aiMessage});
            return;
        }
        let token = decoder.decode(result.value);
        aiMessage += token;
         let htmlContent = marked.parse(aiMessage);
         htmlContent = addCustomClasses(htmlContent);
        document.getElementById(aiMessageId).innerHTML = htmlContent;
        // chatBox.scrollTop = chatBox.scrollHeight;
        document.body.scrollTo({
            top: document.body.scrollHeight,
            behavior: 'smooth' // Desplazamiento suave
        });
        return reader.read().then(processResult);
    });
}

function addCustomClasses(htmlContent) {
    // Create a temporary DOM element to manipulate the HTML
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = htmlContent;

    // Add classes to <li> elements
    const listItems = tempDiv.querySelectorAll('li');
    listItems.forEach(li => {
        li.classList.add('message-content', 'bullet-point');
    });

    // Add classes to <h*> elements
    for (let i = 1; i <= 6; i++) {
        const headers = tempDiv.querySelectorAll(`h${i}`);
        headers.forEach(header => {
            header.classList.add('subtitle');
            if (i <= 3) {
                header.classList.add('is-3');
            } else {
                header.classList.add('is-4');
            }
        });
    }

    
    const strongElements = tempDiv.querySelectorAll('strong');
    strongElements.forEach(strong => {
        // Check if the <strong> is not part of any list (neither <ol> nor <ul>)
        const isPartOfAnyList = strong.closest('ol') !== null || strong.closest('ul') !== null;
        
        // Insert <br> before and after <strong> elements that are not part of any list
        if (!isPartOfAnyList) {
            const brBefore = document.createElement('br');
            const brAfter = document.createElement('br');
            strong.insertAdjacentElement('beforebegin', brBefore);
            strong.insertAdjacentElement('afterend', brAfter);
        }
    });
    return tempDiv.innerHTML;
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
                        <footer class="card-footer" style="border-top: none; background-color: transparent;" >
                        <div style="display: flex; align-items: center;">
                            <button class="is-small no-border no-outline" style="margin-left: 1rem;" title="Copiar"> 
                                    <span class="icon is-small">
                                        <i class="fas fa-clipboard"></i>
                                </span>
                            </button>
                            <button class=" is-small no-border no-outline"  style="margin-left: 1rem;" title="Me gusta"> 
                                <span class="icon is-small">    
                                    <i class="fas fa-thumbs-up"></i>
                                    
                                </span>
                            </button>
                            <button class=" is-small no-border no-outline"  style="margin-left: 1rem;" title="No me gusta"> 
                                <span class="icon is-small">    
                                    
                                    <i class="fas fa-thumbs-down"></i>
                                </span>
                            </button>
                        </div>
                    </footer>
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
            // get an element byid chatBox in a const named messages_div
            const messages_div = document.getElementById("chatBox");
            const csrfToken = getCookie('csrftoken');
            const languagePrefix = getLanguagePrefix();
            
            let urlEndpoint = `/${languagePrefix}/static-messages/`;

            fetch(urlEndpoint, {
                method: "POST",
                body: JSON.stringify({ "template_name": templateName }),
                headers: {
                    "Content-Type": "application/json",
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
                //insert the template html in the buttom of the messages_div          
                messages_div.insertAdjacentHTML('beforeend', data.html);
                messages_div.scrollTop = messages_div.scrollHeight;
                // Si el template es "contact_us", marcar que estamos esperando el correo del usuario
                if (templateName === "contact_us") {
                    sessionStorage.setItem('awaitingContactEmail', 'true');
                }
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

document.addEventListener('DOMContentLoaded', () => {
    // Función para abrir el modal
    const openModal = () => {
      const modal = document.getElementById('modal-cancel-subscription');
      modal.style.display = 'flex';
    };
  
    // Función para cerrar el modal
    const closeModal = () => {
      const modal = document.getElementById('modal-cancel-subscription');
      modal.style.display = 'none';
    };
  
    // Evento para abrir el modal
    const modalTrigger = document.querySelector('.js-modal-trigger');
    if (modalTrigger) {
      modalTrigger.addEventListener('click', openModal);
    }
  
    // Eventos para cerrar el modal
    const closeModalButton = document.querySelector('#modal-cancel-subscription button[type="button"]');
    if (closeModalButton) {
      closeModalButton.addEventListener('click', closeModal);
    }
  
    window.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') {
        closeModal();
      }
    });
  
    // Interceptar el envío del formulario de cancelación de suscripción
    const cancelSubscriptionForm = document.getElementById('cancel-subscription-form');
    if (cancelSubscriptionForm) {
      cancelSubscriptionForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Prevenir el envío tradicional del formulario
  
        const formData = new FormData(cancelSubscriptionForm);
        const csrfToken = getCookie('csrftoken');
        const response = await fetch(cancelSubscriptionForm.action, {
          method: 'POST',
          headers: {
            'X-CSRFToken': csrfToken
          },
          body: formData
        });
  
        if (response.ok) {
          // Manejar la respuesta exitosa
          closeModal();
          // Puedes agregar lógica adicional aquí, como mostrar un mensaje de éxito
        } else {
          // Manejar errores
          console.error('Error al cancelar la suscripción');
        }
      });
    }
  });


// Initialize event listeners.
//document.getElementById("userMessage").addEventListener("input", checkAndAutocomplete);

document.addEventListener("DOMContentLoaded", function() {
    // Selección de elementos del DOM
    const hamburgerToggle = document.querySelector("#hamburgerToggle");
    const menuItems = document.querySelector(".menu-items");
    const hamburgerIcon = document.querySelector(".hamburger-lines i");

    // Función para actualizar el menú y el icono
    function updateMenu(isOpen) {
        hamburgerIcon.className = isOpen ? 'bi bi-x-lg' : 'bi bi-list';
        menuItems.style.transform = isOpen ? 'translateX(0)' : 'translateX(-100%)';
    }

    // Event listener para el toggle del menú hamburguesa
    hamburgerToggle.addEventListener("change", function() {
        updateMenu(this.checked);
    });

    // Event listener para cerrar el menú si se hace clic fuera de él
    document.addEventListener("click", function(event) {
        // Verificar si el menú está abierto
        if (hamburgerIcon.className === 'bi bi-x-lg') {
            // Comprobar si el clic fue fuera del menú y del toggle
            if (!menuItems.contains(event.target) && !event.target.closest('.hamburger-lines')) {
                hamburgerToggle.checked = false;
                updateMenu(false);
            }
        }
    });
});
