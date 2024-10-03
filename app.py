import os
from telethon.sync import TelegramClient
from telethon import utils
import csv
import time

# Configurações da API do Telegram
api_id = os.getenv('API_ID')  # Pegue o API_ID da variável de ambiente
api_hash = os.getenv('API_HASH')  # Pegue o API_HASH da variável de ambiente

# Ler números de telefone do arquivo CSV
def read_phone_numbers(filename):
    with open(filename, 'r') as f:
        return [row[0] for row in csv.reader(f)]

# Função principal para executar o script
def main():
    phone_numbers = read_phone_numbers('phone.csv')

    # Pega o índice do número de telefone de uma variável de ambiente
    phone_index = int(os.getenv('PHONE_INDEX', 0))  # Defina o índice padrão como 0 se não estiver definido
    if not (0 <= phone_index < len(phone_numbers)):
        print("Número inválido.")
        return

    phone = utils.parse_phone(phone_numbers[phone_index])
    print(f"\nVocê escolheu o número: {phone}")

    # Criar cliente Telegram
    client = TelegramClient(f"sessions/{phone}", api_id, api_hash)

    try:
        client.start(phone)
        print(f"✅ Login bem-sucedido para: {phone}")
    except Exception as e:
        print(f"❌ Erro ao iniciar sessão para {phone}: {e}")
        return

    # Coletar e listar apenas grupos com permissão para enviar mensagens
    print(f"\n🔍 Coletando grupos com permissão para enviar mensagens para {phone}...")
    groups = []
    for dialog in client.iter_dialogs():
        if dialog.is_group:
            group_id = dialog.entity.id
            group_name = dialog.name
            groups.append((group_name, group_id))
            print(f'🌟 Grupo: {group_name} (ID: {group_id})')

    if not groups:
        print("🚫 Nenhum grupo com permissão encontrado.")
        client.disconnect()
        return

    # Seleção de múltiplos grupos de destino via variável de ambiente
    selected_indices = os.getenv('GROUP_INDICES', '0').split(',')
    selected_groups = [groups[int(idx.strip())] for idx in selected_indices if idx.isdigit() and 0 <= int(idx) < len(groups)]
    if not selected_groups:
        print("Nenhum grupo selecionado ou seleção inválida.")
        client.disconnect()
        return

    print(f"\nVocê escolheu os seguintes grupos:")
    for group_name, group_id in selected_groups:
        print(f"📍 {group_name} (ID: {group_id})")

    # Configurações de envio de mensagens
    total_messages = int(os.getenv('TOTAL_MESSAGES', 10))
    delay = float(os.getenv('MESSAGE_DELAY', 5.0))

    # Mensagem a ser enviada
    message = os.getenv('MESSAGE', "Mensagem padrão de parceria.")

    # Envio das mensagens
    num_groups = len(selected_groups)
    messages_sent = 0
    group_index = 0

    while messages_sent < total_messages:
        group_name, group_id = selected_groups[group_index]
        try:
            client.send_message(group_id, message)
            messages_sent += 1
            print(f"✉️ Mensagem enviada para {group_name}. Total enviado: {messages_sent}/{total_messages}")
            time.sleep(delay)  # Espera pelo intervalo especificado
        except Exception as e:
            print(f"❌ Erro ao enviar mensagem para {group_name}: {e}")

        # Alterna para o próximo grupo
        group_index = (group_index + 1) % num_groups

    client.disconnect()
    print("🔌 Desconectado.")

if __name__ == "__main__":
    main()