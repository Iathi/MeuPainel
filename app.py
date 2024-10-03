from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_cors import CORS
from telethon import TelegramClient
from telethon.sessions import StringSession
import os
import asyncio

app = Flask(__name__)
CORS(app)  # Adicionando suporte a CORS
app.secret_key = 'seu_segredo_aqui'

api_id = '24010179'  # Substitua pelo seu API ID
api_hash = '7ddc83d894b896975083f985effffe11'  # Substitua pelo seu API Hash

client = None
loop = asyncio.new_event_loop()

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
            await client.start(phone=phone_number)
            session_string = client.session.save()
            with open(session_file, 'w') as f:
                f.write(session_string)

    await client.connect()

def start_client(phone_number):
    loop.run_until_complete(async_start_client(phone_number))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone_number = request.form['phone_number']
        session['phone_number'] = phone_number
        start_client(phone_number)
        return redirect(url_for('index'))
    return render_template('login.html')

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
    group_ids = request.form.getlist('groups')
    total_messages = int(request.form['total_messages'])
    delay = float(request.form['delay'])
    message = request.form['message']

    session['status'] = {'sending': [], 'errors': []}

    async def send_messages_task():
        for group_id in group_ids:
            try:
                for _ in range(total_messages):
                    await client.send_message(int(group_id), message)
                    session['status']['sending'].append(f"✅ Mensagem enviada para o grupo {group_id}")
                    await asyncio.sleep(delay)
            except Exception as e:
                session['status']['errors'].append(f"❌ Erro ao enviar mensagem para o grupo {group_id}: {str(e)}")

    loop.run_until_complete(send_messages_task())
    return redirect(url_for('status'))

@app.route('/status')
def status():
    if 'status' in session:
        return render_template('status.html', status=session['status'])
    return redirect(url_for('index'))

@app.route('/status_updates')
def status_updates():
    if 'status' in session:
        return jsonify(session['status']['sending'])
    return jsonify([])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
