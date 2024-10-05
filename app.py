from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from telethon import TelegramClient
from telethon.sessions import StringSession
import os
import asyncio

app = Flask(__name__)
app.secret_key = 'seu_segredo_aqui'  # Alterar para uma chave segura

api_id = os.getenv('API_ID')  # Defina como variável de ambiente
api_hash = os.getenv('API_HASH')  # Defina como variável de ambiente

client = None
loop = asyncio.new_event_loop()
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

def start_client(phone_number):
    return loop.run_until_complete(async_start_client(phone_number))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone_number = request.form['phone_number']
        session['phone_number'] = phone_number
        if not start_client(phone_number):
            return redirect(url_for('verify_code'))
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/verify_code', methods=['GET', 'POST'])
def verify_code():
    if request.method == 'POST':
        code = request.form['code']
        phone_number = session.get('phone_number')
        if client and client.session:
            try:
                loop.run_until_complete(client.sign_in(code=code))
                session_file = f'sessions/{phone_number}.session'
                session_string = client.session.save()
                with open(session_file, 'w') as f:
                    f.write(session_string)
                return redirect(url_for('index'))
            except Exception as e:
                return f"Erro ao verificar o código: {e}"
    return render_template('verify_code.html')

@app.route('/')
def index():
    if 'phone_number' not in session:
        return redirect(url_for('login'))

    phone_number = session.get('phone_number')

    if client is None or not client.is_connected():
        start_client(phone_number)

    try:
        dialogs = loop.run_until_complete(client.get_dialogs())
        groups = [(dialog.id, dialog.name) for dialog in dialogs if dialog.is_group]

        return render_template('index.html', groups=groups)

    except Exception as e:
        print(f"Erro ao tentar listar os grupos: {str(e)}")
        return render_template('index.html', groups=[])

@app.route('/send_messages', methods=['POST'])
def send_messages():
    global sending, stop_sending_event
    group_ids = request.form.getlist('groups')
    delay = float(request.form['delay'])
    message = request.form['message']

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

    loop.run_until_complete(send_messages_task())
    return jsonify(session['status'])

@app.route('/status_updates')
def status_updates():
    if 'status' in session:
        return jsonify(session['status'])
    return jsonify({'sending': [], 'errors': []})

@app.route('/stop_sending', methods=['POST'])
def stop_sending():
    global sending
    sending = False
    stop_sending_event.set()
    return jsonify(session.get('status', {'sending': [], 'errors': []}))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
