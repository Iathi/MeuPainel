# Usando uma imagem base do Python
FROM python:3.9-slim

# Definindo o diretório de trabalho
WORKDIR /app

# Copiando o arquivo de requisitos
COPY requirements.txt ./
# Instalando as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiando o restante dos arquivos da aplicação
COPY . .

# Comando para rodar a aplicação
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
