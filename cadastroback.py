from flask import Flask, request, jsonify, render_template, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'sua senha')  # Definir uma chave secreta a partir de uma variável de ambiente

# Função para conectar ao banco de dados
def conectar_bd():
    conn = sqlite3.connect('registros.db')
    return conn

# Gerar e armazenar um token CSRF exclusivo para cada sessão de usuário
@app.before_request
def gerar_token_csrf():
    if 'csrf_token' not in session:
        session['csrf_token'] = os.urandom(24).hex()

# Rota para renderizar o formulário de cadastro de usuário
@app.route('/')
def formulario_cadastro():
    return render_template('cadastrofront.html', csrf_token=session['csrf_token'])

# Rota para cadastro de usuário com a chave
@app.route('/cadastrar_usuario', methods=['POST'])
def cadastrar_usuario():
    dados_requisicao = request.json
    chave = dados_requisicao.get('chave')
    nome = dados_requisicao.get('nome')
    token_csrf = request.headers.get('X-CSRFToken')  # Recuperar o token CSRF da solicitação

    # Verificar se o token CSRF enviado pelo cliente corresponde ao token da sessão
    if token_csrf != session['csrf_token']:
        return jsonify({'success': False, 'error': 'Token CSRF inválido.'}), 403

    conn = conectar_bd()
    cursor = conn.cursor()

    # Verificar se a chave é válida e não foi usada
    cursor.execute('SELECT id FROM chaves WHERE chave=? AND id_usuario IS NULL', (chave,))
    chave_id = cursor.fetchone()

    if chave_id:
        # Verificar se o nome já está em uso
        cursor.execute('SELECT id FROM usuarios WHERE nome=?', (nome,))
        usuario_existente = cursor.fetchone()

        if usuario_existente:
            conn.close()
            return jsonify({'success': False, 'error': 'Nome de usuário já está em uso.'}), 400
        else:
            # Inserir usuário
            cursor.execute('INSERT INTO usuarios (nome) VALUES (?)', (nome,))
            usuario_id = cursor.lastrowid

            cursor.execute('UPDATE chaves SET id_usuario=? WHERE id=?', (usuario_id, chave_id[0]))

            conn.commit()
            conn.close()

            return jsonify({'success': True, 'message': 'Usuário cadastrado com sucesso.'}), 200
    else:
        conn.close()
        return jsonify({'success': False, 'error': 'Chave inválida ou já utilizada.'}), 400

if __name__ == '__main__':
    app.run(debug=False, port=666)
