import sqlite3
from tkinter import messagebox

DB_NAME = "xo_sujeira.db"


def conectar():
    try:
        return sqlite3.connect(DB_NAME)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao conectar ao banco: {e}")
        return None


def criar_tabelas():
    conn = conectar()

    if conn:
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL,
            tipo TEXT NOT NULL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            endereco TEXT NOT NULL,
            telefone TEXT NOT NULL,
            cpf TEXT,
            cnpj TEXT,
            razao_social TEXT,
            email TEXT
        )
        """)

        cursor.execute("SELECT * FROM usuarios WHERE nome = ?", ("admin",))

        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO usuarios (nome, senha, tipo) VALUES (?, ?, ?)",
                ("admin", "admin123", "Administrador")
            )

        conn.commit()
        conn.close()


def realizar_login(login_digitado, senha_digitada):
    conn = conectar()

    if conn:
        cursor = conn.cursor()

        comando = "SELECT tipo FROM usuarios WHERE nome = ? AND senha = ?"

        cursor.execute(comando, (login_digitado, senha_digitada))

        resultado = cursor.fetchone()

        conn.close()

        return resultado

    return None


def salvar_cliente(nome, endereco, telefone, cpf, cnpj, razao_social, email):
    conn = conectar()

    if conn:
        try:
            cursor = conn.cursor()

            comando = """
            INSERT INTO clientes (
                nome,
                endereco,
                telefone,
                cpf,
                cnpj,
                razao_social,
                email
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """

            cursor.execute(comando, (
                nome,
                endereco,
                telefone,
                cpf,
                cnpj,
                razao_social,
                email
            ))

            conn.commit()

            id_gerado = cursor.lastrowid

            conn.close()

            return id_gerado

        except Exception as e:
            messagebox.showerror("Erro SQL", f"Erro ao salvar cliente: {e}")
            return None

    return None


def buscar_cliente_por_id(id_cliente):
    conn = conectar()

    if conn:
        try:
            cursor = conn.cursor()

            comando = """
            SELECT id, nome, endereco, telefone, cpf, cnpj, razao_social, email
            FROM clientes
            WHERE id = ?
            """

            cursor.execute(comando, (id_cliente,))

            resultado = cursor.fetchone()

            conn.close()

            if resultado:
                return {
                    "id": resultado[0],
                    "nome": resultado[1],
                    "endereco": resultado[2],
                    "telefone": resultado[3],
                    "cpf": resultado[4],
                    "cnpj": resultado[5],
                    "razao_social": resultado[6],
                    "email": resultado[7]
                }

            return None

        except Exception as e:
            messagebox.showerror("Erro SQL", f"Erro ao buscar cliente: {e}")
            return None

    return None
