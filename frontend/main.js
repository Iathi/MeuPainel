// Função para enviar mensagens para grupos
async function sendMessages() {
    const groupIds = Array.from(document.querySelectorAll('input[name="groups"]:checked')).map(input => input.value);
    const totalMessages = document.getElementById('totalMessages').value;
    const delay = document.getElementById('delay').value;
    const message = document.getElementById('message').value;

    const response = await fetch('/send_messages', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            groups: groupIds,
            total_messages: totalMessages,
            delay: delay,
            message: message
        })
    });

    if (response.ok) {
        alert('Mensagens enviadas com sucesso!');
        // Redirecionar para a página de status ou outra página conforme necessário
        window.location.href = '/status';
    } else {
        const errorData = await response.json();
        alert('Erro ao enviar mensagens: ' + errorData.message);
    }
}

// Função para buscar atualizações de status
async function fetchStatusUpdates() {
    const response = await fetch('/status_updates');
    if (response.ok) {
        const statusUpdates = await response.json();
        const statusContainer = document.getElementById('statusContainer');
        statusContainer.innerHTML = ''; // Limpar status anterior

        statusUpdates.forEach(status => {
            const statusElement = document.createElement('div');
            statusElement.textContent = status;
            statusContainer.appendChild(statusElement);
        });
    } else {
        console.error('Erro ao buscar atualizações de status');
    }
}

// Adiciona um evento ao botão de enviar
document.getElementById('sendButton').addEventListener('click', sendMessages);

// Atualiza o status a cada 5 segundos
setInterval(fetchStatusUpdates, 5000);
