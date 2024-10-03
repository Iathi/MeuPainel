# Use uma imagem oficial do Python como base
FROM python:3.9

# Defina o diretório de trabalho dentro do contêiner
WORKDIR /

# Copie os arquivos de dependências para o contêiner
COPY requirements.txt /

# Crie e ative o ambiente virtual e instale as dependências
RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

# Copie o restante da aplicação para o contêiner
COPY . /

# Exponha a porta em que o app Flask ou Quart estará rodando
EXPOSE 5000

# Defina o comando de entrada
CMD ["/opt/venv/bin/python", "app.py"]
