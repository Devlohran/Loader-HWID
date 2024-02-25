import sqlite3
import datetime
import time

# Função para conectar ao banco de dados
def conectar_bd():
    conn = sqlite3.connect('registros.db')
    return conn

# Função para remover chave expirada e registros relacionados
def remover_chave_expirada(chave_id):
    conn = conectar_bd()
    cursor = conn.cursor()
    try:
        cursor.execute('PRAGMA foreign_keys = OFF')
        cursor.execute('SELECT id_usuario FROM chaves WHERE id=?', (chave_id,))
        usuario_id = cursor.fetchone()[0]
        cursor.execute('DELETE FROM chaves WHERE id=?', (chave_id,))
        cursor.execute('SELECT id FROM chaves ORDER BY id')
        chaves_restantes = cursor.fetchall()
        for idx, chave in enumerate(chaves_restantes, start=1):
            cursor.execute('UPDATE chaves SET id=? WHERE id=?', (idx, chave[0]))
        cursor.execute('SELECT id FROM chaves WHERE id_usuario=?', (usuario_id,))
        outras_chaves = cursor.fetchall()
        if not outras_chaves:
            cursor.execute('DELETE FROM usuarios WHERE id=?', (usuario_id,))
        cursor.execute('DELETE FROM ids WHERE id_usuario=?', (usuario_id,))
        cursor.execute('PRAGMA foreign_keys = ON')
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# Função para verificar e remover chaves expiradas
def verificar_chaves_expiradas():
    conn = conectar_bd()
    cursor = conn.cursor()

    # Obter a data e hora atual
    agora = datetime.datetime.now()

    # Converter para string no formato que você está usando para 'expiracao'
    agora_str = agora.strftime('%Y-%m-%d %H:%M:%S')

    # Executar a consulta para obter chaves expiradas
    cursor.execute('SELECT id FROM chaves WHERE expiracao < ?', (agora_str,))
    chaves_expiradas = cursor.fetchall()

    # Remover chaves expiradas
    for chave in chaves_expiradas:
        chave_id = chave[0]
        remover_chave_expirada(chave_id)

    conn.close()

# Função para iniciar o sistema de remoção de chaves expiradas
def iniciar_sistema():
    while True:
        verificar_chaves_expiradas()
        # Aguardar um minuto antes de verificar novamente
        time.sleep(60)

# Executar a inicialização do sistema
iniciar_sistema()
