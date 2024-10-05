# Usar uma imagem base do Python
FROM python:3.9

# Definir o diretório de trabalho
WORKDIR /MeuPainel

# Copiar os arquivos requirements.txt para o diretório de trabalho
COPY requirements.txt .

# Instalar as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante do código da aplicação para o diretório de trabalho
COPY . .

# Comando para executar a aplicação
CMD ["python", "app.py"]
