import sqlite3
import os
from datetime import datetime

class SistemaXoSujeira:
    def __init__(self, db_name="xo_sujeira.db"):
        self.db_name = db_name
        self.conectar_bd()
        self.inicializar_tabelas()

    def conectar_bd(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def inicializar_tabelas(self):
        """Cria as tabelas baseadas no Diagrama de Relacionamento e Requisitos"""
        
        # Tabela de Usuários (Login único pessoal)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome VARCHAR(100) NOT NULL,
                senha VARCHAR(100) NOT NULL,
                tipo VARCHAR(100) NOT NULL -- Administrador ou Vendedor
            )
        """)

        # Tabela de Produtos (Foco: Gestão de Estoque e Validade)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome VARCHAR(100) NOT NULL,
                quantidade INT DEFAULT 0,
                categoria VARCHAR(100),
                preco_custo DECIMAL(10,2),
                preco_venda DECIMAL(10,2),
                estoque_minimo INT,
                validade DATE,
                lote VARCHAR(50)
            )
        """)

        # Tabela de Vendedores
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendedor (
                id_barcode VARCHAR(50) PRIMARY KEY, -- ID único (Código de Barras) conforme especificação
                nome VARCHAR(100) NOT NULL,
                tel VARCHAR(14),
                email VARCHAR(100)
            )
        """)

        # Tabela de Clientes (Dados obrigatórios: Razão Social/CNPJ/CPF)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome VARCHAR(100) NOT NULL,
                endereco VARCHAR(100),
                telefone VARCHAR(14),
                cpf VARCHAR(11),
                cnpj VARCHAR(14),
                razao_social VARCHAR(100),
                email VARCHAR(100)
            )
        """)

        # Tabela de Vendas
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendas (
                id_venda INTEGER PRIMARY KEY AUTOINCREMENT,
                id_vendedor INTEGER,
                id_cliente INTEGER,
                data_venda DATETIME DEFAULT CURRENT_TIMESTAMP,
                valor_total DECIMAL(10,2),
                valor_frete DECIMAL(10,2),
                FOREIGN KEY (id_vendedor) REFERENCES vendedor(id_barcode),
                FOREIGN KEY (id_cliente) REFERENCES clientes(id)
            )
        """)

        # Tabela Itens da Venda (Apenas unidade)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS itens_vendas (
                id_item INTEGER PRIMARY KEY AUTOINCREMENT,
                id_venda INTEGER,
                id_produto INTEGER,
                qnt INT,
                preco_unitario DECIMAL(10,2),
                FOREIGN KEY (id_venda) REFERENCES vendas(id_venda),
                FOREIGN KEY (id_produto) REFERENCES produtos(id)
            )
        """)

        # Adicionar Usuário Administrador padrão [Solicitação do Usuário]
        self.cursor.execute("SELECT * FROM usuarios WHERE nome = 'admin'")
        if not self.cursor.fetchone():
            self.cursor.execute("INSERT INTO usuarios (nome, senha, tipo) VALUES ('admin', 'admin123', 'Administrador')")
            self.conn.commit()

    # --- Funcionalidades do Sistema ---

    def login(self, usuario, senha):
        """Verifica credenciais [cite: 35]"""
        self.cursor.execute("SELECT tipo FROM usuarios WHERE nome = ? AND senha = ?", (usuario, senha))
        res = self.cursor.fetchone()
        return res[0] if res else None

    def cadastrar_produto(self, nome, validade, qtd, lote, p_custo, p_venda, min_est):
        """RF01: Cadastro com lote e validade."""
        query = "INSERT INTO produtos (nome, validade, quantidade, lote, preco_custo, preco_venda, estoque_minimo) VALUES (?, ?, ?, ?, ?, ?, ?)"
        self.cursor.execute(query, (nome, validade, qtd, lote, p_custo, p_venda, min_est))
        self.conn.commit()
        return "Produto cadastrado com sucesso!"

    def cadastrar_vendedor(self, id_barcode, nome, tel, email):
        """RF01.2: Cadastra um vendedor com seu ID único (Código de Barras)."""
        try:
            self.cursor.execute("INSERT INTO vendedor (id_barcode, nome, tel, email) VALUES (?, ?, ?, ?)",
                                (id_barcode, nome, tel, email))
            self.conn.commit()
            return "Vendedor cadastrado com sucesso!"
        except sqlite3.IntegrityError:
            return "Erro: ID de código de barras já existe."
        except Exception as e:
            return f"Erro ao cadastrar vendedor: {e}"

    def realizar_venda(self, id_vendedor, id_cliente, id_produto, quantidade, pagamento_avista=False):
        """RN01 e RN05: Validação de estoque e validade."""
        self.cursor.execute("SELECT quantidade, validade, preco_venda FROM produtos WHERE id = ?", (id_produto,))
        prod = self.cursor.fetchone()

        if not prod:
            return "Erro: Produto não encontrado."

        if prod[0] < quantidade: # RN05
            return "Erro: Sem estoque disponível."

        # Convertendo a data de validade para um objeto datetime para comparação
        data_atual = datetime.now().strftime("%Y-%m-%d")
        if prod[1] < data_atual: # RN01 [cite: 17]
            return "Erro: Produto vencido. Saída não permitida."

        # Processar venda
        preco_unitario = prod[2]
        total = preco_unitario * quantidade

        if pagamento_avista: # RN03: Política de Descontos (10% de desconto para pagamentos à vista)
            total = total * 0.90

        self.cursor.execute("INSERT INTO vendas (id_vendedor, id_cliente, valor_total) VALUES (?,?,?)", (id_vendedor, id_cliente, total))
        id_venda = self.cursor.lastrowid
        self.cursor.execute("INSERT INTO itens_vendas (id_venda, id_produto, qnt, preco_unitario) VALUES (?,?,?,?)", (id_venda, id_produto, quantidade, prod[2]))
        
        # Baixa no estoque
        self.cursor.execute("UPDATE produtos SET quantidade = quantidade - ? WHERE id = ?", (quantidade, id_produto))
        self.conn.commit()
        return f"Venda realizada com sucesso! Total: R${total}"

    def verificar_estoque_critico(self):
        """RF02: Emite alertas quando o estoque atinge a quantidade mínima definida."""
        self.cursor.execute("SELECT nome, quantidade, estoque_minimo FROM produtos WHERE quantidade <= estoque_minimo")
        return self.cursor.fetchall()

    def gerar_relatorio_vendas_por_vendedor_comissao(self, id_vendedor=None):
        """RF04: Gera relatório de vendas por representante comercial para cálculo de comissões."""
        query = """
            SELECT v.nome, SUM(iv.qnt * iv.preco_unitario) AS total_vendas
            FROM vendas ve
            JOIN vendedor v ON ve.id_vendedor = v.id_barcode
            JOIN itens_vendas iv ON ve.id_venda = iv.id_venda
            WHERE (? IS NULL OR ve.id_vendedor = ?)
            GROUP BY v.nome
        """
        self.cursor.execute(query, (id_vendedor, id_vendedor))
        return self.cursor.fetchall()

    def gerar_relatorio_lucro(self):
        """RN04: Margem de lucro apenas para Administrador."""
        self.cursor.execute("SELECT nome, (preco_venda - preco_custo) FROM produtos")
        return self.cursor.fetchall()

