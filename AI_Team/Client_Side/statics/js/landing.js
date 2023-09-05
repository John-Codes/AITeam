
// Variables related to the UI
let isDotsVisible = false;

function toggleDotsAnimation(shouldShow) {
    const loadingDots = document.querySelector('.loading-dots-container');
    const metallicText = document.querySelector('.metallic-text');

    if (shouldShow && !isDotsVisible) {
        loadingDots.style.display = 'inline-flex';
        metallicText.style.display = 'flex';
        isDotsVisible = true;
    } else if (!shouldShow && isDotsVisible) {
        loadingDots.style.display = 'none';
        metallicText.style.display = 'none';
        isDotsVisible = false;
    }
}

function sendMessage() {
    let message = document.getElementById("userMessage").value; // Corregido el ID
    if(message.trim() !== "") {
        toggleDotsAnimation(true);

        let csrfToken = getCookie('csrftoken'); // Obtiene el token CSRF

        fetch("/aiteam/", {
            method: "POST",
            body: new URLSearchParams({ "message": message }),
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": csrfToken // Envía el token CSRF
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log(`Usuario: ${message}`);
            console.log(`IA: ${data.ai_response}`);
            toggleDotsAnimation(false);
        })
        .catch(error => {
            console.error('Error:', error);
            toggleDotsAnimation(false);
        });

        document.getElementById("userMessage").value = ""; // Corregido el ID
    }
}



function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function handleKeyDown(event) {
    if (event.keyCode === 13) {  // 13 es el keyCode para la tecla Enter
        sendMessage();
        event.preventDefault();  // Evita que se realice la acción por defecto del Enter
    }
}

// Event listeners
const sendButton = document.querySelector('.btn-send');
sendButton.addEventListener('click', sendMessage);

const hamburgerToggle = document.getElementById('hamburgerToggle');
const menuItems = document.querySelector('.menu-items');

hamburgerToggle.addEventListener('change', () => {
    if (hamburgerToggle.checked) {
        menuItems.style.transform = 'translateX(0)';
    } else {
        menuItems.style.transform = 'translateX(-100%)';
    }
});

