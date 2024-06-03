// Function to copy the AI response to the clipboard
function copyToClipboard(event) {
    const button = event.target.closest('button');
    const messageContent = button.closest('.message-left').querySelector('.message-content').textContent;
    navigator.clipboard.writeText(messageContent).then(() => {
        console.log('Text copied to clipboard');
    }).catch(err => {
        console.error('Error copying text: ', err);
    });
}

// Function to copy the AI response to the clipboard
function copyToClipboard(event) {
    const button = event.target.closest('button');
    const messageContent = button.closest('.message-left').querySelector('.message-content').textContent;
    navigator.clipboard.writeText(messageContent).then(() => {
        console.log('Text copied to clipboard');
    }).catch(err => {
        console.error('Error copying text: ', err);
    });
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
    //add the current url of the user
    const url = window.location.href;
    const button = event.target.closest('button');
    const messageContent = button.closest('.message-left').querySelector('.message-content').textContent;
    const languagePrefix = getLanguagePrefix();
    const csrfToken = getCookie('csrftoken')
    const urlEndpoint = `/${languagePrefix}/interaction-user-messages/`;
    fetch(urlEndpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken':  csrfToken// Assuming you have a function to get the CSRF token
        },
        body: JSON.stringify({ message: messageContent, action: action, url: url })
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