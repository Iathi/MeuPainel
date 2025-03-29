from quart import Quart, render_template, request, redirect, url_for, session, jsonify
from telethon import TelegramClient
from telethon.sessions import StringSession
import os
import asyncio

# Inicialização do app
app = Quart(__name__)
app.secret_key = 'seu_segredo_aqui'

api_id = '24010179'  # Substitua pelo seu API ID
api_hash = '7ddc83d894b896975083f985effffe11'  # Substitua pelo seu API Hash

client = None
sending = False  # Variável global para controlar o envio
stop_sending_event = asyncio.Event()

# Função para garantir a existência do diretório de sessões
def ensure_sessions_dir():
    """Garante que a pasta 'sessions' exista."""
    if not os.path.exists('sessions'):
        os.makedirs('sessions')

# Função assíncrona para iniciar o cliente Telegram
async def async_start_client(phone_number):
    """Inicia a sessão do TelegramClient."""
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

# Rota de login
@app.route('/login', methods=['GET', 'POST'])
async def login():
    """Página de login do Telegram."""
    if request.method == 'POST':
        phone_number = (await request.form)['phone_number']
        session['phone_number'] = phone_number
        if not await async_start_client(phone_number):
            return redirect(url_for('verify_code'))  # Redireciona para verificação
        return redirect(url_for('index'))
    return await render_template('login.html')

# Rota de verificação do código
@app.route('/verify_code', methods=['GET', 'POST'])
async def verify_code():
    """Página para inserir o código de verificação do Telegram."""
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

# Página principal que exibe os grupos disponíveis
@app.route('/')
async def index():
    """Página principal que exibe os grupos disponíveis."""
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

# Rota para enviar mensagens
@app.route('/send_messages', methods=['POST'])
async def send_messages():
    """Envia uma mensagem para cada grupo um por vez em um loop infinito."""
    global sending, stop_sending_event

    form = await request.form
    group_ids = form.getlist('groups')
    delay = float(form['delay'])
    message = form['message']

    session['status'] = {'sending': [], 'errors': []}
    sending = True
    stop_sending_event.clear()

    async def send_messages_task():
        """Tarefa assíncrona para envio de mensagens com loop infinito."""
        global sending
        while sending:  # Loop infinito enquanto o envio estiver ativo
            for group_id in group_ids:
                if not sending:
                    break
                try:
                    if client is None or not await client.is_user_authorized():
                        session['status']['errors'].append("❌ Cliente não conectado.")
                        break
                    
                    # Enviar uma única mensagem para cada grupo
                    await client.send_message(int(group_id), message)
                    session['status']['sending'].append(f"✅ Mensagem enviada para o grupo {group_id}")
                    await asyncio.sleep(delay)
                except Exception as e:
                    session['status']['errors'].append(f"❌ Erro ao enviar mensagem para o grupo {group_id}: {str(e)}")

            # Reiniciar o envio para os mesmos grupos após um ciclo completo
            if sending:
                session['status']['sending'].append("🔄 Reiniciando o envio de mensagens.")
                await asyncio.sleep(5)  # Pausa antes de reiniciar (opcional)

        stop_sending_event.set()

    asyncio.create_task(send_messages_task())  # Inicia a tarefa sem bloquear a execução
    return jsonify(session['status'])

# Rota para consultar o status do envio
@app.route('/status_updates')
async def status_updates():
    """Retorna o status do envio de mensagens."""
    if 'status' in session:
        return jsonify(session['status'])
    return jsonify({'sending': [], 'errors': []})

# Rota para parar o envio de mensagens
@app.route('/stop_sending', methods=['POST'])
async def stop_sending():
    """Para o envio de mensagens."""
    global sending
    sending = False
    stop_sending_event.set()
    return jsonify(session.get('status', {'sending': [], 'errors': []}))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
