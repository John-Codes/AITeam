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
function addUserMessage() {
    const message = document.getElementById("userMessage").value;

    if (message.trim() !== "") {
        const csrfToken = getCookie('csrftoken');
        toggleDotsAnimation(true)
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
        })
        .catch(error => {
            console.error('Error:', error);
        });
        toggleDotsAnimation(false)
        // Clear the user input field.
        document.getElementById("userMessage").value = "";
    }
}

// Function to receive the AI's response.
function sendMessage(message) {
    //const message = document.getElementById("userMessage").value;
    const csrfToken = getCookie('csrftoken');

    fetch("/aiteam/", {
        method: "POST",
        body: new URLSearchParams({ "message": message, "phase": "ai_response" }),
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
        if (data.error) {
            console.error('Error from server:', data.error);
        } else {
            const chatBox = document.getElementById("chatBox");
            chatBox.insertAdjacentHTML('beforeend', data.ia_message_div);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });

    // Clear the user input field.
    document.getElementById("userMessage").value = "";
}

// Handle Enter key press to send the message.
function handleKeyDown(event) {
    if (event.keyCode === 13) {  // 13 is the keyCode for Enter key.
        addUserMessage();
        event.preventDefault();  // Prevents the Enter action from triggering a page reload.
    }
}

// Initialize event listeners.
document.addEventListener("DOMContentLoaded", function() {
    // Send message using the button.
    const sendButton = document.querySelector('.btn-send');
    sendButton.addEventListener('click', addUserMessage);

    // Send message using the Enter key.
    const userMessageInput = document.getElementById('userMessage');
    userMessageInput.addEventListener('keydown', handleKeyDown);

    // Toggle hamburger menu.
    const hamburgerToggle = document.querySelector("#hamburgerToggle");
    const menuItems = document.querySelector(".menu-items");

    hamburgerToggle.addEventListener("change", function() {
        menuItems.style.transform = this.checked ? 'translateX(0)' : 'translateX(-100%)';
    });
});
