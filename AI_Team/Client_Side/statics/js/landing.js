function toggleDotsAnimation(shouldShow) {
    const loadingDots = document.querySelector('.loading-dots-container');
    const metallicText = document.querySelector('.metallic-text');
    const displayValue = shouldShow ? 'flex' : 'none';

    loadingDots.style.display = displayValue;
    metallicText.style.display = displayValue;
}

function sendMessage() {
    let message = document.getElementById("userMessage").value;

    if(message.trim() !== "") {
        toggleDotsAnimation(true);

        let csrfToken = getCookie('csrftoken'); 

        fetch("/aiteam/", {
            method: "POST",
            body: new URLSearchParams({ "message": message }),
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
            console.log(`Usuario: ${message}`);
            console.log(`IA: ${data.ai_response}`);
            toggleDotsAnimation(false);
        })
        .catch(error => {
            console.error('Error:', error);
            toggleDotsAnimation(false);
        });

        document.getElementById("userMessage").value = "";
    }
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

// Send message
function handleKeyDown(event) {
    if (event.keyCode === 13) {  // 13 es el keyCode para la tecla Enter
        sendMessage();
        event.preventDefault();  // Evita que se realice la acción por defecto del Enter
    }
}

//Event listeners for send messages
const sendButton = document.querySelector('.btn-send');
sendButton.addEventListener('click', sendMessage);

const userMessageInput = document.getElementById('userMessage');
sendButton.addEventListener('keydown', handleKeyDown);


document.addEventListener("DOMContentLoaded", function() {
    // Hamburger toggle
    const hamburgerToggle = document.querySelector("#hamburgerToggle");
    const menuItems = document.querySelector(".menu-items");

    hamburgerToggle.addEventListener("change", function() {
        if (this.checked) {
            menuItems.style.transform = 'translateX(0)';
        } else {
            menuItems.style.transform = 'translateX(-100%)';
        }
    });
});