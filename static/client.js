// static/client.js
const chatbox = document.getElementById('chatbox');
const messageForm = document.getElementById('message-form');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button'); // Button referenzieren

// Funktion zum Hinzufügen einer Nachricht zur Chatbox
// Gibt das erstellte Element zurück
function addMessage(text, type) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', type); // type = 'user', 'ai', 'loading', 'error'

    // Wandelt Zeilenumbrüche im Text in <br> Tags um (wichtig für Ollama-Antworten)
    messageElement.innerHTML = text.replace(/\n/g, '<br>');

    chatbox.appendChild(messageElement);
    scrollToBottom();
    return messageElement;
}

// Funktion zum Scrollen nach unten
function scrollToBottom() {
    chatbox.scrollTop = chatbox.scrollHeight;
}

// Wenn das Formular abgeschickt wird
messageForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const userQuery = messageInput.value.trim();

    if (userQuery && !sendButton.disabled) { // Nur senden, wenn Text da ist und Button aktiv ist
        // Deaktiviere Input und Button während der Verarbeitung
        messageInput.disabled = true;
        sendButton.disabled = true;

        addMessage(userQuery, 'user');
        messageInput.value = ''; // Eingabefeld leeren

        const loadingElement = addMessage('Denke nach...', 'loading');

        try {
            const response = await fetch('/process', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: userQuery }),
            });

            // Ladeanzeige entfernen, egal ob erfolgreich oder nicht
            chatbox.removeChild(loadingElement);

            const data = await response.json(); // Versuche immer, JSON zu lesen

            if (!response.ok) {
                // Zeige die Fehlermeldung vom Server an
                addMessage(`Fehler: ${data.error || `Status ${response.status}`}`, 'error');
                console.error('Serverfehler:', data.error || response.statusText);
            } else {
                // Erfolgreiche Antwort anzeigen
                addMessage(data.response, 'ai');
            }

        } catch (error) {
             // Netzwerkfehler oder anderer Client-seitiger Fehler
             if (chatbox.contains(loadingElement)) { // Sicherstellen, dass Ladeanzeige weg ist
                chatbox.removeChild(loadingElement);
             }
            console.error('Fehler beim Senden/Empfangen der Nachricht:', error);
            addMessage('Kommunikationsfehler. Bitte versuche es später erneut.', 'error');
        } finally {
            // Aktiviere Input und Button wieder
            messageInput.disabled = false;
            sendButton.disabled = false;
            messageInput.focus(); // Setze Fokus zurück ins Input-Feld
        }
    }
});

// Initial zum Ende scrollen, falls bereits Nachrichten da sind (z.B. die erste AI-Nachricht)
scrollToBottom();
