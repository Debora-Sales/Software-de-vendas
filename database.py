import sqlite3
from tkinter import messagebox
import random
from datetime import datetime
import re

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

        # Script 41: A limpeza automática foi removida para garantir a persistência das vendas 
        # realizadas entre diferentes sessões de login (Vendedor -> Administrador).
        
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
            salario REAL,
            email TEXT
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
            distancia TEXT,
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

        # Script 33: Tabela de Configuração de Fretes
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS configuracao_frete (
            urgencia TEXT,
            distancia TEXT,
            valor REAL,
            PRIMARY KEY (urgencia, distancia)
        )
        """)

        # Inicializar tabela de fretes com valores padrão se estiver vazia
        cursor.execute("SELECT count(*) FROM configuracao_frete")
        if cursor.fetchone()[0] == 0:
            urgencias = ["Normal", "Urgente", "Crítico"]
            distancias = ["20Km", "50Km", "100Km", "250Km", "500Km", ">500Km"]
            for u in urgencias:
                for d in distancias:
                    # Valores base sugeridos
                    base = 10.0 if u == "Normal" else 20.0 if u == "Urgente" else 35.0
                    mult = 1.0
                    if d == "100Km": mult = 2.0
                    elif d == "250Km": mult = 4.0
                    elif d == "500Km": mult = 8.0
                    elif d == ">500Km": mult = 12.0
                    cursor.execute("INSERT INTO configuracao_frete VALUES (?, ?, ?)", (u, d, base * mult))

        # Script 34: Inicialização de Perfis de Usuário (Administrador, Vendedor e Estoquista)
        usuarios_iniciais = [
            ("Admin", "Admin123", "Administrador"),
            ("Vendedor", "Vendedor123", "Vendedor"),
            ("Estoquista", "Estoquista123", "Estoquista")
        ]

        for login, senha, tipo in usuarios_iniciais:
            cursor.execute("SELECT * FROM usuarios WHERE nome = ?", (login,))
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO usuarios (nome, senha, tipo) VALUES (?, ?, ?)",
                    (login, senha, tipo)
                )

        # Garantir que a tabela de vendedores existe (evitar conflito com versões antigas)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendedores (
            barcode TEXT PRIMARY KEY,
            nome TEXT NOT NULL
        )""")

        # Inserir um vendedor padrão para teste se não houver nenhum
        try:
            cursor.execute("SELECT count(*) FROM vendedores")
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO vendedores (barcode, nome) VALUES (?, ?)", ("12345", "Vendedor Padrão"))
                cursor.execute("INSERT INTO vendedores (barcode, nome) VALUES (?, ?)", ("54321", "Vendedor Premium"))
        except sqlite3.OperationalError:
            # Caso a tabela vendedores esteja com nome errado ou corrompida
            pass

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
        if "distancia" not in colunas:
            cursor.execute("ALTER TABLE vendas ADD COLUMN distancia TEXT")
        if "forma_pagamento" not in colunas:
            cursor.execute("ALTER TABLE vendas ADD COLUMN forma_pagamento TEXT")

        # Script 41: Migração para adicionar e-mail aos funcionários se não existir
        cursor.execute("PRAGMA table_info(funcionarios)")
        colunas_func = [info[1] for info in cursor.fetchall()]
        if "email" not in colunas_func:
            cursor.execute("ALTER TABLE funcionarios ADD COLUMN email TEXT")

        # Script 41: Seed de dados realistas (Produtos, Clientes e Vendas para contexto)
        cursor.execute("SELECT count(*) FROM produtos")
        if cursor.fetchone()[0] == 0:
            # Script 41: Produtos com preços reais (Ex: Custo 1.00 -> Venda 2.00)
            prods = [
                ("Detergente Neutro 500ml", "31/12/2026", 85, "Limpeza", "99", 1.00, 2.00, 20),
                ("Desinfetante Lavanda 2L", "15/06/2027", 40, "Limpeza", "102", 3.50, 8.50, 20),
                ("Água Sanitária 1L", "20/08/2026", 60, "Higiene", "55", 1.50, 4.00, 20),
                ("Multiuso Tradicional", "10/01/2027", 30, "Limpeza", "22", 2.50, 5.50, 20)
            ]
            cursor.executemany("""
                INSERT INTO produtos (nome, validade, quantidade, categoria, lote, preco_custo, preco_venda, estoque_minimo) 
                VALUES (?,?,?,?,?,?,?,?)
            """, prods)
            
            # Cliente para amostra contextual
            cursor.execute("SELECT count(*) FROM clientes")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO clientes (nome, endereco, telefone, email) 
                    VALUES (?,?,?,?)
                """, ("Limpeza Total Ltda", "Rua das Flores, 123, Centro, São Paulo - Bloco B", "(11) 97777-6666", "vendas@limpezatotal.com.br"))
                id_cli = cursor.lastrowid
                
                # Histórico de venda realista para alimentar Dashboard/Relatórios
                hoje = datetime.now().strftime("%d/%m/%Y %H:%M")
                cursor.execute("""
                    INSERT INTO vendas (id_vendedor, id_cliente, data_venda, valor_total, valor_frete, forma_pagamento, status_entrega, tipo_venda, urgencia, distancia) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, ("12345", id_cli, hoje, 50.00, 10.00, "À Vista", "Entregue", "Entrega", "Normal", "20Km"))
                id_v = cursor.lastrowid
                
                # Itens da venda para compor o lucro
                cursor.execute("""
                    INSERT INTO itens_venda (id_venda, id_produto, quantidade, preco_unitario) 
                    VALUES (?,?,?,?)
                """, (id_v, 1, 20, 2.50))

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
        # Script 36: Regra de Bloqueio de Cadastro Retroativo
        try:
            # Script 41: Validação de Limites (Estoque, Mínimo e Lote)
            if int(quantidade) > 100 or int(estoque_minimo) > 100:
                return None
            
            if lote and len(str(lote)) > 10:
                return None

            # Script 41: Arredondamento para evitar decimais infinitos no SQLite
            preco_custo = round(float(preco_custo), 2)
            preco_venda = round(float(preco_venda), 2)

            # Script 41: Ajuste de preço irreal (Venda deve ser > Custo e ambos > 0)
            if float(preco_custo) <= 0 or float(preco_venda) <= float(preco_custo):
                return None

            val_dt = datetime.strptime(validade, "%d/%m/%Y").date()
            if val_dt < datetime.now().date():
                return None
        except ValueError:
            pass

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
            return None
    return None

