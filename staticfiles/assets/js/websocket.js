let socket;

function initializeWebSocket() {
    if (socket && socket.readyState === WebSocket.OPEN) {
        return; // WebSocket already open
    }

    socket = new WebSocket("ws://localhost:3001/ws/notifications/");

    socket.onopen = () => {
        console.log("WebSocket connection established.");
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === "notification") {
            displayNotification(data.message);
        }
    };

    socket.onclose = (event) => {
        console.log("WebSocket connection closed. Reconnecting...");
        setTimeout(initializeWebSocket, 3000); // Reconnect after 3 seconds
    };

    socket.onerror = (error) => {
        console.error("WebSocket error:", error);
        socket.close();
    };
}

function displayNotification(message) {
    // Display the notification in the UI
    console.log("New notification:", message);
}

// Initialize WebSocket on page load
initializeWebSocket();
