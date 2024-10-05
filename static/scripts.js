document.getElementById('send-form').addEventListener('submit', function (event) {
    event.preventDefault();

    const formData = new FormData(this);
    const groups = formData.getAll('groups');
    const message = formData.get('message');
    const delay = formData.get('delay');

    if (!groups.length || !message || !delay) {
        alert('Por favor, preencha todos os campos.');
        return;
    }

    // Enviar a mensagem via POST para o backend
    fetch('/send_messages', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('status').innerHTML = '<h3>Status das Mensagens:</h3>';
        updateStatus();
    })
    .catch(error => {
        console.error('Erro ao enviar a mensagem:', error);
    });
});

function updateStatus() {
    fetch('/status_updates')
        .then(response => response.json())
        .then(data => {
            let statusElement = document.getElementById('status');
            statusElement.innerHTML = '<h3>Status das Mensagens:</h3>';

            if (data.sending.length > 0) {
                statusElement.innerHTML += '<ul>';
                data.sending.forEach(function (status) {
                    statusElement.innerHTML += `<li>${status}</li>`;
                });
                statusElement.innerHTML += '</ul>';
            }

            if (data.errors.length > 0) {
                statusElement.innerHTML += '<h3>Erros:</h3>';
                statusElement.innerHTML += '<ul>';
                data.errors.forEach(function (error) {
                    statusElement.innerHTML += `<li>${error}</li>`;
                });
                statusElement.innerHTML += '</ul>';
            }

            // Continuar atualizando até que o envio seja concluído
            if (data.sending.length > 0 || data.errors.length > 0) {
                setTimeout(updateStatus, 3000);
            }
        })
        .catch(error => {
            console.error('Erro ao atualizar o status:', error);
        });
}

document.getElementById('stop-button').addEventListener('click', function () {
    fetch('/stop_sending', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            updateStatus();
        })
        .catch(error => {
            console.error('Erro ao interromper o envio:', error);
        });
});
