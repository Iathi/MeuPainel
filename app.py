from telegram import Bot
from telegram.error import TelegramError
import asyncio
import os

# Token do bot
TOKEN = '6859463280:AAGthI7TXdRdVJIp9U-cOvgF0EcC6AITdeM'
bot = Bot(token=TOKEN)

# Configurações automáticas
CHAT_ID = '@VendaemAlta'  # Nome de usuário do grupo/canal
MESSAGE = """🔥 ATENÇÃO 🔥
🔥 ATENÇÃO 🔥
Lucros de R$ 17,29
Faca um Teste 
https://paineltelegram.netlify.app/

https://t.me/Dinheir0Gratis
Ganhe 65% de Comissão com o BotPro Anúncios & LEDs! Participe do nosso programa de afiliados e ganhe 65% de comissão ao promover o BotPro Anúncios & LEDs. Este produto revolucionário automatiza campanhas publicitárias e controla LEDs com eficiência e facilidade. Ofereça aos seus seguidores uma solução inovadora para otimizar anúncios e projetos com LEDs e aproveite uma alta comissão sobre cada venda gerada. Não perca a chance de aumentar seus ganhos com um produto que realmente faz a diferença!"""
PHOTO_PATH = 'grupos.jpg'
NUM_TIMES = 2000  # Quantas vezes enviar a mensagem e a foto
MESSAGE_INTERVAL = 20  # Intervalo em segundos entre cada envio de mensagem
PHOTO_INTERVAL = 20  # Intervalo em segundos entre cada envio de foto

# Função para enviar texto e imagem
async def send_text_and_photo(chat_id, message, photo_path, num_times, message_interval, photo_interval):
    try:
        for i in range(num_times):
            # Enviar a mensagem
            await bot.send_message(chat_id=chat_id, text=message)
            print(f"Mensagem {i + 1} enviada com sucesso!")
            await asyncio.sleep(message_interval)

            # Verificar se o arquivo existe e é um JPG
            if os.path.isfile(photo_path) and photo_path.lower().endswith(('.jpg', '.jpeg')):
                try:
                    with open(photo_path, 'rb') as photo:
                        await bot.send_photo(chat_id=chat_id, photo=photo)
                        print(f"Foto {i + 1} enviada com sucesso!")
                except FileNotFoundError:
                    print(f"Arquivo de imagem não encontrado no caminho: {photo_path}")
                except Exception as e:
                    print(f"Erro ao enviar a foto: {e}")
            else:
                print(f"O aí as e:
        print(f"Erro ao enviar mensagem ou foto: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")

# Função principal
async def main():
    # Enviar a mensagem e a foto o número especificado de vezes
    await send_text_and_photo(CHAT_ID, MESSAGE, PHOTO_PATH, NUM_TIMES, MESSAGE_INTERVAL, PHOTO_INTERVAL)

if __name__ == '__main__':
    asyncio.run(main())
