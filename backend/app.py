from flask import Flask, request, jsonify, session
from flask_cors import CORS
from telethon import TelegramClient
from telethon.sessions import StringSession
import os
import asyncio

app = Flask(__name__)
CORS(app)  # Adiciona suporte a CORS
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

@app.route('/send_messages', methods=['POST'])
def send_messages():
    data = request.json
    group_ids = data.get('groups')
    total_messages = int(data.get('total_messages'))
    delay = float(data.get('delay'))
    message = data.get('message')

    async def send_messages_task():
        for group_id in group_ids:
            try:
                for _ in range(total_messages):
                    await client.send_message(int(group_id), message)
                    await asyncio.sleep(delay)
            except Exception as e:
                return jsonify({'status': f"Erro ao enviar mensagem para o grupo {group_id}: {str(e)}"})

    loop.run_until_complete(send_messages_task())
    return jsonify({'status': 'Mensagens enviadas com sucesso'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
