from telegram import Bot
import asyncio
import os

# Token do bot
TOKEN = '6859463280:AAGthI7TXdRdVJIp9U-cOvgF0EcC6AITdeM'
bot = Bot(token=TOKEN)

# Configurações automáticas
CHAT_ID = '@VendaemAlta'  # Nome de usuário do grupo/canal
MESSAGE = """🔥 ATENÇÃO 🔥
Lucros de R$ 17,29
Faca um Teste: https://paineltelegram.netlify.app/
Ganhe 65% de Comissão com o BotPro Anúncios & LEDs!"""

PHOTO_PATH = 'grupos.jpg'
NUM_TIMES = 2000  # Quantidade de envios
MESSAGE_INTERVAL = 20  # Intervalo entre mensagens em segundos
PHOTO_INTERVAL = 20  # Intervalo entre fotos em segundos

# Função para enviar texto e imagem
async def send_text_and_photo(chat_id, message, photo_path, num_times, message_interval, photo_interval):
    try:
        for i in range(num_times):
            # Enviar a mensagem
            await bot.send_message(chat_id=chat_id, text=message)
            print(f"Mensagem {i + 1} enviada com sucesso!")
            await asyncio.sleep(message_interval)

            # Verificar se o arquivo existe e é uma imagem válida
            if os.path.isfile(photo_path) and photo_path.lower().endswith(('.jpg', '.jpeg')):
                with open(photo_path, 'rb') as photo:
                    await bot.send_photo(chat_id=chat_id, photo=photo)
                    print(f"Foto {i + 1} enviada com sucesso!")
            else:
                print(f"Erro: Arquivo de imagem inválido ou não encontrado no caminho: {photo_path}")
            await asyncio.sleep(photo_interval)

    except Exception as e:
        print(f"Erro ao enviar mensagem ou foto: {e}")

# Função principal
async def main():
    await send_text_and_photo(CHAT_ID, MESSAGE, PHOTO_PATH, NUM_TIMES, MESSAGE_INTERVAL, PHOTO_INTERVAL)

if __name__ == '__main__':
    asyncio.run(main())