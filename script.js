document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('chatForm');
    const chatContainer = document.getElementById('chatContainer');

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const platform = document.getElementById('platform').value;
        const username = document.getElementById('username').value;
        loadChat(platform, username);
    });

    function loadChat(platform, username) {
        let chatUrl;
        if (platform === 'twitch') {
            chatUrl = `https://www.twitch.tv/embed/${username}/chat?parent=${window.location.hostname}`;
        } else if (platform === 'kick') {
            chatUrl = `kick-proxy.html?username=${encodeURIComponent(username)}`;
        }

        console.log(chatUrl);
        
        const chatDiv = document.createElement('div');
        chatDiv.innerHTML = `<iframe src="${chatUrl}" height="500" width="100%" frameborder="0"></iframe>`;
        chatContainer.innerHTML = ''; // Clear previous chat
        chatContainer.appendChild(chatDiv);

        // Remove the interval as it's not necessary anymore
    }
});
