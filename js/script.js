document.getElementById('loginForm').onsubmit = function(e) {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    if (username === "" || password === "") {
        e.preventDefault();
        document.getElementById('error-message').innerText = "Por favor, preencha todos os campos.";
    } else {
        document.getElementById('error-message').innerText = ""; // Limpa a mensagem de erro
    }
};