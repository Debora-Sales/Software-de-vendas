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
        self.geometry("750x850")
        self.resizable(False, False)

        self.grab_set()
        self.focus()

        # Estado
        self.id_produto_editando = None
        self.produto_atual = None

        # Título principal
        ctk.CTkLabel(self, text="Gerenciamento de Produtos", font=("Roboto", 28, "bold")).pack(pady=15)

        # Status/Feedback (Inspirado no vendas.py)
        self.lbl_status = ctk.CTkLabel(self, text="", font=("Roboto", 14, "bold"))
        self.lbl_status.pack(pady=5)

        # --- FRAME DE BUSCA (TOPO) ---
        self.frame_busca = ctk.CTkFrame(self)
        self.frame_busca.pack(padx=20, pady=10, fill="x")
        
        ctk.CTkLabel(self.frame_busca, text="Localizar Produto (ID):", font=("Roboto", 12, "bold")).pack(side="left", padx=10)
        
        self.ent_busca_id = ctk.CTkEntry(self.frame_busca, placeholder_text="ID...", width=150)
        self.ent_busca_id.pack(side="left", padx=5)
        self.ent_busca_id.bind("<KeyRelease>", lambda e: self.validar_apenas_numeros(self.ent_busca_id))

        self.btn_buscar = ctk.CTkButton(self.frame_busca, text="🔍 Buscar / Editar", width=140, command=self.buscar_produto)
        self.btn_buscar.pack(side="left", padx=10)

        self.btn_cancelar = ctk.CTkButton(self.frame_busca, text="❌ Cancelar", width=100, fg_color="#444444", hover_color="#333333", command=self.limpar_campos)
        # O botão inicia sem pack() para ficar oculto até uma busca ser realizada

        # --- FRAME DO FORMULÁRIO ---
        self.frame_form = ctk.CTkFrame(self)
        self.frame_form.pack(padx=20, pady=10, fill="both", expand=True)

        # Campos com Labels
        ctk.CTkLabel(self.frame_form, text="Nome do Produto:", font=("Roboto", 12, "bold")).pack(anchor="w", padx=150)
        self.ent_nome = self.criar_entry(self.frame_form, "Ex: Detergente Neutro 500ml")
        self.ent_nome.pack(pady=(0, 10))

        ctk.CTkLabel(self.frame_form, text="Categoria:", font=("Roboto", 12, "bold")).pack(anchor="w", padx=150)
        self.ent_categoria = self.criar_entry(self.frame_form, "Ex: Limpeza, Higiene")
        self.ent_categoria.pack(pady=(0, 10))

        ctk.CTkLabel(self.frame_form, text="Lote:", font=("Roboto", 12, "bold")).pack(anchor="w", padx=150)
        self.ent_lote = self.criar_entry(self.frame_form, "Apenas números")
        self.ent_lote.pack(pady=(0, 10))

        ctk.CTkLabel(self.frame_form, text="Data de Validade:", font=("Roboto", 12, "bold")).pack(anchor="w", padx=150)
        self.ent_validade = self.criar_entry(self.frame_form, "DD/MM/AAAA")
        self.ent_validade.pack(pady=(0, 10))

        ctk.CTkLabel(self.frame_form, text="Quantidade em Estoque:", font=("Roboto", 12, "bold")).pack(anchor="w", padx=150)
        self.ent_qnt = self.criar_entry(self.frame_form, "0 a 100")
        self.ent_qnt.pack(pady=(0, 10))

        ctk.CTkLabel(self.frame_form, text="Estoque Mínimo (Alerta):", font=("Roboto", 12, "bold")).pack(anchor="w", padx=150)
        self.ent_min = self.criar_entry(self.frame_form, "Quantidade para aviso")
        self.ent_min.pack(pady=(0, 10))

        ctk.CTkLabel(self.frame_form, text="Preço de Custo:", font=("Roboto", 12, "bold")).pack(anchor="w", padx=150)
        self.ent_custo = self.criar_entry(self.frame_form, "R$ 0,00")
        self.ent_custo.pack(pady=(0, 10))

        ctk.CTkLabel(self.frame_form, text="Preço de Venda:", font=("Roboto", 12, "bold")).pack(anchor="w", padx=150)
        self.ent_venda = self.criar_entry(self.frame_form, "R$ 0,00")
        self.ent_venda.pack(pady=(0, 10))

        self.ent_lote.bind("<KeyRelease>", lambda e: self.validar_apenas_numeros(self.ent_lote))
        self.ent_validade.bind("<KeyRelease>", self.formatar_data)
        self.ent_qnt.bind("<KeyRelease>", self.validar_estoque)
        self.ent_min.bind("<KeyRelease>", lambda e: self.validar_apenas_numeros(self.ent_min))
        self.ent_custo.bind("<FocusOut>", lambda e: self.formatar_moeda(self.ent_custo))
        self.ent_venda.bind("<FocusOut>", lambda e: self.formatar_moeda(self.ent_venda))

        # --- FRAME DE AÇÕES (BOTÕES) ---
        self.frame_acoes = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_acoes.pack(pady=15)

        self.btn_salvar = ctk.CTkButton(self.frame_acoes, text="💾 Salvar / Atualizar", height=45, font=("Roboto", 15, "bold"), fg_color="green", command=self.validar_e_salvar)
        self.btn_salvar.pack(side="left", padx=10)

        self.btn_limpar = ctk.CTkButton(self.frame_acoes, text="🧹 Limpar", height=45, font=("Roboto", 15, "bold"), fg_color="gray", command=self.limpar_campos)
        self.btn_limpar.pack(side="left", padx=10)

        self.btn_excluir = ctk.CTkButton(self.frame_acoes, text="🗑️ Excluir", height=45, font=("Roboto", 15, "bold"), fg_color="red", state="disabled", command=self.confirmar_exclusao)
        self.btn_excluir.pack(side="left", padx=10)

        # Área de log/detalhes (Opcional, mas útil para o Alerta de Estoque Mínimo)
        self.txt_resultado = ctk.CTkTextbox(self, width=650, height=100, font=("Roboto", 12))
        self.txt_resultado.pack(pady=10, padx=20)
        self.txt_resultado.insert("0.0", "Informações adicionais e alertas de estoque aparecerão aqui...")
        self.txt_resultado.configure(state="disabled")

    def mostrar_feedback(self, mensagem, cor="red"):
        self.lbl_status.configure(text=mensagem, text_color=cor)
        self.after(3500, lambda: self.lbl_status.configure(text=""))

    def buscar_produto(self):
        id_digitado = self.ent_busca_id.get()
        if not id_digitado:
            self.mostrar_feedback("⚠️ Informe um ID.")
            return

        produto = buscar_produto_por_id(id_digitado)
        self.produto_atual = produto

        if produto:
            self.preparar_edicao() # Preenche o formulário automaticamente
            self.btn_excluir.configure(state="normal")
            self.btn_cancelar.pack(side="left", padx=5) # Mostra o botão ao carregar um produto
            
            # Alerta de estoque na caixa de texto
            self.txt_resultado.configure(state="normal")
            self.txt_resultado.delete("1.0", "end")
            info = f"PRODUTO ENCONTRADO:\n\n"
            info += f"ID: {produto['id']}\n"
            if produto['quantidade'] <= produto['estoque_minimo']:
                info += f"\n\n⚠️ ALERTA: ESTOQUE CRÍTICO!\nA quantidade atual ({produto['quantidade']}) atingiu o limite mínimo ({produto['estoque_minimo']})."
            self.txt_resultado.insert("0.0", info)
            self.txt_resultado.configure(state="disabled")
            
            self.mostrar_feedback("✅ Produto carregado para edição!", "green")
        else:
            self.btn_excluir.configure(state="disabled")
            self.mostrar_feedback("❌ Produto não encontrado.")
            self.limpar_campos()

    def criar_entry(self, master, texto):
        return ctk.CTkEntry(
            master,
            placeholder_text=texto,
            width=450,
            height=40,
            corner_radius=10
        )

    # --- MÉTODOS DE FORMATAÇÃO E VALIDAÇÃO (SCRIPT 24) ---

    def validar_apenas_numeros(self, entry):
        texto = entry.get()
        if not texto.isdigit() and texto != "":
            limpo = "".join(filter(str.isdigit, texto))
            entry.delete(0, "end")
            entry.insert(0, limpo)

    def formatar_data(self, event):
        if event.keysym == "BackSpace": return
        texto = "".join(filter(str.isdigit, self.ent_validade.get()))
        novo_texto = ""
        if len(texto) > 8: texto = texto[:8]
        
        for i, char in enumerate(texto):
            if i == 2 or i == 4:
                novo_texto += "/"
            novo_texto += char
            
        self.ent_validade.delete(0, "end")
        self.ent_validade.insert(0, novo_texto)

    def validar_estoque(self, event):
        self.validar_apenas_numeros(self.ent_qnt)
        texto = self.ent_qnt.get()
        if texto:
            try:
                val = int(texto)
                if val > 100:
                    self.ent_qnt.delete(0, "end")
                    self.ent_qnt.insert(0, "100")
                elif val < 0:
                    self.ent_qnt.delete(0, "end")
                    self.ent_qnt.insert(0, "0")
            except ValueError:
                pass

    def formatar_moeda(self, entry):
        texto = entry.get().replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".").strip()
        try:
            if not texto: return
            valor = float(texto)
            formatado = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            entry.delete(0, "end")
            entry.insert(0, formatado)
        except ValueError:
            pass

    def extrair_valor_float(self, campo):
        texto = campo.get().replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")
        try:
            return float(texto)
        except:
            return 0.0

    def limpar_campos(self):
        self.ent_nome.delete(0, "end")
        self.ent_categoria.delete(0, "end")
        self.ent_lote.delete(0, "end")
        self.ent_validade.delete(0, "end")
        self.ent_qnt.delete(0, "end")
        self.ent_min.delete(0, "end")
        self.ent_custo.delete(0, "end")
        self.ent_venda.delete(0, "end")
        
        self.ent_busca_id.delete(0, "end") # Limpa o campo de busca ao cancelar/limpar
        self.btn_cancelar.pack_forget()    # Esconde o botão cancelar ao voltar para o modo cadastro
        
        self.txt_resultado.configure(state="normal")
        self.txt_resultado.delete("1.0", "end")
        self.txt_resultado.insert("0.0", "Informações adicionais aparecerão aqui...")
        self.txt_resultado.configure(state="disabled")

        self.id_produto_editando = None
        self.btn_salvar.configure(text="💾 Salvar / Atualizar", fg_color="green")
        self.btn_excluir.configure(state="disabled")

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

        self.btn_salvar.configure(text="🔄 Atualizar Produto", fg_color="blue")

    def confirmar_exclusao(self):
        if not self.produto_atual:
            return

        confirmar = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Deseja realmente excluir o produto '{self.produto_atual['nome']}'?"
        )

        if confirmar:
            if deletar_produto_db(self.produto_atual['id']):
                self.mostrar_feedback("🗑️ Produto excluído!", "orange")
                self.ent_busca_id.delete(0, "end")
                self.limpar_campos()

    def validar_e_salvar(self):
        try:
            dados = {
                "nome": self.ent_nome.get(),
                "validade": self.ent_validade.get(),
                "quantidade": int(self.ent_qnt.get()),
                "categoria": self.ent_categoria.get(),
                "lote": self.ent_lote.get(),
                "preco_custo": self.extrair_valor_float(self.ent_custo),
                "preco_venda": self.extrair_valor_float(self.ent_venda),
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
                self.mostrar_feedback(f"✅ Produto '{dados['nome']}' atualizado!", "green")
                self.limpar_campos()
        else:
            # Salvando no banco
            id_produto = salvar_produto(
                dados["nome"], dados["validade"], dados["quantidade"], 
                dados["categoria"], dados["lote"], dados["preco_custo"], 
                dados["preco_venda"], dados["estoque_minimo"]
            )

            if id_produto:
                self.mostrar_feedback(f"✅ Produto cadastrado com ID: {id_produto}", "green")
                self.limpar_campos()