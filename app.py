from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/comando', methods=['POST'])
def executar_comando():
    data = request.json
    comando = data.get('comando')
    resultado = os.popen(comando).read()  # Executa o comando no servidor
    return jsonify({'resultado': resultado})

if __name__ == '__main__':
    app.run(debug=True)