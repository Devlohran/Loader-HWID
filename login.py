import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import subprocess
import ctypes
import os
import re
import socket
import sys
import guardshield

class SistemaLogin:
    def __init__(self):
        # Inicialização da janela principal da aplicação
        self.root = tk.Tk()
        self.root.title("Página de Login")

        # Criação do frame para organizar os widgets
        self.frame = tk.Frame(self.root)
        self.frame.pack(padx=20, pady=20)

        # Widgets para inserção do nome de usuário
        self.label_usuario = tk.Label(self.frame, text="Nome de Usuário:")
        self.label_usuario.grid(row=0, column=0)
        self.entry_usuario = tk.Entry(self.frame)
        self.entry_usuario.grid(row=0, column=1)

        # Checkbox para permitir ao usuário escolher salvar suas credenciais
        self.save_var = tk.BooleanVar()
        self.save_checkbox = ttk.Checkbutton(self.frame, text="Salvar credenciais", variable=self.save_var)
        self.save_checkbox.grid(row=1, columnspan=2, pady=5)

        # Botão para realizar o login
        self.button_login = tk.Button(self.frame, text="Login", command=self.fazer_login)
        self.button_login.grid(row=2, columnspan=2, pady=10)

    def verificar_privilegios_admin(self):
        """Verifica se o script está sendo executado com privilégios de administrador."""
        try:
            if not ctypes.windll.shell32.IsUserAnAdmin():
                messagebox.showinfo("Aviso", "Este script requer privilégios de administrador para ser executado.")
                script = os.path.abspath(sys.argv[0])
                if not sys.argv[-1].endswith('pyw'):
                    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}"', None, 1)
                sys.exit(0)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao verificar privilégios de administrador: {e}")
            sys.exit(1)

    def debugger_detected(self):
        """Função a ser chamada em caso de detecção de debugger."""
        self.module.force_kill()
        self.root.destroy()

    def conectar_bd(self):
        """Conecta-se ao banco de dados SQLite."""
        conn = sqlite3.connect('registros.db')
        return conn

    def fechar_conexao_bd(self, conn):
        """Fecha a conexão com o banco de dados."""
        try:
            if conn:
                conn.close()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao fechar conexão com o banco de dados: {e}")

    def get_ip_address(self):
        """Obtém o endereço IP do sistema."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip_address = s.getsockname()[0]
            s.close()
            return ip_address
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao obter o endereço IP: {e}")
            self.root.destroy()
            return None

    def get_system_info(self):
        """Obtém informações do sistema, como endereço IP, número de série do disco rígido, etc."""
        ids = {}
        ids["endereco_ip"] = self.get_ip_address()
        commands = {
            "disco_rigido": 'wmic diskdrive get serialnumber',
            "cpu": 'wmic cpu get ProcessorId',
            "ram": 'wmic memorychip get serialnumber',
            "placa_video": 'wmic path win32_VideoController get name',
            "placa_rede": 'wmic nic get macaddress',
            "sistema_operacional": 'wmic os get serialnumber'
        }

        for name, command in commands.items():
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            output, _ = process.communicate()
            output_cleaned = re.sub(r'\s+', ' ', output.decode('utf-8')).strip()
            ids[name] = output_cleaned

        return ids

    def verificar_e_obter_ids_sistema(self, nome_usuario):
        """Verifica e obtém os HWID do sistema associados ao usuário."""
        conn = self.conectar_bd()
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT IP, disco_rigido, cpu, ram, placa_video, placa_rede, sistema_operacional FROM ids WHERE id_usuario = (SELECT id FROM usuarios WHERE nome = ?)', (nome_usuario,))
            usuario_ids = cursor.fetchone()

            if not usuario_ids:
                messagebox.showinfo("Aviso", "Pegando os HWID do sistema pela primeira vez...")
                ids = self.get_system_info()
                id_usuario = cursor.execute('SELECT id FROM usuarios WHERE nome = ?', (nome_usuario,)).fetchone()
                if id_usuario:
                    id_usuario = id_usuario[0]
                    self.inserir_ids_sistema(cursor, id_usuario, ids)
                    cursor.execute('SELECT IP, disco_rigido, cpu, ram, placa_video, placa_rede, sistema_operacional FROM ids WHERE id_usuario = ?', (id_usuario,))
                    usuario_ids = cursor.fetchone()
                    if usuario_ids:
                        messagebox.showinfo("Aviso", "HWID do sistema foram inseridos com sucesso.")
                    else:
                        messagebox.showerror("Erro", "Erro ao inserir HWID do sistema.")
                        self.root.destroy()

            return usuario_ids
        finally:
            self.fechar_conexao_bd(conn)  # Fechar a conexão com o banco de dados após o uso

    def inserir_ids_sistema(self, cursor, id_usuario, ids):
        """Insere os IDs do sistema na tabela do banco de dados."""
        try:
            cursor.execute('''
                INSERT INTO ids (id_usuario, IP, disco_rigido, cpu, ram, placa_video, placa_rede, sistema_operacional)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (id_usuario, ids.get("endereco_ip", ""), ids.get("disco_rigido", ""), ids.get("cpu", ""), ids.get("ram", ""), ids.get("placa_video", ""), ids.get("placa_rede", ""), ids.get("sistema_operacional", "")))
            cursor.connection.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao inserir HWID do sistema: {e}")
            self.root.destroy()

    def fazer_login(self):
        """Realiza o processo de login."""
        nome_usuario = self.entry_usuario.get()

        if not self.verificar_usuario_existente(nome_usuario):
            messagebox.showerror("Erro", "Usuário não encontrado. Login falhou.")
            self.root.destroy()
            return

        usuario_ids = self.verificar_e_obter_ids_sistema(nome_usuario)

        if usuario_ids:
            ids_banco = self.obter_ids_do_banco(nome_usuario)
            if usuario_ids == ids_banco:
                messagebox.showinfo("Aviso", "Login bem-sucedido!")
                if self.save_var.get():  # Verificar se o usuário deseja salvar suas credenciais
                    self.salvar_usuario(nome_usuario)  # Salvar usuário após o login bem-sucedido
                self.root.destroy()  # Fechar a janela de login após o login bem-sucedido
                #coloque aqui sua aplicacao!!!
            else:
                messagebox.showerror("Erro", "HWID do sistema não correspondem aos armazenados no banco de dados. Login falhou.")
                self.root.destroy()
        else:
            messagebox.showerror("Erro", "HWID do sistema não encontrados. Login falhou.")
            self.root.destroy()

    def obter_ids_do_banco(self, nome_usuario):
        """Obtém os HWID do sistema armazenados no banco de dados."""
        conn = self.conectar_bd()
        cursor = conn.cursor()

        cursor.execute('SELECT IP, disco_rigido, cpu, ram, placa_video, placa_rede, sistema_operacional FROM ids WHERE id_usuario = (SELECT id FROM usuarios WHERE nome = ?)', (nome_usuario,))
        usuario_ids = cursor.fetchone()

        self.fechar_conexao_bd(conn)  # Fechar a conexão com o banco de dados após o uso

        return usuario_ids

    def verificar_usuario_existente(self, nome_usuario):
        """Verifica se o usuário existe no banco de dados."""
        conn = self.conectar_bd()
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM usuarios WHERE nome = ?', (nome_usuario,))
        count = cursor.fetchone()[0]

        self.fechar_conexao_bd(conn)  # Fechar a conexão com o banco de dados após o uso

        return count > 0

    def salvar_usuario(self, nome_usuario):
        """Salva o nome de usuário em um arquivo 'login.cfg'."""
        try:
            os.makedirs("C:/seu_loader", exist_ok=True)
            with open("C:/seu_loader/login.cfg", "w") as f:
                f.write(nome_usuario)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar usuário: {e}")

    def fazer_login_automatico(self):
        """Faz login automático se o arquivo 'login.cfg' existir."""
        try:
            with open("C:/seu_loader/login.cfg", "r") as f:
                nome_usuario = f.read().strip()
                if nome_usuario:
                    self.entry_usuario.insert(0, nome_usuario)
                    self.fazer_login()
        except FileNotFoundError:
            pass  # O arquivo 'login.cfg' ainda não existe, portanto, não há necessidade de fazer login automático

    def run(self):
        """Método principal para iniciar a aplicação."""
        self.verificar_privilegios_admin()
        self.fazer_login_automatico()  # Verificar se há login automático ao iniciar a aplicação
        self.module = guardshield.Security(
            anti_debugger=True,
            kill_on_debug=True,
            detect_vm=True,
            detect_sandbox=True,
            on_detection=self.debugger_detected
        )
        self.module.check_security()
        self.root.mainloop()

if __name__ == "__main__":
    app = SistemaLogin()
    app.run()
