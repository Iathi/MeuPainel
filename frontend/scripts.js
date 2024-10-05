document.getElementById('send-form').addEventListener('submit', function (event) {
    event.preventDefault();

    const message = document.getElementById('message').value;
    const groups = document.getElementById('groups').value.split(',');
    const delay = document.getElementById('delay').value;

    fetch('/send_messages', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            message: message,
            groups: groups,
            delay: delay,
        }),
    })
    .then(response => response.json())
    .then(data => {
        updateStatus(data);
    })
    .catch(error => console.error('Erro ao enviar mensagens:', error));
});

function updateStatus(data) {
    const statusDiv = document.getElementById('status');
    statusDiv.innerHTML = '';

    if (data.sending.length > 0) {
        data.sending.forEach(msg => {
            const p = document.createElement('p');
            p.textContent = msg;
            statusDiv.appendChild(p);
        });
    }

    if (data.errors.length > 0) {
        data.errors.forEach(error => {
            const p = document.createElement('p');
            p.textContent = error;
            p.style.color = 'red';
            statusDiv.appendChild(p);
        });
    }
}
