# Use uma imagem oficial do Python como base
FROM python:3.9

# Defina o diretório de trabalho dentro do contêiner
WORKDIR /

# Copie os arquivos de dependências para o contêiner
COPY requirements.txt .

# Crie o ambiente virtual e instale as dependências
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Copie o restante da aplicação para o contêiner
COPY . .

# Exponha a porta em que o app Flask ou Quart estará rodando
EXPOSE 5000

# Defina o comando de entrada para rodar a aplicação
CMD ["/opt/venv/bin/python", "app.py"]