def salvar_cliente(nome, endereco, telefone, cpf, cnpj, razao_social, email):
    conn = conectar()

    # Script 48 (Item 4): Restrição rigorosa para aceitar apenas domínios terminados em .com
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.com$'
    if email and not re.match(email_regex, email):
        return None

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
        # Script 36: Regra de Bloqueio de Atualização Retroativa
        try:
            # Script 41: Validação de Limites (Estoque, Mínimo e Lote)
            if int(quantidade) > 100 or int(estoque_minimo) > 100:
                return False

            if lote and len(str(lote)) > 10:
                return False

            # Script 41: Arredondamento para evitar decimais infinitos
            preco_custo = round(float(preco_custo), 2)
            preco_venda = round(float(preco_venda), 2)

            # Script 41: Ajuste de preço irreal (Venda deve ser > Custo e ambos > 0)
            if float(preco_custo) <= 0 or float(preco_venda) <= float(preco_custo):
                return False

            val_dt = datetime.strptime(validade, "%d/%m/%Y").date()
            if val_dt < datetime.now().date():
                return False
        except ValueError:
            pass

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

    # Script 48 (Item 4): Restrição rigorosa para aceitar apenas domínios terminados em .com
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.com$'
    if email and not re.match(email_regex, email):
        return False

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

