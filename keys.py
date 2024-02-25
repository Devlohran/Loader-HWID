import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.simpledialog import askinteger
from datetime import datetime, timedelta
import random
import string
import pyperclip

class SistemaChaves:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Gerenciamento de Chaves')

        self.label_duracao = tk.Label(self.root, text='Duração:')
        self.combo_duracao = tk.StringVar(self.root)
        self.combo_duracao.set('Mensal')

        self.menu_duracao = tk.OptionMenu(self.root, self.combo_duracao, 'Semanal', 'Mensal', 'Trimestral', 'Anual',
                                          'Vitalício')
        self.menu_duracao.config(width=20)

        self.button_criar = tk.Button(self.root, text='Criar Chave', command=self.criar_chave)
        self.button_visualizar = tk.Button(self.root, text='Visualizar Chaves', command=self.visualizar_chaves)

        self.label_duracao.grid(row=0, column=0, padx=5, pady=5)
        self.menu_duracao.grid(row=0, column=1, padx=5, pady=5)
        self.button_criar.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='we')
        self.button_visualizar.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky='we')

    def conectar_bd(self):
        conn = sqlite3.connect('registros.db')
        return conn

    def gerar_chave(self):
        caracteres = string.ascii_letters + string.digits
        chave_gerada = ''.join(random.choices(caracteres, k=16))
        return chave_gerada

    def criar_chave(self):
        duracao = self.combo_duracao.get()

        match duracao:
            case 'Semanal':
                duracao_dias = 7
            case 'Mensal':
                duracao_dias = 30
            case 'Trimestral':
                duracao_dias = 90
            case 'Anual':
                duracao_dias = 365
            case 'Vitalício':
                duracao_dias = 36500 #100 anos
            case _:
                raise ValueError("Duração desconhecida")

        chave = self.gerar_chave()
        expiracao = (datetime.now() + timedelta(days=duracao_dias)).strftime('%Y-%m-%d')

        conn = self.conectar_bd()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO chaves (chave, expiracao, id_usuario) VALUES (?, ?, NULL)', (chave, expiracao))
        conn.commit()
        conn.close()

        messagebox.showinfo('Info', 'Chave criada com sucesso.')

    def visualizar_chaves(self):

        def pesquisar_usuario(event=None):
            nome_usuario = entry_usuario.get()
            conn = self.conectar_bd()
            cursor = conn.cursor()
            if nome_usuario:
                cursor.execute('''
                    SELECT chaves.id, chaves.chave, chaves.expiracao, usuarios.nome 
                    FROM chaves 
                    LEFT JOIN usuarios ON chaves.id_usuario = usuarios.id
                    WHERE usuarios.nome LIKE ?
                ''', ('%' + nome_usuario + '%',))
            else:
                cursor.execute('''
                    SELECT chaves.id, chaves.chave, chaves.expiracao, usuarios.nome 
                    FROM chaves 
                    LEFT JOIN usuarios ON chaves.id_usuario = usuarios.id
                ''')
            chaves = cursor.fetchall()
            conn.close()
            self.treeview.delete(*self.treeview.get_children())
            for chave in chaves:
                self.treeview.insert('', 'end', values=chave)

        def apagar_selecionado():
            item = self.treeview.focus()
            if item:
                chave_id = self.treeview.item(item, 'values')[0]
                conn = self.conectar_bd()
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
                    conn.close()
                    messagebox.showinfo('Info', 'Chave e registros relacionados apagados com sucesso.')
                    self.atualizar_tabela()
                except Exception as e:
                    conn.rollback()
                    messagebox.showerror('Erro', f'Ocorreu um erro: {str(e)}')
                    conn.close()

        def copiar_chave():
            item = self.treeview.focus()
            if item:
                chave = self.treeview.item(item, 'values')[1]
                pyperclip.copy(chave)
                messagebox.showinfo('Info', 'Chave copiada para a área de transferência.')

        def visualizar_ids_relacionados():
            item = self.treeview.focus()
            if item:
                chave_id = self.treeview.item(item, 'values')[0]
                conn = self.conectar_bd()
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT 
                        ids.id, 
                        ids.id_usuario, 
                        ids.IP, 
                        ids.placa_video, 
                        ids.disco_rigido, 
                        ids.cpu, 
                        ids.ram, 
                        ids.placa_rede, 
                        ids.sistema_operacional
                    FROM ids
                    INNER JOIN chaves ON chaves.id_usuario = ids.id_usuario
                    WHERE chaves.id = ? 
                ''', (chave_id,))
                ids = cursor.fetchall()
                conn.close()

                info_text = f'IDs relacionados à chave {chave_id}:\n'
                for id_info in ids:
                    info_text += f'ID: {id_info[0]}\n'
                    info_text += f'ID Usuário: {id_info[1]}\n'
                    info_text += f'IP: {id_info[2]}\n'
                    info_text += f'Placa de Vídeo: {id_info[3]}\n'
                    info_text += f'Disco Rígido: {id_info[4]}\n'
                    info_text += f'CPU: {id_info[5]}\n'
                    info_text += f'RAM: {id_info[6]}\n'
                    info_text += f'Placa de Rede: {id_info[7]}\n'
                    info_text += f'Sistema Operacional: {id_info[8]}\n\n'

                messagebox.showinfo('IDs Relacionados', info_text)

        def atualizar_key():
            item = self.treeview.focus()
            if item:
                chave_id = self.treeview.item(item, 'values')[0]
                dias_adicionais = askinteger("Atualizar Key", "Digite a quantidade de dias a serem adicionados:")
                if dias_adicionais is not None:
                    conn = self.conectar_bd()
                    cursor = conn.cursor()
                    try:
                        cursor.execute('SELECT expiracao FROM chaves WHERE id=?', (chave_id,))
                        expiracao_atual = cursor.fetchone()[0]
                        nova_expiracao = (datetime.strptime(expiracao_atual, '%Y-%m-%d') + timedelta(
                            days=dias_adicionais)).strftime('%Y-%m-%d')
                        cursor.execute('UPDATE chaves SET expiracao=? WHERE id=?', (nova_expiracao, chave_id))
                        conn.commit()
                        conn.close()
                        messagebox.showinfo('Info', 'Data de expiração atualizada com sucesso.')
                        self.atualizar_tabela()
                    except Exception as e:
                        conn.rollback()
                        messagebox.showerror('Erro', f'Ocorreu um erro: {str(e)}')
                        conn.close()

        def resetar_ids_relacionados():
            item = self.treeview.focus()
            if item:
                chave_id = self.treeview.item(item, 'values')[0]
                conn = self.conectar_bd()
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE ids
                    SET id_usuario = NULL, IP = NULL, placa_video = NULL, disco_rigido = NULL,
                        cpu = NULL, ram = NULL, placa_rede = NULL, sistema_operacional = NULL
                    WHERE id_usuario = ? 
                ''', (chave_id,))
                conn.commit()
                conn.close()
                messagebox.showinfo('Info', f'HWID relacionados à chave {chave_id} foram resetados com sucesso.')
                self.atualizar_tabela()

        visualizar = tk.Toplevel()
        visualizar.title('Visualizar Chaves')

        search_frame = ttk.Frame(visualizar)
        search_frame.pack(padx=10, pady=10, fill='x')

        label_usuario = ttk.Label(search_frame, text='Pesquisar por nome de usuário:')
        label_usuario.pack(side='left', padx=5, pady=5)

        entry_usuario = ttk.Entry(search_frame, width=30)
        entry_usuario.pack(side='left', padx=5, pady=5)
        entry_usuario.bind('<KeyRelease>', pesquisar_usuario)  # Adicionando o evento de vinculação

        treeframe = ttk.Frame(visualizar)
        treeframe.pack(fill='both', expand=True)

        self.treeview = ttk.Treeview(treeframe, columns=('ID', 'Chave', 'Expiração', 'Usuário'), show='headings', selectmode='extended')
        self.treeview.heading('ID', text='ID')
        self.treeview.heading('Chave', text='Chave')
        self.treeview.heading('Expiração', text='Expiração')
        self.treeview.heading('Usuário', text='Usuário')
        self.treeview.column('Usuário', anchor='center')

        vsb = ttk.Scrollbar(treeframe, orient="vertical", command=self.treeview.yview)
        vsb.pack(side='right', fill='y')
        self.treeview.configure(yscrollcommand=vsb.set)

        self.treeview.pack(fill='both', expand=True)

        btn_apagar = ttk.Button(visualizar, text='Apagar Selecionado', command=apagar_selecionado)
        btn_apagar.pack(side='left', padx=5, pady=5)

        btn_copiar = ttk.Button(visualizar, text='Copiar Chave', command=copiar_chave)
        btn_copiar.pack(side='left', padx=5, pady=5)

        btn_visualizar_ids = ttk.Button(visualizar, text='Visualizar HWID', command=visualizar_ids_relacionados)
        btn_visualizar_ids.pack(side='left', padx=5, pady=5)

        btn_resetar_ids = ttk.Button(visualizar, text='Resetar HWID', command=resetar_ids_relacionados)
        btn_resetar_ids.pack(side='left', padx=5, pady=5)

        btn_atualizar_key = ttk.Button(visualizar, text='Atualizar Key', command=atualizar_key)
        btn_atualizar_key.pack(side='left', padx=5, pady=5)

        self.atualizar_tabela()

    def atualizar_tabela(self):
        self.treeview.delete(*self.treeview.get_children())
        conn = self.conectar_bd()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT chaves.id, chaves.chave, chaves.expiracao, usuarios.nome 
            FROM chaves 
            LEFT JOIN usuarios ON chaves.id_usuario = usuarios.id
        ''')
        chaves = cursor.fetchall()
        conn.close()
        for chave in chaves:
            self.treeview.insert('', 'end', values=chave)

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    app = SistemaChaves()
    app.run()
