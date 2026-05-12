"""
Módulo para gerenciamento de cadastro de produtos.
Define funções para adicionar, listar, buscar, atualizar e remover produtos.
"""

import datetime

# Armazenamento em memória para os produtos.
# Em uma aplicação real, isso seria substituído por um banco de dados ou arquivo.
_produtos = []
_next_id = 1

def _gerar_novo_id() -> int:
    """Gera um novo ID único para um produto."""
    global _next_id
    new_id = _next_id
    _next_id += 1
    return new_id

class Produto:
    """Representa um produto com seus atributos."""
    def __init__(self, id: int, nome: str, validade: datetime.date, qnt: int, categoria: str):
        if not isinstance(id, int) or id <= 0:
            raise ValueError("ID do produto deve ser um número inteiro positivo.")
        if not isinstance(nome, str) or not nome.strip():
            raise ValueError("Nome do produto não pode ser vazio.")
        if not isinstance(validade, datetime.date):
            raise ValueError("Validade do produto deve ser um objeto datetime.date.")
        if not isinstance(qnt, int) or qnt < 0:
            raise ValueError("Quantidade do produto deve ser um número inteiro não negativo.")
        if not isinstance(categoria, str) or not categoria.strip():
            raise ValueError("Categoria do produto não pode ser vazia.")

        self.id = id
        self.nome = nome.strip()
        self.validade = validade
        self.qnt = qnt
        self.categoria = categoria.strip()

    def __str__(self) -> str:
        return (f"ID: {self.id}, Nome: {self.nome}, Validade: {self.validade.strftime('%d/%m/%Y')}, "
                f"Quantidade: {self.qnt}, Categoria: {self.categoria}")

    def to_dict(self) -> dict:
        """Retorna o produto como um dicionário."""
        return {
            "id": self.id,
            "nome": self.nome,
            "validade": self.validade.isoformat(), # Formato ISO para fácil serialização
            "qnt": self.qnt,
            "categoria": self.categoria
        }

def adicionar_produto(nome: str, validade_str: str, qnt: int, categoria: str) -> Produto:
    """
    Adiciona um novo produto ao cadastro.
    A validade deve ser fornecida no formato 'DD-MM-YYYY'.
    """
    try:
        validade = datetime.datetime.strptime(validade_str, '%d-%m-%Y').date()
    except ValueError:
        raise ValueError("Formato de data inválido. Use 'DD-MM-YYYY'.")

    novo_id = _gerar_novo_id()
    produto = Produto(novo_id, nome, validade, qnt, categoria)
    _produtos.append(produto)
    print(f"Produto '{produto.nome}' adicionado com ID {produto.id}.")
    return produto

def listar_produtos() -> list[Produto]:
    """Lista todos os produtos cadastrados."""
    if not _produtos:
        print("Nenhum produto cadastrado.")
        return []
    print("\n--- Lista de Produtos ---")
    for produto in _produtos:
        print(produto)
    print("-------------------------")
    return _produtos

def buscar_produto(id: int) -> Produto | None:
    """Busca um produto pelo ID."""
    for produto in _produtos:
        if produto.id == id:
            return produto
    print(f"Produto com ID {id} não encontrado.")
    return None

def atualizar_produto(id: int, novo_nome: str = None, nova_validade_str: str = None,
                      nova_qnt: int = None, nova_categoria: str = None) -> Produto | None:
    """Atualiza os dados de um produto existente."""
    produto = buscar_produto(id)
    if produto:
        if novo_nome:
            produto.nome = novo_nome.strip()
        if nova_validade_str:
            try:
                produto.validade = datetime.datetime.strptime(nova_validade_str, '%d-%m-%Y').date()
            except ValueError:
                print("Formato de data inválido para atualização. Use 'DD-MM-YYYY'.")
                return None
        if nova_qnt is not None:
            if nova_qnt < 0:
                print("Quantidade não pode ser negativa.")
                return None
            produto.qnt = nova_qnt
        if nova_categoria:
            produto.categoria = nova_categoria.strip()
        print(f"Produto com ID {id} atualizado.")
        return produto
    return None

def remover_produto(id: int) -> bool:
    """Remove um produto do cadastro pelo ID."""
    global _produtos
    produto_removido = None
    for i, produto in enumerate(_produtos):
        if produto.id == id:
            produto_removido = _produtos.pop(i)
            break
    if produto_removido:
        print(f"Produto '{produto_removido.nome}' (ID: {id}) removido.")
        return True
    print(f"Produto com ID {id} não encontrado para remoção.")
    return False

# Exemplo de uso:
if __name__ == "__main__":
    print("--- Testando o Módulo de Produtos ---")

    adicionar_produto("Leite Integral", "10-12-2024", 20, "Laticínios")
    adicionar_produto("Pão de Forma", "05-11-2024", 15, "Padaria")
    adicionar_produto("Arroz Branco 5kg", "20-01-2025", 30, "Grãos")

    listar_produtos()

    produto_buscado = buscar_produto(1)
    if produto_buscado:
        print(f"\nProduto buscado (ID 1): {produto_buscado}")

    atualizar_produto(2, novo_nome="Pão Integral", nova_qnt=10)
    listar_produtos()

    remover_produto(3)
    listar_produtos()

    adicionar_produto("Queijo Minas", "25-12-2024", 12, "Laticínios")
    listar_produtos()