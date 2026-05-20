import sqlite3
from tkinter import messagebox
import random
from datetime import datetime

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
        
        # Sprint 14 & 16: Tabela de Funcionários
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS funcionarios (
            id INTEGER PRIMARY KEY, -- Script 15: ID de 5 números aleatórios
            nome TEXT NOT NULL,
            cpf TEXT NOT NULL,
            nascimento TEXT,
            estado_civil TEXT,
            endereco TEXT,
            cargo TEXT,
            salario REAL
        )
        """)

        # Tabelas de Vendas e Vendedores
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendedores (
            barcode TEXT PRIMARY KEY,
            nome TEXT NOT NULL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_vendedor TEXT,
            id_cliente INTEGER,
            data_venda TEXT,
            valor_total REAL,
            valor_frete REAL DEFAULT 0,
            status_entrega TEXT DEFAULT 'Pendente',
            tipo_venda TEXT DEFAULT 'Retirada',
            urgencia TEXT DEFAULT 'Normal',
            forma_pagamento TEXT, 
            FOREIGN KEY (id_vendedor) REFERENCES vendedores(barcode), 
            FOREIGN KEY (id_cliente) REFERENCES clientes(id)
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS itens_venda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_venda INTEGER,
            id_produto INTEGER,
            quantidade INTEGER,
            preco_unitario REAL,
            FOREIGN KEY (id_venda) REFERENCES vendas(id),
            FOREIGN KEY (id_produto) REFERENCES produtos(id)
        )
        """)

        cursor.execute("SELECT * FROM usuarios WHERE nome = ?", ("admin",))

        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO usuarios (nome, senha, tipo) VALUES (?, ?, ?)",
                ("admin", "admin123", "Administrador")
            )

        # Inserir um vendedor padrão para teste se não houver nenhum
        cursor.execute("SELECT count(*) FROM vendedores")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO vendedores (barcode, nome) VALUES (?, ?)", ("12345", "Vendedor Padrão"))
            cursor.execute("INSERT INTO vendedores (barcode, nome) VALUES (?, ?)", ("54321", "Vendedor Premium"))

        # Migração: Garante que as novas colunas de logística existam em bancos de dados antigos
        cursor.execute("PRAGMA table_info(vendas)")
        colunas = [info[1] for info in cursor.fetchall()]
        
        if "valor_frete" not in colunas:
            cursor.execute("ALTER TABLE vendas ADD COLUMN valor_frete REAL DEFAULT 0")
        if "status_entrega" not in colunas:
            cursor.execute("ALTER TABLE vendas ADD COLUMN status_entrega TEXT DEFAULT 'Pendente'")
        if "tipo_venda" not in colunas:
            cursor.execute("ALTER TABLE vendas ADD COLUMN tipo_venda TEXT DEFAULT 'Retirada'")
        if "urgencia" not in colunas:
            cursor.execute("ALTER TABLE vendas ADD COLUMN urgencia TEXT DEFAULT 'Normal'")

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

# --- FUNÇÕES PARA FUNCIONÁRIOS (Sprints 14, 15, 16) ---

def gerar_id_funcionario():
    """Script 15: Gera um ID de 5 números aleatórios que não se repete."""
    conn = conectar()
    if conn:
        cursor = conn.cursor()
        while True:
            novo_id = random.randint(10000, 99999)
            cursor.execute("SELECT id FROM funcionarios WHERE id = ?", (novo_id,))
            if not cursor.fetchone():
                conn.close()
                return novo_id
    return None

