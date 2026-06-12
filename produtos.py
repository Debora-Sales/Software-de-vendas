import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from database import (
    salvar_produto, 
    buscar_produto_por_id, 
    atualizar_produto_db, 
    deletar_produto_db
)

class JanelaProdutos(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

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
        
        # Script 47: Centralizador responsivo para ajustar layout em tela cheia ou janela
        self.centro_form = ctk.CTkFrame(self.frame_form, fg_color="transparent")
        self.centro_form.pack(expand=True, pady=10)

        # Campos com Labels
        ctk.CTkLabel(self.centro_form, text="Nome do Produto:", font=("Roboto", 12, "bold")).pack(anchor="w")
        self.ent_nome = self.criar_entry(self.centro_form, "Ex: Detergente Neutro 500ml")
        self.ent_nome.pack(pady=(0, 10))
        self.ent_nome.bind("<KeyRelease>", self.validar_nome)

        ctk.CTkLabel(self.centro_form, text="Categoria:", font=("Roboto", 12, "bold")).pack(anchor="w")
        self.ent_categoria = self.criar_entry(self.centro_form, "Ex: Limpeza, Higiene")
        self.ent_categoria.pack(pady=(0, 10))
        self.ent_categoria.bind("<KeyRelease>", self.validar_categoria)

        ctk.CTkLabel(self.centro_form, text="Lote:", font=("Roboto", 12, "bold")).pack(anchor="w")
        self.ent_lote = self.criar_entry(self.centro_form, "Apenas números")
        self.ent_lote.pack(pady=(0, 10))

        ctk.CTkLabel(self.centro_form, text="Data de Validade:", font=("Roboto", 12, "bold")).pack(anchor="w")
        self.ent_validade = self.criar_entry(self.centro_form, "DD/MM/AAAA")
        self.ent_validade.pack(pady=(0, 10))

        ctk.CTkLabel(self.centro_form, text="Quantidade em Estoque:", font=("Roboto", 12, "bold")).pack(anchor="w")
        self.ent_qnt = self.criar_entry(self.centro_form, "0 a 100")
        self.ent_qnt.pack(pady=(0, 10))

        ctk.CTkLabel(self.centro_form, text="Estoque Mínimo (Padrão 20):", font=("Roboto", 12, "bold")).pack(anchor="w")
        self.ent_min = self.criar_entry(self.centro_form, "Quantidade para aviso")
        self.ent_min.pack(pady=(0, 10))
        self.ent_min.insert(0, "20") # Script 41: Valor padrão inicial

        ctk.CTkLabel(self.centro_form, text="Preço de Custo:", font=("Roboto", 12, "bold")).pack(anchor="w")
        self.ent_custo = self.criar_entry(self.centro_form, "Ex: 1.00")
        self.ent_custo.pack(pady=(0, 10))

        ctk.CTkLabel(self.centro_form, text="Preço de Venda:", font=("Roboto", 12, "bold")).pack(anchor="w")
        self.ent_venda = self.criar_entry(self.centro_form, "Ex: 2.00")
        self.ent_venda.pack(pady=(0, 10))

        # Script 41: Refinamento de bindings para validação em tempo real
        self.ent_lote.bind("<KeyRelease>", self.validar_lote)
        self.ent_validade.bind("<KeyRelease>", self.formatar_data)
        self.ent_qnt.bind("<KeyRelease>", self.validar_estoque)
        self.ent_min.bind("<KeyRelease>", self.validar_estoque_minimo)
        
        # Prevenção de preenchimento de lixo nos campos de preço
        self.ent_custo.bind("<KeyRelease>", lambda e: self.validar_caracteres_preco(self.ent_custo))
        self.ent_venda.bind("<KeyRelease>", lambda e: self.validar_caracteres_preco(self.ent_venda))
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

    def validar_nome(self, event):
        """Script 41: Limita o nome a 50 caracteres em tempo real."""
        texto = self.ent_nome.get()
        if len(texto) > 50:
            self.ent_nome.delete(50, "end")
            self.mostrar_feedback("⚠️ Nome atingiu o limite de 50 caracteres.", "orange")

    def validar_categoria(self, event):
        """Script 41: Limita a categoria a 30 caracteres em tempo real."""
        texto = self.ent_categoria.get()
        if len(texto) > 30:
            self.ent_categoria.delete(30, "end")
            self.mostrar_feedback("⚠️ Categoria atingiu o limite de 30 caracteres.", "orange")

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

    def validar_caracteres_preco(self, entry):
        """Script 41: Permite apenas números, ponto e vírgula e limita o tamanho."""
        texto = entry.get()
        # Permite apenas dígitos, ponto e vírgula. Remove 'R$' se o usuário tentar colar.
        permitidos = "0123456789.,"
        limpo = "".join(filter(lambda x: x in permitidos, texto))
        
        if len(limpo) > 10:
            limpo = limpo[:10]
            self.mostrar_feedback("⚠️ Preço muito longo (máx. 10 caracteres).", "orange")
        elif texto != limpo:
            self.mostrar_feedback("⚠️ Apenas números e separadores no preço.", "orange")

        if texto != limpo:
            entry.delete(0, "end")
            entry.insert(0, limpo)

    def validar_lote(self, event):
        """Script 41: Limita o lote a 10 dígitos com feedback visual."""
        texto = self.ent_lote.get()
        limpo = "".join(filter(str.isdigit, texto))
        if len(limpo) > 10:
            limpo = limpo[:10]
            self.mostrar_feedback("⚠️ Limite do Lote: 10 dígitos.", "red")
        
        if texto != limpo:
            self.ent_lote.delete(0, "end")
            self.ent_lote.insert(0, limpo)

    def validar_estoque_minimo(self, event):
        """Script 41: Limita o estoque mínimo a 100 com feedback visual automático."""
        texto = self.ent_min.get()
        limpo = "".join(filter(str.isdigit, texto))
        
        excedeu = False
        if len(limpo) > 3:
            limpo = limpo[:3]
            excedeu = True
        
        if limpo and int(limpo) > 100:
            limpo = "100"
            excedeu = True
            
        if excedeu:
            self.mostrar_feedback("⚠️ Estoque mínimo não pode exceder 100.", "red")
        
        if texto != limpo:
            self.ent_min.delete(0, "end")
            self.ent_min.insert(0, limpo)

    def validar_estoque(self, event):
        """Script 41: Limita a quantidade em estoque a 100 com feedback visual automático."""
        texto = self.ent_qnt.get()
        limpo = "".join(filter(str.isdigit, texto))
        
        excedeu = False
        if len(limpo) > 3:
            limpo = limpo[:3]
            excedeu = True
            
        if limpo and int(limpo) > 100:
            limpo = "100"
            excedeu = True
            
        if excedeu:
            self.mostrar_feedback("⚠️ A quantidade não pode exceder 100 unidades.", "red")
            
        if texto != limpo:
            self.ent_qnt.delete(0, "end")
            self.ent_qnt.insert(0, limpo)

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
            # Script 41: Arredonda para 2 casas para evitar o "decimal infinito"
            return round(float(texto), 2)
        except:
            return 0.0

    def limpar_campos(self):
        self.ent_nome.delete(0, "end")
        self.ent_categoria.delete(0, "end")
        self.ent_lote.delete(0, "end")
        self.ent_validade.delete(0, "end")
        self.ent_qnt.delete(0, "end")
        self.ent_min.delete(0, "end")
        self.ent_min.insert(0, "20") # Script 41: Restaura o padrão de 20
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
        self.ent_min.delete(0, "end")
        self.ent_min.insert(0, str(self.produto_atual['estoque_minimo']))

        # Script 41: Formatação automática de preços ao carregar para edição (evita valores brutos como 1.0)
        c = self.produto_atual['preco_custo']
        v = self.produto_atual['preco_venda']
        self.ent_custo.insert(0, f"R$ {c:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        self.ent_venda.insert(0, f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

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

            # Script 41: Validação de preços irreais
            if dados["preco_custo"] <= 0:
                self.mostrar_feedback("❌ O Preço de Custo deve ser maior que zero.", "red")
                return
            
            if dados["preco_venda"] <= dados["preco_custo"]:
                self.mostrar_feedback("❌ Preço de Venda deve ser maior que o Custo.", "red")
                return

            if dados["estoque_minimo"] > 100 or len(str(dados["lote"])) > 10:
                self.mostrar_feedback("❌ Dados fora do limite (Min: 100 | Lote: 10)", "red")
                return

        except ValueError:
            messagebox.showwarning("Erro de Preenchimento", "Certifique-se que Quantidade e Preços são números válidos.")
            return

        if not dados["nome"] or not dados["validade"] or not dados["lote"] or not dados["categoria"]:
            messagebox.showwarning("Campos obrigatórios", "Preencha Nome, Categoria, Validade e Lote.")
            return

        # Script 36: Validação de data retroativa na interface
        try:
            val_dt = datetime.strptime(dados["validade"], "%d/%m/%Y").date()
            if val_dt < datetime.now().date():
                self.mostrar_feedback("🚫 Validade vencida! Operação não permitida.")
                return
        except ValueError:
            pass

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
                self.mostrar_feedback("❌ Falha na atualização (Limite 100 ou Validade).")
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
            else:
                self.mostrar_feedback("❌ Falha no cadastro (Limite 100 ou Validade).")