def salvar_funcionario(nome, cpf, nascimento, estado_civil, endereco, cargo, salario, email):
    id_gerado = gerar_id_funcionario()
    if id_gerado is None:
        messagebox.showerror("Erro", "Não foi possível gerar um ID único para o funcionário.")
        return None

    # Script 48 (Item 4): Restrição rigorosa para aceitar apenas domínios terminados em .com
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.com$'
    if email and not re.match(email_regex, email):
        return None

    conn = conectar()
    if conn:
        try:
            cursor = conn.cursor()
            comando = """
            INSERT INTO funcionarios (id, nome, cpf, nascimento, estado_civil, endereco, cargo, salario, email)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(comando, (id_gerado, nome, cpf, nascimento, estado_civil, endereco, cargo, salario, email))
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
                    "salario": res[7],
                    "email": res[8]
                }
        except Exception as e:
            messagebox.showerror("Erro SQL", f"Erro ao buscar funcionário: {e}")
    return None

def atualizar_funcionario_db(id_func, nome, cpf, nascimento, estado_civil, endereco, cargo, salario, email): # Atualiza por ID
    # Script 48 (Item 4): Restrição rigorosa para aceitar apenas domínios terminados em .com
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.com$'
    if email and not re.match(email_regex, email):
        return False

    conn = conectar()
    if conn:
        try:
            cursor = conn.cursor()
            comando = """
            UPDATE funcionarios SET
                nome=?, cpf=?, nascimento=?, estado_civil=?, endereco=?, cargo=?, salario=?, email=?
            WHERE id=?
            """
            cursor.execute(comando, (nome, cpf, nascimento, estado_civil, endereco, cargo, salario, email, id_func))
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

def buscar_valor_frete_db(urgencia, distancia):
    """Busca o valor configurado para a combinação de urgência e distância."""
    conn = conectar()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT valor FROM configuracao_frete WHERE urgencia = ? AND distancia = ?", (urgencia, distancia))
        res = cursor.fetchone()
        conn.close()
        return res[0] if res else 0.0
    return 0.0

def obter_tabela_fretes_db():
    """Retorna todas as configurações de frete."""
    conn = conectar()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT urgencia, distancia, valor FROM configuracao_frete ORDER BY urgencia, distancia")
        res = cursor.fetchall()
        conn.close()
        return res
    return []

def salvar_configuracao_frete_db(urgencia, distancia, valor):
    """Atualiza o valor de um frete específico."""
    conn = conectar()
    if conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE configuracao_frete SET valor = ? WHERE urgencia = ? AND distancia = ?", (valor, urgencia, distancia))
        conn.commit()
        conn.close()
        return True
    return False

def registrar_venda_db(id_vendedor, id_cliente, valor_total, valor_frete, forma_pagamento, tipo_venda, urgencia, distancia, itens):
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
                INSERT INTO vendas (id_vendedor, id_cliente, data_venda, valor_total, valor_frete, forma_pagamento, status_entrega, tipo_venda, urgencia, distancia) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (id_vendedor, id_cliente, data_venda, valor_total, valor_frete, forma_pagamento, 'Pendente', tipo_venda, urgencia, distancia))
            
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
            print(f"ERRO AO REGISTRAR VENDA NO BANCO: {e}")
            conn.rollback()
            conn.close()
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

def obter_ranking_produtos_db():
    """Script 37: Retorna o ranking dos produtos mais vendidos."""
    conn = conectar()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.nome, SUM(iv.quantidade) as total 
            FROM itens_venda iv 
            JOIN produtos p ON iv.id_produto = p.id 
            GROUP BY p.id 
            ORDER BY total DESC 
            LIMIT 5
        """)
        res = cursor.fetchall()
        conn.close()
        return res
    return []