def salvar_funcionario(nome, cpf, nascimento, estado_civil, endereco, cargo, salario):
    id_gerado = gerar_id_funcionario()
    if id_gerado is None:
        messagebox.showerror("Erro", "Não foi possível gerar um ID único para o funcionário.")
        return None
    conn = conectar()
    if conn:
        try:
            cursor = conn.cursor()
            comando = """
            INSERT INTO funcionarios (id, nome, cpf, nascimento, estado_civil, endereco, cargo, salario)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(comando, (id_gerado, nome, cpf, nascimento, estado_civil, endereco, cargo, salario))
            conn.commit()
            conn.close()
            return id_gerado
        except Exception as e:
            messagebox.showerror("Erro SQL", f"Erro ao salvar funcionário: {e}")
            return None
    return None

def buscar_funcionario_por_id_func(id_func): # Busca por ID
    conn = conectar()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM funcionarios WHERE id = ?", (id_func,))
            res = cursor.fetchone()
            conn.close()
            if res:
                return {
                    "id": res[0],
                    "nome": res[1],
                    "cpf": res[2],
                    "nascimento": res[3],
                    "estado_civil": res[4],
                    "endereco": res[5],
                    "cargo": res[6],
                    "salario": res[7]
                }
        except Exception as e:
            messagebox.showerror("Erro SQL", f"Erro ao buscar funcionário: {e}")
    return None

def atualizar_funcionario_db(id_func, nome, cpf, nascimento, estado_civil, endereco, cargo, salario): # Atualiza por ID
    conn = conectar()
    if conn:
        try:
            cursor = conn.cursor()
            comando = """
            UPDATE funcionarios SET
                nome=?, cpf=?, nascimento=?, estado_civil=?, endereco=?, cargo=?, salario=?
            WHERE id=?
            """
            cursor.execute(comando, (nome, cpf, nascimento, estado_civil, endereco, cargo, salario, id_func))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            messagebox.showerror("Erro SQL", f"Erro ao atualizar funcionário: {e}")
    return False

def deletar_funcionario_db(id_func): # Deleta por ID
    conn = conectar()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM funcionarios WHERE id = ?", (id_func,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            messagebox.showerror("Erro SQL", f"Erro ao excluir funcionário: {e}")
    return False

def buscar_vendedor_por_barcode(barcode):
    conn = conectar()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT nome FROM vendedores WHERE barcode = ?", (barcode,))
        res = cursor.fetchone()
        conn.close()
        return res[0] if res else None
    return None

def registrar_venda_db(id_vendedor, id_cliente, valor_total, valor_frete, forma_pagamento, tipo_venda, urgencia, itens):
    """
    itens: lista de dicionarios [{'id_prod': 1, 'qnt': 2, 'preco': 10.0}, ...]
    """
    conn = conectar()
    if conn:
        try:
            cursor = conn.cursor()
            data_venda = datetime.now().strftime("%d/%m/%Y %H:%M")
            
            # 1. Registrar a Venda
            cursor.execute("""
                INSERT INTO vendas (id_vendedor, id_cliente, data_venda, valor_total, valor_frete, forma_pagamento, status_entrega, tipo_venda, urgencia) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (id_vendedor, id_cliente, data_venda, valor_total, valor_frete, forma_pagamento, 'Pendente', tipo_venda, urgencia))
            
            id_venda = cursor.lastrowid

            # 2. Registrar itens e baixar estoque
            for item in itens:
                # Verificar validade e estoque novamente por segurança (RN01 e RN05)
                cursor.execute("SELECT quantidade, validade FROM produtos WHERE id = ?", (item['id_prod'],))
                prod_data = cursor.fetchone()
                
                if prod_data[0] < item['qnt']:
                    raise Exception(f"Estoque insuficiente para o produto ID {item['id_prod']}")
                
                # Registro do item
                cursor.execute("""
                    INSERT INTO itens_venda (id_venda, id_produto, quantidade, preco_unitario)
                    VALUES (?, ?, ?, ?)
                """, (id_venda, item['id_prod'], item['qnt'], item['preco']))

                # Baixa no estoque
                cursor.execute("""
                    UPDATE produtos SET quantidade = quantidade - ? WHERE id = ?
                """, (item['qnt'], item['id_prod']))

            conn.commit()
            conn.close()
            return id_venda
        except Exception as e:
            conn.rollback()
            conn.close()
            messagebox.showerror("Erro na Venda", str(e))
            return None
    return None

def obter_vendas_por_vendedor():
    """Extrai o total vendido por cada vendedor para cálculo de comissões."""
    conn = conectar()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    IFNULL(vended.nome, 'Vendedor não Cadastrado'), 
                    SUM(ven.valor_total) 
                FROM vendas ven
                LEFT JOIN vendedores vended ON ven.id_vendedor = vended.barcode
                GROUP BY vended.nome
            """)
            res = cursor.fetchall()
            conn.close()
            return res
        except Exception as e:
            print(f"ERRO COMISSÕES: {e}")
    return []

def obter_relatorio_lucro_db():
    """Calcula a margem de lucro por produto baseando-se nas vendas realizadas."""
    conn = conectar()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    p.nome, 
                    SUM(iv.quantidade), 
                    SUM(iv.quantidade * iv.preco_unitario), 
                    SUM(iv.quantidade * IFNULL(p.preco_custo, 0))
                FROM itens_venda iv
                JOIN produtos p ON iv.id_produto = p.id
                GROUP BY p.nome
            """)
            res = cursor.fetchall()
            conn.close()
            return res
        except Exception as e:
            print(f"ERRO LUCRO: {e}")
    return []

def obter_historico_vendas_db():
    """Retorna uma lista resumida das últimas vendas."""
    conn = conectar()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    ven.id, 
                    IFNULL(vended.nome, 'Vendedor não Cadastrado'), 
                    IFNULL(cli.nome, 'Cliente não Identificado'), 
                    ven.data_venda, 
                    ven.valor_total,
                    IFNULL(ven.forma_pagamento, 'N/A'),
                    ven.tipo_venda,
                    ven.urgencia,
                    ven.status_entrega
                FROM vendas ven 
                LEFT JOIN vendedores vended ON ven.id_vendedor = vended.barcode
                LEFT JOIN clientes cli ON ven.id_cliente = cli.id
                ORDER BY ven.id DESC
            """)
            res = cursor.fetchall()
            conn.close()
            return res
        except Exception as e:
            print(f"ERRO HISTORICO: {e}")
    return []

def obter_entregas_pendentes_db():
    """Retorna vendas do tipo Entrega que não foram finalizadas, ordenadas por urgência."""
    conn = conectar()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    ven.id, 
                    cli.nome, 
                    cli.endereco, 
                    ven.urgencia, 
                    ven.status_entrega
                FROM vendas ven
                JOIN clientes cli ON ven.id_cliente = cli.id
                WHERE ven.tipo_venda = 'Entrega' AND ven.status_entrega != 'Entregue'
                ORDER BY 
                    CASE ven.urgencia 
                        WHEN 'Crítico' THEN 1 
                        WHEN 'Urgente' THEN 2 
                        ELSE 3 
                    END, ven.id ASC
            """)
            res = cursor.fetchall()
            conn.close()
            return res
        except Exception as e:
            print(f"ERRO LOGISTICA: {e}")
    return []

def atualizar_status_entrega_db(id_venda, novo_status):
    """Atualiza o status de entrega de uma venda específica."""
    conn = conectar()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE vendas SET status_entrega = ? WHERE id = ?", (novo_status, id_venda))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            messagebox.showerror("Erro SQL", f"Erro ao atualizar status: {e}")
    return False
