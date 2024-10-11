from quart import Quart, websocket, render_template
import subprocess
import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

app = Quart(__name__)
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

@app.route('/')
async def index():
    return await render_template('terminal.html')

@app.websocket('/ws')
async def ws():
    while True:
        command = await websocket.receive()
        try:
            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            output = output.decode('utf-8')
        except subprocess.CalledProcessError as e:
            output = e.output.decode('utf-8')

        await websocket.send(output)

@app.route('/login', methods=['GET', 'POST'])
async def login():
    if request.method == 'POST':
        form = await request.form
        phone_number = form['phone_number']
        session['phone_number'] = phone_number
        if not await async_start_client(phone_number):
            return redirect(url_for('verify_code'))
        return redirect(url_for('index'))
    return await render_template('login.html')

@app.route('/verify_code', methods=['GET', 'POST'])
async def verify_code():
    if request.method == 'POST':
        form = await request.form
        code = form['code']
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
