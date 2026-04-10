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
                validade DATE,
                quantidade INT DEFAULT 0,
                categoria VARCHAR(100),
                lote VARCHAR(20),
                preco_custo DECIMAL(10,2),
                preco_venda DECIMAL(10,2),
                estoque_minimo INT
            )
        """)

        # Tabela de Vendedores
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendedor (
                id INTEGER PRIMARY KEY,
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
                FOREIGN KEY (id_vendedor) REFERENCES vendedor(id),
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
        """RF01: Cadastro com lote e validade """
        query = "INSERT INTO produtos (nome, validade, quantidade, lote, preco_custo, preco_venda, estoque_minimo) VALUES (?,?,?,?,?,?,?)"
        self.cursor.execute(query, (nome, validade, qtd, lote, p_custo, p_venda, min_est))
        self.conn.commit()

    def realizar_venda(self, id_vendedor, id_cliente, id_produto, quantidade):
        """RN01 e RN05: Validação de estoque e validade """
        self.cursor.execute("SELECT quantidade, validade, preco_venda FROM produtos WHERE id = ?", (id_produto,))
        prod = self.cursor.fetchone()

        if not prod or prod[0] < quantidade: # RN05 [cite: 22]
            return "Erro: Sem estoque disponível."

        data_atual = datetime.now().strftime("%Y-%m-%d")
        if prod[1] < data_atual: # RN01 [cite: 17]
            return "Erro: Produto vencido. Saída não permitida."

        # Processar venda
        total = prod[2] * quantidade
        self.cursor.execute("INSERT INTO vendas (id_vendedor, id_cliente, valor_total) VALUES (?,?,?)", (id_vendedor, id_cliente, total))
        id_venda = self.cursor.lastrowid
        self.cursor.execute("INSERT INTO itens_vendas (id_venda, id_produto, qnt, preco_unitario) VALUES (?,?,?,?)", (id_venda, id_produto, quantidade, prod[2]))
        
        # Baixa no estoque
        self.cursor.execute("UPDATE produtos SET quantidade = quantidade - ? WHERE id = ?", (quantidade, id_produto))
        self.conn.commit()
        return f"Venda realizada com sucesso! Total: R${total}"

    def gerar_relatorio_lucro(self):
        """RN04: Margem de lucro apenas para Administrador [cite: 21, 26]"""
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
        app.cadastrar_produto("Detergente Neutro", "2027-12-31", 100, "LOTE-001", 1.50, 3.50, 10)
        
        print("\nRelatório de Margem de Lucro (RN04):")
        for p in app.gerar_relatorio_lucro():
            print(f"Produto: {p[0]} | Lucro Unitário: R${p[1]:.2f}")

    elif perfil == "Vendedor":
        print("\nAcesso concedido: Painel de Vendas")
        # Logica de vendas aqui...
    else:
        print("\nUsuário ou senha inválidos.")