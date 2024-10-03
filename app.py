import csv
import time
import os
import asyncio
from telethon.sync import TelegramClient
from telethon import utils

# Configurações da API do Telegram
api_id = 24010179  # Substitua com o seu API ID
api_hash = '7ddc83d894b896975083f985effffe11'  # Substitua com o seu API Hash

# Função para verificar permissão de envio de mensagens
async def check_message_permission(client, group_id):
    try:
        # Verifica se o grupo é acessível sem enviar mensagem
        await client.get_entity(group_id)
        return True
    except Exception:
        return False

# Ler números de telefone do arquivo CSV
def read_phone_numbers(filename):
    if not os.path.exists(filename):
        print(f"Arquivo {filename} não encontrado.")
        return []
    
    with open(filename, 'r') as f:
        return [row[0] for row in csv.reader(f)]

# Função principal para executar o script
async def main():
    phone_numbers = read_phone_numbers('phone.csv')

    if not phone_numbers:
        print("Nenhum número de telefone disponível.")
        return

    # Seleção do número de telefone
    print("📋 Números de telefone disponíveis:")
    for idx, phone in enumerate(phone_numbers):
        print(f"{idx + 1}: {phone}")

    phone_index = int(input("\nEscolha o número de telefone (número): ")) - 1
    if not (0 <= phone_index < len(phone_numbers)):
        print("Número inválido.")
        return

    phone = utils.parse_phone(phone_numbers[phone_index])
    print(f"\nVocê escolheu o número: {phone}")

    # Criar cliente Telegram
    client = TelegramClient(f"sessions/{phone}", api_id, api_hash)

    try:
        await client.start(phone)
        print(f"✅ Login bem-sucedido para: {phone}")
    except Exception as e:
        print(f"❌ Erro ao iniciar sessão para {phone}: {e}")
        return

    # Coletar e listar apenas grupos com permissão para enviar mensagens
    print(f"\n🔍 Coletando grupos com permissão para enviar mensagens para {phone}...")
    groups = []
    async for dialog in client.iter_dialogs():
        if dialog.is_group:
            group_id = dialog.entity.id
            group_name = dialog.name
            if await check_message_permission(client, group_id):
                groups.append((group_name, group_id))
                print(f'🌟 Grupo: {group_name} (ID: {group_id}) - Permissão: Pode enviar mensagens')

    if not groups:
        print("🚫 Nenhum grupo com permissão encontrado.")
        await client.disconnect()
        return

    # Seleção de múltiplos grupos de destino
    print("\nEscolha os grupos para enviar a mensagem (separe os números por vírgula):")
    for idx, (group_name, group_id) in enumerate(groups):
        print(f"{idx + 1}: {group_name} (ID: {group_id})")

    selected_indices = input("\nEscolha os grupos (números separados por vírgula): ")
    selected_indices = [int(idx.strip()) - 1 for idx in selected_indices.split(',')]

    selected_groups = [groups[idx] for idx in selected_indices if 0 <= idx < len(groups)]
    if not selected_groups:
        print("Nenhum grupo selecionado ou seleção inválida.")
        await client.disconnect()
        return

    print(f"\nVocê escolheu os seguintes grupos:")
    for group_name, group_id in selected_groups:
        print(f"📍 {group_name} (ID: {group_id})")

    # Configurações de envio de mensagens
    total_messages = int(input("Digite o número total de mensagens a serem enviadas: "))
    delay = float(input("Digite o intervalo entre mensagens (em segundos): "))

    # Mensagem a ser enviada
    message = (
        "🔥 ATENÇÃO 🔥\n\n"
        "Estamos buscando parcerias! Se você está interessado em colaborar e explorar novas oportunidades, esta é a sua chance!\n\n"
        "- Construa parcerias com uma equipe inovadora! 🚀\n"
        "- Desenvolva projetos em um ambiente dinâmico! 💡\n"
        "- Aumente suas oportunidades de crescimento! 📈\n\n"
        "Para mais detalhes e parcerias, entre em contato: https://t.me/Dinheir0Gratis\n\n"
        "Vamos crescer juntos! 🤝"
    )

    # Envio das mensagens
    num_groups = len(selected_groups)
    messages_sent = 0
    group_index = 0

    while messages_sent < total_messages:
        group_name, group_id = selected_groups[group_index]
        try:
            await client.send_message(group_id, message)
            messages_sent += 1
            print(f"✉️ Mensagem enviada para {group_name}. Total enviado: {messages_sent}/{total_messages}")
            await asyncio.sleep(delay)  # Espera pelo intervalo especificado
        except Exception as e:
            print(f"❌ Erro ao enviar mensagem para {group_name}: {e}")

        # Alterna para o próximo grupo
        group_index = (group_index + 1) % num_groups

    await client.disconnect()
    print("🔌 Desconectado.") 

if __name__ == "__main__":
    asyncio.run(main())