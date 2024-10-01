// functions/check-password.js

exports.handler = async (event, context) => {
    const users = {
        'usuario1': 'senha1',
        'usuario2': 'senha2',
    };

    const { username, password } = JSON.parse(event.body);

    // Verifica as credenciais
    if (users[username] && users[username] === password) {
        return {
            statusCode: 200,
            body: JSON.stringify({ success: true }),
        };
    }

    return {
        statusCode: 401,
        body: JSON.stringify({ success: false }),
    };
};