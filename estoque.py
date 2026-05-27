import customtkinter as ctk
from tkinter import messagebox
from database import ajustar_estoque_db, obter_totais_estoque_db, buscar_produto_por_id

class JanelaEstoque(ctk.CTkToplevel):
    def __init__(self, parent, perfil):
        super().__init__(parent)

        self.title("Controle de Estoque - Xô Sujeira")
        self.geometry("700x750")
        self.resizable(False, False)
        self.perfil = perfil
        self.lista_movimentacao = []
        self.grab_set()
        self.focus()

        ctk.CTkLabel(self, text="📦 Movimentação de Lote (Entrada/Saída)", font=("Roboto", 24, "bold")).pack(pady=15)

        # Painel de Totais
        self.frame_info = ctk.CTkFrame(self, fg_color="#2b2b2b")
        self.frame_info.pack(padx=20, pady=10, fill="x")
        
        self.lbl_itens = ctk.CTkLabel(self.frame_info, text="Itens Cadastrados: --", font=("Roboto", 14))
        self.lbl_itens.pack(pady=5)
        self.lbl_unidades = ctk.CTkLabel(self.frame_info, text="Total de Unidades: --", font=("Roboto", 14, "bold"), text_color="cyan")
        self.lbl_unidades.pack(pady=5)

        # Formulário de Adição
        self.frame_add = ctk.CTkFrame(self)
        self.frame_add.pack(padx=20, pady=10, fill="x")

        f_inputs = ctk.CTkFrame(self.frame_add, fg_color="transparent")
        f_inputs.pack(pady=10)

        ctk.CTkLabel(f_inputs, text="ID Produto:", font=("Roboto", 11, "bold")).grid(row=0, column=0, padx=5)
        self.ent_id = ctk.CTkEntry(f_inputs, placeholder_text="ID", width=100)
        self.ent_id.grid(row=1, column=0, padx=5)

        ctk.CTkLabel(f_inputs, text="Quantidade:", font=("Roboto", 11, "bold")).grid(row=0, column=1, padx=5)
        self.ent_qtd = ctk.CTkEntry(f_inputs, placeholder_text="Qtd", width=100)
        self.ent_qtd.grid(row=1, column=1, padx=5)

        self.btn_add_lista = ctk.CTkButton(f_inputs, text="+ Adicionar à Lista", width=150, fg_color="teal", command=self.adicionar_a_lista)
        self.btn_add_lista.grid(row=1, column=2, padx=10)

        # Lista de Movimentação (O "Carrinho" do Estoque)
        ctk.CTkLabel(self, text="Produtos para Processar:", font=("Roboto", 14, "bold")).pack(pady=(10, 0))
        self.scroll_lista = ctk.CTkScrollableFrame(self, width=650, height=300)
        self.scroll_lista.pack(padx=20, pady=5, fill="both", expand=True)

        # Botão de Finalização
        self.btn_finalizar = ctk.CTkButton(
            self,
            text="✅ FINALIZAR MOVIMENTAÇÃO DE LOTE",
            height=50,
            fg_color="green",
            font=("Roboto", 16, "bold"),
            command=self.finalizar_lote
        )
        self.btn_finalizar.pack(pady=20)

        self.atualizar_totais()
        self.atualizar_lista_ui()

    def atualizar_totais(self):
        qtd_itens, total_unidades = obter_totais_estoque_db()
        self.lbl_itens.configure(text=f"📊 Variedade de Produtos: {qtd_itens}")
        self.lbl_unidades.configure(text=f"🔢 Saldo Total Global: {total_unidades}")

    def adicionar_a_lista(self):
        """Adiciona um produto temporariamente à lista de processamento."""
        id_prod = self.ent_id.get()
        qtd_ajuste = self.ent_qtd.get()

        if not id_prod or not qtd_ajuste:
            messagebox.showwarning("Atenção", "Preencha o ID e a Quantidade.")
            return

        try:
            id_int = int(id_prod)
            qtd_int = int(qtd_ajuste)
        except ValueError:
            messagebox.showerror("Erro", "ID e Quantidade devem ser números inteiros.")
            return

        if qtd_int == 0:
            return

        if self.perfil == "Estoquista" and qtd_int < 0:
            messagebox.showwarning("Acesso Restrito", "Seu perfil de Estoquista permite realizar apenas ENTRADAS de mercadoria.")
            return

        prod = buscar_produto_por_id(id_int)
        if not prod:
            messagebox.showerror("Erro", "Produto não encontrado no sistema.")
            return

        # Adiciona à lista local
        self.lista_movimentacao.append({
            "id": id_int,
            "nome": prod['nome'],
            "qtd": qtd_int
        })
        
        self.ent_id.delete(0, "end")
        self.ent_qtd.delete(0, "end")
        self.atualizar_lista_ui()

    def remover_da_lista(self, index):
        self.lista_movimentacao.pop(index)
        self.atualizar_lista_ui()

    def atualizar_lista_ui(self):
        """Renderiza os itens que serão processados."""
        for widget in self.scroll_lista.winfo_children():
            widget.destroy()

        for i, item in enumerate(self.lista_movimentacao):
            f = ctk.CTkFrame(self.scroll_lista)
            f.pack(fill="x", pady=2)
            
            cor_tipo = "#4CAF50" if item['qtd'] > 0 else "#F44336"
            txt_tipo = "ENTRADA" if item['qtd'] > 0 else "SAÍDA"
            
            ctk.CTkLabel(f, text=f"ID: {item['id']}", width=60).pack(side="left", padx=5)
            ctk.CTkLabel(f, text=item['nome'], width=250, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(f, text=f"{txt_tipo}: {abs(item['qtd'])} un", width=150, text_color=cor_tipo, font=("", 11, "bold")).pack(side="left")
            
            ctk.CTkButton(f, text="X", width=30, fg_color="#444", hover_color="red", command=lambda idx=i: self.remover_da_lista(idx)).pack(side="right", padx=10)

    def finalizar_lote(self):
        """Processa todos os itens da lista no banco de dados."""
        if not self.lista_movimentacao:
            messagebox.showwarning("Atenção", "A lista está vazia.")
            return

        confirmar = messagebox.askyesno("Confirmar Lote", f"Deseja processar a movimentação de {len(self.lista_movimentacao)} produto(s)?")
        if confirmar:
            sucessos = 0
            for item in self.lista_movimentacao:
                if ajustar_estoque_db(item['id'], item['qtd']):
                    sucessos += 1
            
            messagebox.showinfo("Processamento", f"Lote finalizado!\n{sucessos} produtos atualizados com sucesso.")
            self.lista_movimentacao = []
            self.atualizar_lista_ui()
            self.atualizar_totais()