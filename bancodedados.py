import sqlite3

# Função para conectar ao banco de dados
def conectar_bd():
    conn = sqlite3.connect('registros.db')
    return conn

# Criar o banco de dados e as tabelas
def criar_banco():
    conn = conectar_bd()
    cursor = conn.cursor()

    # Criar tabela de usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY,
            nome TEXT
        )
    ''')

    # Criar tabela de chaves
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chaves (
            id INTEGER PRIMARY KEY,
            chave TEXT CHECK(length(chave) = 16),  -- Restrição de tamanho
            expiracao TEXT,
            id_usuario INTEGER,
            FOREIGN KEY(id_usuario) REFERENCES usuarios(id)
        )
    ''')

    # Criar tabela de IDs relacionados aos usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ids (
            id INTEGER PRIMARY KEY,
            id_usuario INTEGER,
            IP TEXT,
            placa_video TEXT,
            disco_rigido TEXT,
            cpu TEXT,
            ram TEXT,
            placa_rede TEXT,
            sistema_operacional TEXT,
            FOREIGN KEY(id_usuario) REFERENCES usuarios(id)
        )
    ''')

    conn.commit()
    conn.close()

# Executar a criação do banco de dados
criar_banco()
