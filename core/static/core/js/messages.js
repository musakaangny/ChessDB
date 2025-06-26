// This script handles the notification on the top-right corner.
// Refreshing the page re-renders the notification but it is not a critical issue for this project
document.addEventListener('DOMContentLoaded', function() {
    const fixedMessagesContainer = document.getElementById('fixed-messages');
    if (fixedMessagesContainer) {
        const messages = fixedMessagesContainer.querySelectorAll('.message, .error');
        messages.forEach(function(message) {
            setTimeout(function() {
                message.style.display = 'none'; 
            }, 5000);
        });
    }
});
