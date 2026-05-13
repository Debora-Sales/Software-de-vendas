import customtkinter as ctk
from tkinter import messagebox
from database import (
    salvar_produto, 
    buscar_produto_por_id, 
    atualizar_produto_db, 
    deletar_produto_db
)

class JanelaProdutos(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("Cadastro de Produtos - Xô Sujeira")
        self.geometry("700x750")
        self.resizable(False, False)

        self.grab_set()
        self.focus()

        self.id_produto_editando = None
        self.produto_atual = None

        self.label_titulo = ctk.CTkLabel(
            self,
            text="Novo Cadastro de Produto",
            font=("Roboto", 28, "bold")
        )
        self.label_titulo.pack(pady=20)

        # Criação das Abas (Tabs)
        self.tabview = ctk.CTkTabview(self, width=650, height=600)
        self.tabview.pack(padx=20, pady=10, fill="both", expand=True)
        
        self.tab_cadastro = self.tabview.add("Cadastrar Produto")
        self.tab_busca = self.tabview.add("Buscar Produto")

        # --- UI DA ABA CADASTRO ---
        
        # Campos de entrada para cadastro
        self.ent_nome = self.criar_entry(self.tab_cadastro, "Nome do Produto (ex: Detergente Neutro 500ml)")
        self.ent_categoria = self.criar_entry(self.tab_cadastro, "Categoria (ex: Limpeza, Higiene)")
        self.ent_lote = self.criar_entry(self.tab_cadastro, "Lote")
        self.ent_validade = self.criar_entry(self.tab_cadastro, "Data de Validade (DD/MM/YYYY)")
        self.ent_qnt = self.criar_entry(self.tab_cadastro, "Quantidade em Estoque")
        self.ent_min = self.criar_entry(self.tab_cadastro, "Estoque Mínimo (Alerta)")
        self.ent_custo = self.criar_entry(self.tab_cadastro, "Preço de Custo (Ex: 1.50)")
        self.ent_venda = self.criar_entry(self.tab_cadastro, "Preço de Venda (Ex: 3.50)")

        # Posicionamento
        for entry in [self.ent_nome, self.ent_categoria, self.ent_lote, self.ent_validade, self.ent_qnt, self.ent_min, self.ent_custo, self.ent_venda]:
            entry.pack(pady=8)

        self.frame_botoes_cadastro = ctk.CTkFrame(self.tab_cadastro, fg_color="transparent")
        self.frame_botoes_cadastro.pack(pady=15)

        self.btn_salvar = ctk.CTkButton(
            self.frame_botoes_cadastro,
            text="Salvar Produto",
            height=45,
            font=("Roboto", 16, "bold"),
            fg_color="green",
            hover_color="darkgreen",
            command=self.validar_e_salvar
        )
        self.btn_salvar.pack(side="left", padx=10)

        # Sprint 9: Botão Limpar Campos
        self.btn_limpar = ctk.CTkButton(
            self.frame_botoes_cadastro,
            text="Limpar Campos",
            height=45,
            font=("Roboto", 16, "bold"),
            fg_color="gray",
            hover_color="dimgray",
            command=self.limpar_campos
        )
        self.btn_limpar.pack(side="left", padx=10)

        # --- UI DA ABA BUSCA ---
        
        self.frame_busca = ctk.CTkFrame(self.tab_busca, fg_color="transparent")
        self.frame_busca.pack(pady=20, padx=20, fill="x")

        self.ent_busca_id = ctk.CTkEntry(
            self.frame_busca, 
            placeholder_text="Digite o ID do produto...",
            width=300,
            height=40
        )
        self.ent_busca_id.pack(side="left", padx=10)

        self.btn_buscar = ctk.CTkButton(
            self.frame_busca,
            text="Buscar",
            width=100,
            height=40,
            command=self.buscar_produto
        )
        self.btn_buscar.pack(side="left")

        self.txt_resultado = ctk.CTkTextbox(
            self.tab_busca,
            width=550,
            height=300,
            font=("Roboto", 14)
        )
        self.txt_resultado.pack(pady=20, padx=20)
        self.txt_resultado.insert("0.0", "Os detalhes do produto aparecerão aqui...")
        self.txt_resultado.configure(state="disabled")

        # Sprints 7 e 8: Botões de Ação na Busca
        self.frame_acoes_busca = ctk.CTkFrame(self.tab_busca, fg_color="transparent")
        self.frame_acoes_busca.pack(pady=10)

        self.btn_editar = ctk.CTkButton(
            self.frame_acoes_busca,
            text="Editar Produto",
            state="disabled",
            command=self.preparar_edicao
        )
        self.btn_editar.pack(side="left", padx=10)

        self.btn_excluir = ctk.CTkButton(
            self.frame_acoes_busca,
            text="Excluir Produto",
            state="disabled",
            fg_color="red",
            hover_color="darkred",
            command=self.confirmar_exclusao
        )
        self.btn_excluir.pack(side="left", padx=10)

    def buscar_produto(self):
        id_digitado = self.ent_busca_id.get()
        if not id_digitado:
            messagebox.showwarning("Atenção", "Informe um ID para buscar.")
            return

        produto = buscar_produto_por_id(id_digitado)
        self.produto_atual = produto
        
        self.txt_resultado.configure(state="normal")
        self.txt_resultado.delete("1.0", "end")
        
        if produto:
            self.btn_editar.configure(state="normal")
            self.btn_excluir.configure(state="normal")

            info = f"PRODUTO ENCONTRADO:\n\n"
            info += f"ID: {produto['id']}\n"
            info += f"Nome: {produto['nome']}\n"
            info += f"Categoria: {produto['categoria']}\n"
            info += f"Lote: {produto['lote']}\n"
            info += f"Validade: {produto['validade']}\n"
            info += f"Quantidade: {produto['quantidade']}\n"
            info += f"Preço Venda: R$ {produto['preco_venda']:.2f}\n"
            info += f"Estoque Mínimo: {produto['estoque_minimo']}"

            # Sprint 10: Alerta de Estoque Mínimo
            if produto['quantidade'] <= produto['estoque_minimo']:
                info += f"\n\n⚠️ ALERTA: ESTOQUE CRÍTICO!\nA quantidade atual ({produto['quantidade']}) atingiu o limite mínimo ({produto['estoque_minimo']})."

            self.txt_resultado.insert("0.0", info)
        else:
            self.btn_editar.configure(state="disabled")
            self.btn_excluir.configure(state="disabled")
            self.txt_resultado.insert("0.0", "Produto não encontrado no sistema.")
        
        self.txt_resultado.configure(state="disabled")

    def criar_entry(self, master, texto):
        return ctk.CTkEntry(
            master,
            placeholder_text=texto,
            width=450,
            height=40,
            corner_radius=10
        )

    def limpar_campos(self):
        self.ent_nome.delete(0, "end")
        self.ent_categoria.delete(0, "end")
        self.ent_lote.delete(0, "end")
        self.ent_validade.delete(0, "end")
        self.ent_qnt.delete(0, "end")
        self.ent_min.delete(0, "end")
        self.ent_custo.delete(0, "end")
        self.ent_venda.delete(0, "end")
        
        self.id_produto_editando = None
        self.btn_salvar.configure(text="Salvar Produto", fg_color="green")

    def preparar_edicao(self):
        if not self.produto_atual:
            return

        self.limpar_campos()
        
        self.id_produto_editando = self.produto_atual['id']
        
        self.ent_nome.insert(0, self.produto_atual['nome'])
        self.ent_categoria.insert(0, self.produto_atual['categoria'])
        self.ent_lote.insert(0, self.produto_atual['lote'])
        self.ent_validade.insert(0, self.produto_atual['validade'])
        self.ent_qnt.insert(0, str(self.produto_atual['quantidade']))
        self.ent_min.insert(0, str(self.produto_atual['estoque_minimo']))
        self.ent_custo.insert(0, str(self.produto_atual['preco_custo']))
        self.ent_venda.insert(0, str(self.produto_atual['preco_venda']))

        self.btn_salvar.configure(text="Atualizar Produto", fg_color="blue")
        self.tabview.set("Cadastrar Produto")

    def confirmar_exclusao(self):
        if not self.produto_atual:
            return

        confirmar = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Deseja realmente excluir o produto '{self.produto_atual['nome']}'?"
        )

        if confirmar:
            if deletar_produto_db(self.produto_atual['id']):
                messagebox.showinfo("Sucesso", "Produto excluído com sucesso.")
                self.ent_busca_id.delete(0, "end")
                self.txt_resultado.configure(state="normal")
                self.txt_resultado.delete("1.0", "end")
                self.txt_resultado.insert("0.0", "Os detalhes do produto aparecerão aqui...")
                self.txt_resultado.configure(state="disabled")
                self.btn_editar.configure(state="disabled")
                self.btn_excluir.configure(state="disabled")
                self.produto_atual = None

    def validar_e_salvar(self):
        try:
            dados = {
                "nome": self.ent_nome.get(),
                "validade": self.ent_validade.get(),
                "quantidade": int(self.ent_qnt.get()),
                "categoria": self.ent_categoria.get(),
                "lote": self.ent_lote.get(),
                "preco_custo": float(self.ent_custo.get().replace(',', '.')),
                "preco_venda": float(self.ent_venda.get().replace(',', '.')),
                "estoque_minimo": int(self.ent_min.get())
            }
        except ValueError:
            messagebox.showwarning("Erro de Preenchimento", "Certifique-se que Quantidade e Preços são números válidos.")
            return

        if not dados["nome"] or not dados["validade"] or not dados["lote"] or not dados["categoria"]:
            messagebox.showwarning("Campos obrigatórios", "Preencha Nome, Categoria, Validade e Lote.")
            return

        if self.id_produto_editando:
            sucesso = atualizar_produto_db(
                self.id_produto_editando,
                dados["nome"], dados["validade"], dados["quantidade"], 
                dados["categoria"], dados["lote"], dados["preco_custo"], 
                dados["preco_venda"], dados["estoque_minimo"]
            )
            if sucesso:
                messagebox.showinfo("Sucesso", f"Produto '{dados['nome']}' atualizado!")
                self.limpar_campos()
                self.tabview.set("Buscar Produto")
        else:
            # Salvando no banco
            id_produto = salvar_produto(
                dados["nome"], dados["validade"], dados["quantidade"], 
                dados["categoria"], dados["lote"], dados["preco_custo"], 
                dados["preco_venda"], dados["estoque_minimo"]
            )

            if id_produto:
                messagebox.showinfo(
                    "Sucesso",
                    f"Produto '{dados['nome']}' cadastrado!\nID: {id_produto}"
                )
                self.limpar_campos()