def obter_estoque_baixo_db():
    """Script 37: Retorna os produtos com menor quantidade em estoque."""
    conn = conectar()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT nome, quantidade, estoque_minimo 
            FROM produtos 
            ORDER BY quantidade ASC 
            LIMIT 5
        """)
        res = cursor.fetchall()
        conn.close()
        return res
    return []

def obter_ranking_vendedores_dia_db():
    """Script 39: Retorna o ranking de faturamento por vendedor no dia atual."""
    conn = conectar()
    if conn:
        cursor = conn.cursor()
        hoje = datetime.now().strftime("%d/%m/%Y")
        cursor.execute("""
            SELECT IFNULL(vended.nome, 'Desconhecido'), SUM(v.valor_total) as total 
            FROM vendas v 
            LEFT JOIN vendedores vended ON v.id_vendedor = vended.barcode 
            WHERE substr(v.data_venda, 1, 10) = ? 
            GROUP BY v.id_vendedor 
            ORDER BY total DESC 
            LIMIT 5
        """, (hoje,))
        res = cursor.fetchall()
        conn.close()
        return res
    return []

def obter_ranking_vendedores_db():
    """Script 37: Retorna o ranking de faturamento por vendedor no mês atual."""
    conn = conectar()
    if conn:
        cursor = conn.cursor()
        mes_atual = datetime.now().strftime("%m/%Y")
        cursor.execute("""
            SELECT IFNULL(vended.nome, 'Desconhecido'), SUM(v.valor_total) as total 
            FROM vendas v 
            LEFT JOIN vendedores vended ON v.id_vendedor = vended.barcode 
            WHERE substr(v.data_venda, 4, 7) = ? 
            GROUP BY v.id_vendedor 
            ORDER BY total DESC 
            LIMIT 5
        """, (mes_atual,))
        res = cursor.fetchall()
        conn.close()
        return res
    return []

def obter_ranking_vendedores_semestre_db():
    """Script 39: Retorna o ranking de faturamento por vendedor no semestre atual."""
    conn = conectar()
    if conn:
        cursor = conn.cursor()
        agora = datetime.now()
        ano_atual = agora.strftime("%Y")
        # Define o intervalo do semestre: 1 (Jan-Jun) ou 2 (Jul-Dez)
        mes_inicio, mes_fim = (1, 6) if agora.month <= 6 else (7, 12)
        
        cursor.execute("""
            SELECT IFNULL(vended.nome, 'Desconhecido'), SUM(v.valor_total) as total 
            FROM vendas v 
            LEFT JOIN vendedores vended ON v.id_vendedor = vended.barcode 
            WHERE substr(v.data_venda, 7, 4) = ? -- Filtra o Ano
              AND CAST(substr(v.data_venda, 4, 2) AS INTEGER) BETWEEN ? AND ? -- Filtra o Semestre
            GROUP BY v.id_vendedor 
            ORDER BY total DESC 
            LIMIT 5
        """, (str(ano_atual), mes_inicio, mes_fim))
        res = cursor.fetchall()
        conn.close()
        return res
    return []

def obter_todos_usuarios_db():
    """Script 38: Retorna a lista de todos os usuários para o painel de configurações."""
    conn = conectar()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, senha, tipo FROM usuarios")
        res = cursor.fetchall()
        conn.close()
        return res
    return []

def atualizar_credenciais_usuario_db(id_usuario, novo_nome, nova_senha):
    """Script 38: Permite ao Admin alterar nome e senha de qualquer usuário."""
    conn = conectar()
    if conn:
        try:
            cursor = conn.cursor()
            # Verifica se o novo nome já existe em outro ID para evitar erro de UNIQUE
            cursor.execute("SELECT id FROM usuarios WHERE nome = ? AND id != ?", (novo_nome, id_usuario))
            if cursor.fetchone():
                messagebox.showwarning("Atenção", "Este nome de usuário já está em uso.")
                return False

            cursor.execute("UPDATE usuarios SET nome = ?, senha = ? WHERE id = ?", (novo_nome, nova_senha, id_usuario))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            messagebox.showerror("Erro SQL", f"Erro ao atualizar credenciais: {e}")
    return False

def ajustar_estoque_db(id_produto, quantidade_ajuste):
    """Script 40: Realiza entrada (positivo) ou saída (negativo) manual no estoque."""
    conn = conectar()
    if conn:
        try:
            cursor = conn.cursor()
            # Verifica estoque atual
            cursor.execute("SELECT quantidade FROM produtos WHERE id = ?", (id_produto,))
            res = cursor.fetchone()
            
            if res:
                nova_qtd = res[0] + quantidade_ajuste
                if nova_qtd < 0:
                    return False
                
                # Script 41: Trava de Segurança para Limite Máximo
                if nova_qtd > 100:
                    return False

                cursor.execute("UPDATE produtos SET quantidade = ? WHERE id = ?", (nova_qtd, id_produto))
                conn.commit()
                conn.close()
                return True
            else:
                messagebox.showerror("Erro", "Produto não encontrado.")
        except Exception as e:
            messagebox.showerror("Erro SQL", f"Erro ao ajustar estoque: {e}")
    return False

def obter_totais_estoque_db():
    """Script 40: Retorna o total de itens cadastrados e a soma de todas as unidades."""
    conn = conectar()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(id), IFNULL(SUM(quantidade), 0) FROM produtos")
        res = cursor.fetchone()
        conn.close()
        return res if res else (0, 0)
    return (0, 0)

def limpar_historico_vendas_db():
    """Script 41: Apaga todos os registros de vendas e seus respectivos itens."""
    conn = conectar()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM itens_venda")
            cursor.execute("DELETE FROM vendas")
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            messagebox.showerror("Erro SQL", f"Erro ao limpar histórico: {e}")
    return False
