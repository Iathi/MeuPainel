from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_socketio import SocketIO, emit
import subprocess
import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

app = Flask(__name__)
socketio = SocketIO(app)
app.secret_key = 'seu_segredo_aqui'

api_id = '24010179'  # Substitua pelo seu API ID
api_hash = '7ddc83d894b896975083f985effffe11'  # Substitua pelo seu API Hash

client = None
sending = False  # Variável global para controlar o envio
stop_sending_event = asyncio.Event()

def ensure_sessions_dir():
    if not os.path.exists('sessions'):
        os.makedirs('sessions')

async def async_start_client(phone_number):
    global client
    session_file = f'sessions/{phone_number}.session'
    ensure_sessions_dir()
    
    if os.path.exists(session_file):
        with open(session_file, 'r') as f:
            session_string = f.read().strip()
            client = TelegramClient(StringSession(session_string), api_id, api_hash)
    else:
        client = TelegramClient(StringSession(), api_id, api_hash)
        await client.connect()
        if not await client.is_user_authorized():
            await client.send_code_request(phone_number)
            return False  # Necessário verificar o código
        session_string = client.session.save()
        with open(session_file, 'w') as f:
            f.write(session_string)
    
    await client.connect()
    return True  # Login bem-sucedido

def login_required(f):
    """Decorador para exigir login antes de acessar uma rota."""
    async def decorated_function(*args, **kwargs):
        if 'phone_number' not in session:
            return redirect(url_for('login'))
        return await f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
async def login():
    if request.method == 'POST':
        phone_number = (await request.form)['phone_number']
        session['phone_number'] = phone_number
        if not await async_start_client(phone_number):
            # Redirecionar para a página de verificação se necessário
            return redirect(url_for('verify_code'))
        return redirect(url_for('index'))
    return await render_template('login.html')

@app.route('/verify_code', methods=['GET', 'POST'])
async def verify_code():
    if request.method == 'POST':
        code = (await request.form)['code']
        phone_number = session.get('phone_number')
        if client and client.session:
            try:
                await client.sign_in(code=code)
                # Após a verificação, salve a sessão
                session_file = f'sessions/{phone_number}.session'
                session_string = client.session.save()
                with open(session_file, 'w') as f:
                    f.write(session_string)
                return redirect(url_for('index'))
            except Exception as e:
                return f"Erro ao verificar o código: {e}"
    return await render_template('verify_code.html')

@app.route('/')  # Protegida por login_required
@login_required
async def index():
    phone_number = session.get('phone_number')

    if client is None or not client.is_connected():
        await async_start_client(phone_number)

    try:
        dialogs = await client.get_dialogs()
        groups = [(dialog.id, dialog.name) for dialog in dialogs if dialog.is_group]

        return await render_template('index.html', groups=groups)

    except Exception as e:
        print(f"Erro ao tentar listar os grupos: {str(e)}")
        return await render_template('index.html', groups=[])

@app.route('/send_messages', methods=['POST'])
@login_required
async def send_messages():
    global sending, stop_sending_event
    form = await request.form
    group_ids = form.getlist('groups')
    delay = float(form['delay'])
    message = form['message']

    session['status'] = {'sending': [], 'errors': []}
    sending = True
    stop_sending_event.clear()

    async def send_messages_task():
        global sending
        for group_id in group_ids:
            if not sending:
                break
            try:
                # Enviar uma única mensagem para cada grupo
                await client.send_message(int(group_id), message)
                session['status']['sending'].append(f"✅ Mensagem enviada para o grupo {group_id}")
                await asyncio.sleep(delay)
            except Exception as e:
                session['status']['errors'].append(f"❌ Erro ao enviar mensagem para o grupo {group_id}: {str(e)}")

        sending = False
        stop_sending_event.set()

    await send_messages_task()
    return jsonify(session['status'])

@app.route('/status_updates')
@login_required
async def status_updates():
    if 'status' in session:
        return jsonify(session['status'])
    return jsonify({'sending': [], 'errors': []})

@app.route('/stop_sending', methods=['POST'])
@login_required
async def stop_sending():
    global sending
    sending = False
    stop_sending_event.set()
    return jsonify(session.get('status', {'sending': [], 'errors': []}))

@app.route('/terminal')  # Nova rota para terminal.html
@login_required
def terminal():
    return render_template('terminal.html')

@socketio.on('run_command')
def handle_command(data):
    command = data['command']
    try:
        # Executa o comando no terminal e captura a saída
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        output = output.decode('utf-8')
    except subprocess.CalledProcessError as e:
        output = e.output.decode('utf-8')

    # Envia a saída do comando de volta ao cliente
    emit('command_output', {'output': output})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
