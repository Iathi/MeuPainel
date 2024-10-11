from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError
import os
import asyncio
import logging
import time

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default_secret')

api_id = os.environ.get('24010179')  # Use environment variable
api_hash = os.environ.get('7ddc83d894b896975083f985effffe11')  # Use environment variable

client = None
loop = asyncio.new_event_loop()
sending = False
stop_sending_event = asyncio.Event()

# Set up logging
logging.basicConfig(level=logging.INFO)

def ensure_sessions_dir():
    if not os.path.exists('sessions'):
        os.makedirs('sessions')

async def async_start_client(phone_number):
    global client
    session_file = f'sessions/{phone_number}.session'
    ensure_sessions_dir()

    try:
        if os.path.exists(session_file):
            with open(session_file, 'r') as f:
                session_string = f.read().strip()
                client = TelegramClient(StringSession(session_string), api_id, api_hash)
        else:
            client = TelegramClient(StringSession(), api_id, api_hash)
            await client.connect()
            if not await client.is_user_authorized():
                while True:
                    try:
                        await client.start(phone=phone_number)
                        break
                    except FloodWaitError as e:
                        wait_time = e.seconds
                        logging.warning(f"FloodWaitError: Waiting for {wait_time} seconds.")
                        time.sleep(wait_time)  # Wait for the specified time

        await client.connect()
    except Exception as e:
        logging.error(f"Error starting Telegram client: {str(e)}")
        return None

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
        logging.error(f"Error fetching groups: {str(e)}")
        return render_template('index.html', groups=[])

@app.route('/send_messages', methods=['POST'])
def send_messages():
    global sending, stop_sending_event
    group_ids = request.form.getlist('groups')
    total_messages = int(request.form['total_messages'])
    delay = float(request.form['delay'])
    message = request.form['message']

    session['status'] = {'sending': [], 'errors': []}
    sending = True
    stop_sending_event.clear()

    async def send_messages_task():
        global sending
        try:
            for group_id in group_ids:
                if not sending:
                    break
                for _ in range(total_messages):
                    if not sending:
                        break
                    try:
                        await client.send_message(int(group_id), message)
                        session['status']['sending'].append(f"✅ Message sent to group {group_id}")
                        await asyncio.sleep(delay)
                    except FloodWaitError as e:
                        wait_time = e.seconds
                        logging.warning(f"FloodWaitError while sending message: Waiting for {wait_time} seconds.")
                        time.sleep(wait_time)  # Wait before continuing
                        break  # Stop sending to this group and move to the next
        except Exception as e:
            session['status']['errors'].append(f"❌ Error sending message: {str(e)}")
        finally:
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
    app.run(debug=True, host='0.0.0.0', port=5000)
