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
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            validade TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            categoria TEXT NOT NULL,
            lote TEXT,
            preco_custo REAL,
            preco_venda REAL,
            estoque_minimo INTEGER
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

def salvar_produto(nome, validade, quantidade, categoria, lote, preco_custo, preco_venda, estoque_minimo):
    conn = conectar()
    if conn:
        try:
            cursor = conn.cursor()
            comando = """
            INSERT INTO produtos (
                nome, validade, quantidade, categoria, lote, preco_custo, preco_venda, estoque_minimo
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(comando, (
                nome,
                validade,
                quantidade,
                categoria,
                lote,
                preco_custo,
                preco_venda,
                estoque_minimo
            ))
            conn.commit()
            id_gerado = cursor.lastrowid
            conn.close()
            return id_gerado
        except Exception as e:
            messagebox.showerror("Erro SQL", f"Erro ao salvar produto: {e}")
            return None
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


def atualizar_produto_db(id_produto, nome, validade, quantidade, categoria, lote, preco_custo, preco_venda, estoque_minimo):
    conn = conectar()
    if conn:
        try:
            cursor = conn.cursor()
            comando = """
            UPDATE produtos SET 
                nome = ?, 
                validade = ?, 
                quantidade = ?, 
                categoria = ?, 
                lote = ?, 
                preco_custo = ?, 
                preco_venda = ?, 
                estoque_minimo = ?
            WHERE id = ?
            """
            cursor.execute(comando, (
                nome,
                validade,
                quantidade,
                categoria,
                lote,
                preco_custo,
                preco_venda,
                estoque_minimo,
                id_produto
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            messagebox.showerror("Erro SQL", f"Erro ao atualizar produto: {e}")
            return False
    return False


def deletar_produto_db(id_produto):
    conn = conectar()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM produtos WHERE id = ?", (id_produto,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            messagebox.showerror("Erro SQL", f"Erro ao excluir produto: {e}")
            return False
    return False


def buscar_produto_por_id(id_produto):
    conn = conectar()
    if conn:
        try:
            cursor = conn.cursor()
            comando = "SELECT * FROM produtos WHERE id = ?"
            cursor.execute(comando, (id_produto,))
            resultado = cursor.fetchone()
            conn.close()

            if resultado:
                return {
                    "id": resultado[0],
                    "nome": resultado[1],
                    "validade": resultado[2],
                    "quantidade": resultado[3],
                    "categoria": resultado[4],
                    "lote": resultado[5],
                    "preco_custo": resultado[6],
                    "preco_venda": resultado[7],
                    "estoque_minimo": resultado[8]
                }
            return None
        except Exception as e:
            messagebox.showerror("Erro SQL", f"Erro ao buscar produto: {e}")
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


def atualizar_cliente_db(id_cliente, nome, endereco, telefone, cpf, cnpj, razao_social, email):
    conn = conectar()
    if conn:
        try:
            cursor = conn.cursor()
            comando = """
            UPDATE clientes SET 
                nome = ?, 
                endereco = ?, 
                telefone = ?, 
                cpf = ?, 
                cnpj = ?, 
                razao_social = ?, 
                email = ?
            WHERE id = ?
            """
            cursor.execute(comando, (nome, endereco, telefone, cpf, cnpj, razao_social, email, id_cliente))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            messagebox.showerror("Erro SQL", f"Erro ao atualizar cliente: {e}")
            return False
    return False


def deletar_cliente_db(id_cliente):
    conn = conectar()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clientes WHERE id = ?", (id_cliente,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            messagebox.showerror("Erro SQL", f"Erro ao excluir cliente: {e}")
            return False
    return False
