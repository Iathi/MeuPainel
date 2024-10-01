from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)
app.secret_key = 'sua_chave_secreta'  # Altere isso para algo seguro em produção

# Usuários de exemplo com senha hash (substitua por um banco de dados em produção)
users = {
    "admin": generate_password_hash("9999")  # Exemplo de usuário e senha do administrador
}

# Dicionário para armazenar as localizações dos entregadores
deliverer_locations = {}
# Lista para armazenar os pedidos
deliveries = []
# Lista para armazenar as mensagens do chat
messages = []

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Verifica se o usuário e senha estão corretos
        if username in users and check_password_hash(users[username], password):
            flash('Login bem-sucedido!', 'success')
            session['username'] = username  # Armazena o nome do usuário na sessão
            return redirect(url_for('index'))  # Redireciona para a página inicial após o login
        else:
            flash('Usuário ou senha incorretos. Tente novamente.', 'danger')

    return render_template('login.html')

@app.route('/index')
def index():
    return render_template('index.html', deliveries=deliveries)  # Passa a lista de pedidos para o template

@app.route('/pedidos')
def pedidos():
    return render_template('pedidos.html')  # Renderiza a página de pedidos

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if 'username' in session and session['username'] == 'admin':  # Apenas o admin pode adicionar usuários
        if request.method == 'POST':
            new_username = request.form['username']
            new_password = request.form['password']
            if new_username in users:
                flash('Usuário já existe!', 'danger')
            else:
                # Gera o hash da senha e adiciona o novo usuário
                users[new_username] = generate_password_hash(new_password)
                flash(f'Usuário {new_username} adicionado com sucesso!', 'success')
            return redirect(url_for('add_user'))
        return render_template('add_user.html')  # Exibe o formulário
    else:
        flash('Acesso negado! Somente administradores podem adicionar usuários.', 'danger')
        return redirect(url_for('login'))

@app.route('/api/update_location', methods=['POST'])
def update_location():
    data = request.json
    deliverer_id = data.get('id')
    try:
        latitude = float(data.get('lat'))
        longitude = float(data.get('lng'))
    except (TypeError, ValueError):
        return jsonify(success=False, message="Coordenadas inválidas")

    if deliverer_id and latitude and longitude:
        deliverer_locations[deliverer_id] = {'lat': latitude, 'lng': longitude}
        return jsonify(success=True)
    return jsonify(success=False, message="Dados inválidos")

@app.route('/api/get_all_deliverer_locations', methods=['GET'])
def get_all_deliverer_locations():
    return jsonify(deliverer_locations)

@app.route('/api/get_deliveries', methods=['GET'])
def get_deliveries():
    return jsonify(deliveries)

@app.route('/api/accept_delivery/<int:delivery_id>', methods=['POST'])
def accept_delivery(delivery_id):
    # Simulação de aceitação de entrega
    return jsonify(success=True)

@app.route('/api/create_delivery', methods=['POST'])
def create_delivery():
    data = request.json
    address = data.get('address')
    quantity = data.get('quantity')

    if address and isinstance(quantity, int) and quantity > 0:
        # Adiciona o novo pedido à lista
        deliveries.append({'address': address, 'quantity': quantity})
        return jsonify(success=True)
    return jsonify(success=False, message="Dados inválidos")

@app.route('/api/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    message = {'sender': session.get('username', 'Usuário'), 'content': data['message']}
    messages.append(message)
    return jsonify({'status': 'Mensagem enviada'}), 200

@app.route('/api/get_messages', methods=['GET'])
def get_messages():
    return jsonify({'messages': messages}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
