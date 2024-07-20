document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('chatForm');
    const chatContainer = document.getElementById('chatContainer');

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const platform = document.getElementById('platform').value;
        const username = document.getElementById('username').value;
        loadChat(platform, username);
    });

    async function loadChat(platform, username) {
        let chatUrl;
        if (platform === 'twitch') {
            chatUrl = `https://www.twitch.tv/embed/${username}/chat?parent=${window.location.hostname}`;
            const chatDiv = document.createElement('div');
            chatDiv.innerHTML = `<iframe src="${chatUrl}" height="500" width="100%" frameborder="0"></iframe>`;
            chatContainer.innerHTML = ''; // Clear previous chat
            chatContainer.appendChild(chatDiv);
        } else if (platform === 'kick') {
            chatUrl = `http://127.0.0.1:5000/kick_proxy?username=${encodeURIComponent(username)}`;
            try {
                // First, get the CSRF token
                const csrfResponse = await fetch('http://127.0.0.1:5000/sanctum/csrf-cookie', {
                    method: 'GET',
                    credentials: 'include',
                });
                
                if (!csrfResponse.ok) {
                    throw new Error('Failed to get CSRF token');
                }

                // Now fetch the chat content
                const response = await fetch(chatUrl, {
                    method: 'GET',
                    credentials: 'include',
                    headers: {
                        'X-XSRF-TOKEN': getCookie('XSRF-TOKEN'),
                    },
                });

                if (!response.ok) {
                    throw new Error('Network response was not ok ' + response.statusText);
                }

                const data = await response.text();
                const chatDiv = document.createElement('div');
                chatDiv.innerHTML = data;
                chatContainer.innerHTML = ''; // Clear previous chat
                chatContainer.appendChild(chatDiv);
            } catch (error) {
                console.error('There was a problem with the fetch operation:', error);
                chatContainer.innerHTML = `<p>Error loading chat: ${error.message}</p>`;
            }
        }
    }

    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }
});