# --- Execução Principal ---
if __name__ == "__main__":
    app = SistemaXoSujeira()
    
    print("=== SISTEMA LOJA XÔ SUJEIRA ===")
    u = input("Usuário: ")
    s = input("Senha: ")
    perfil = app.login(u, s)

    if perfil == "Administrador":
        print("\nAcesso concedido: Painel Administrativo")
        # Exemplo de uso RF01 
        print(app.cadastrar_produto("Detergente Neutro", "2027-12-31", 100, "LOTE-001", 1.50, 3.50, 10))
        print(app.cadastrar_produto("Água Sanitária", "2026-06-15", 50, "LOTE-002", 2.00, 4.00, 5))
        
        # Exemplo de uso RF01.2
        print(app.cadastrar_vendedor("VEND001", "João Silva", "11987654321", "joao.silva@xosujeira.com"))
        print(app.cadastrar_vendedor("VEND002", "Maria Souza", "11912345678", "maria.souza@xosujeira.com"))
        
        print("\nRelatório de Margem de Lucro (RN04):")
        for p in app.gerar_relatorio_lucro():
            print(f"Produto: {p[0]} | Lucro Unitário: R${p[1]:.2f}")
        

    elif perfil == "Vendedor":
        print("\nAcesso concedido: Painel de Vendas")
        # Logica de vendas aqui...
    else:
        print("\nUsuário ou senha inválidos.")