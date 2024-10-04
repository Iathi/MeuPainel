document.getElementById('sendForm').addEventListener('submit', async (event) => {
  event.preventDefault();

  const message = document.getElementById('message').value;
  const groups = document.getElementById('groups').value.split(',');
  const total_messages = document.getElementById('total_messages').value;
  const delay = document.getElementById('delay').value;

  const data = {
    message: message,
    groups: groups,
    total_messages: total_messages,
    delay: delay
  };

  const response = await fetch('https://seu-backend.railway.app/send_messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });

  const result = await response.json();
  alert(result.status);
});
