// Function to copy the AI response to the clipboard// Function to copy the AI response to the clipboard
function copyToClipboard(event) {
    const button = event.target.closest('button');
    let messageContent = '';

    // Check if the button is inside a message-left div
    const messageLeftDiv = button.closest('.message-left');
    if (messageLeftDiv) {
        messageContent = messageLeftDiv.querySelector('.message-content').textContent;
    } else {
        // Otherwise, assume it's inside a card div
        const cardDiv = button.closest('.card');
        if (cardDiv) {
            const messageElements = cardDiv.querySelectorAll('.card-content .message-content');
            messageElements.forEach(element => {
                messageContent += element.textContent + ' ';
            });
        }
    }

    if (messageContent) {
        navigator.clipboard.writeText(messageContent.trim()).then(() => {
            console.log('Text copied to clipboard');
        }).catch(err => {
            console.error('Error copying text: ', err);
        });
    }
}
// Function to handle "Me gusta" button click
function handleLike(event) {
    handleInteraction(event, 'like');
}

// Function to handle "No me gusta" button click
function handleDislike(event) {
    handleInteraction(event, 'dislike');
}

// Common function to handle both "Me gusta" and "No me gusta" button clicks
function handleInteraction(event, action) {
    const url = window.location.href;
    const button = event.target.closest('button');
    let messageContent = '';

    // Check if the button is inside a message-left div
    const messageLeftDiv = button.closest('.message-left');
    if (messageLeftDiv) {
        messageContent = messageLeftDiv.querySelector('.message-content').textContent;
    } else {
        // Otherwise, assume it's inside a card div
        const cardDiv = button.closest('.card');
        if (cardDiv) {
            const messageElements = cardDiv.querySelectorAll('.card-content .message-content');
            messageElements.forEach(element => {
                messageContent += element.textContent + ' ';
            });
        }
    }

    if (messageContent) {
        const languagePrefix = getLanguagePrefix();
        const csrfToken = getCookie('csrftoken');
        const urlEndpoint = `/${languagePrefix}/interaction-user-messages/`;

        fetch(urlEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken // Assuming you have a function to get the CSRF token
            },
            body: JSON.stringify({ message: messageContent.trim(), action: action, url: url })
        }).then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        }).then(data => {
            if (data.not_authenticated) {
                // Assuming Django returns HTML content in data.html when the user is not authenticated
                const chatBox = document.getElementById("chatBox");
                chatBox.insertAdjacentHTML('beforeend', data.html);
                chatBox.scrollTop = chatBox.scrollHeight;
            } else {
                console.log(`${action} response:`, data);
            }
        }).catch(error => {
            console.error('Error:', error);
        });
    }
}

function convertTextToAudio(button) {
    // Obtener el texto del mensaje
    const messageContent = button.closest('.card').querySelector('.message-content').innerText;
    const language =  getLanguagePrefix();
    const csrfToken = getCookie('csrftoken');
    const urlEndpoint = `/${language}/upload_text/`;
    // Hacer fetch al endpoint 'upload_text'
    fetch(urlEndpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken // Asegúrate de incluir el token CSRF si estás usando Django
        },
        body: JSON.stringify({ text: messageContent, language: language })
    })
    .then(response => response.json())
    .then(data => {
        if (data.audio_url) {
            // Crear un elemento de audio y reproducir el archivo MP3
            const audio = new Audio(data.audio_url);
            audio.play();
        } else {
            console.error('Error al generar el audio:', data.error);
        }
    })
    .catch(error => {
        console.error('Error en la solicitud:', error);
    });
}

// Add event listeners to the buttons
document.addEventListener('click', function(event) {
    if (event.target.closest('.bi-clipboard')) {
        copyToClipboard(event);
    } else if (event.target.closest('.bi-hand-thumbs-up')) {
        handleLike(event);
    } else if (event.target.closest('.bi-hand-thumbs-down')) {
        handleDislike(event);
    }
});
