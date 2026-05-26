import customtkinter as ctk
from tkinter import messagebox
from database import (
    salvar_cliente, 
    buscar_cliente_por_id, 
    atualizar_cliente_db, 
    deletar_cliente_db
)

class JanelaClientes(ctk.CTkToplevel):
    def __init__(self, parent, perfil_usuario):
        super().__init__(parent)

        self.title("Cadastro de Clientes - Xô Sujeira")
        self.geometry("750x850")
        self.resizable(False, False)

        self.grab_set()
        self.focus()

        # Estado
        self.perfil = perfil_usuario
        self.id_cliente_editando = None
        self.cliente_atual = None

        # Título principal
        ctk.CTkLabel(self, text="Gerenciamento de Clientes", font=("Roboto", 28, "bold")).pack(pady=15)

        # Status/Feedback (Mesmo estilo do produtos.py)
        self.lbl_status = ctk.CTkLabel(self, text="", font=("Roboto", 14, "bold"))
        self.lbl_status.pack(pady=5)

        # --- FRAME DE BUSCA (TOPO) ---
        self.frame_busca = ctk.CTkFrame(self)
        self.frame_busca.pack(padx=20, pady=10, fill="x")
        
        ctk.CTkLabel(self.frame_busca, text="Localizar Cliente (ID):", font=("Roboto", 12, "bold")).pack(side="left", padx=10)
        
        self.ent_busca_id = ctk.CTkEntry(self.frame_busca, placeholder_text="ID...", width=150)
        self.ent_busca_id.pack(side="left", padx=5)
        self.ent_busca_id.bind("<KeyRelease>", lambda e: self.validar_apenas_numeros(self.ent_busca_id))

        self.btn_buscar = ctk.CTkButton(self.frame_busca, text="🔍 Buscar / Editar", width=140, command=self.buscar_cliente)
        self.btn_buscar.pack(side="left", padx=10)

        self.btn_cancelar = ctk.CTkButton(self.frame_busca, text="❌ Cancelar", width=100, fg_color="#444444", hover_color="#333333", command=self.limpar_campos)
        # O botão inicia oculto

        # --- SISTEMA DE ABAS PARA FORMULÁRIO ---
        self.tabview = ctk.CTkTabview(self, width=700, height=480)
        self.tabview.pack(padx=20, pady=10, fill="both", expand=True)
        
        self.tab_pf = self.tabview.add("Pessoa Física")
        self.tab_pj = self.tabview.add("Pessoa Jurídica")

        # --- UI PESSOA FÍSICA ---
        ctk.CTkLabel(self.tab_pf, text="Nome Completo:", font=("Roboto", 12, "bold")).pack(anchor="w", padx=150)
        self.ent_nome_pf = self.criar_entry(self.tab_pf, "Nome Completo"); self.ent_nome_pf.pack(pady=(0, 5))
        
        ctk.CTkLabel(self.tab_pf, text="CPF (Apenas números):", font=("Roboto", 12, "bold")).pack(anchor="w", padx=150)
        self.ent_cpf_pf = self.criar_entry(self.tab_pf, "CPF (Apenas números)"); self.ent_cpf_pf.pack(pady=(0, 5))
        
        ctk.CTkLabel(self.tab_pf, text="Telefone (XX) XXXXX-XXXX):", font=("Roboto", 12, "bold")).pack(anchor="w", padx=150)
        self.ent_telefone_pf = self.criar_entry(self.tab_pf, "Telefone (XX) XXXXX-XXXX"); self.ent_telefone_pf.pack(pady=(0, 5))
        
        ctk.CTkLabel(self.tab_pf, text="E-mail:", font=("Roboto", 12, "bold")).pack(anchor="w", padx=150)
        self.ent_email_pf = self.criar_entry(self.tab_pf, "E-mail"); self.ent_email_pf.pack(pady=(0, 5))
        
        self.frame_end_pf = ctk.CTkFrame(self.tab_pf, fg_color="transparent")
        self.frame_end_pf.pack(pady=5)
        
        ctk.CTkLabel(self.frame_end_pf, text="Rua/Avenida:", font=("Roboto", 12, "bold")).grid(row=0, column=0, padx=5, sticky="w")
        self.ent_rua_pf = self.criar_entry(self.frame_end_pf, "Rua/Avenida", 220); self.ent_rua_pf.grid(row=1, column=0, padx=5)
        
        ctk.CTkLabel(self.frame_end_pf, text="Bairro:", font=("Roboto", 12, "bold")).grid(row=0, column=1, padx=5, sticky="w")
        self.ent_bairro_pf = self.criar_entry(self.frame_end_pf, "Bairro", 220); self.ent_bairro_pf.grid(row=1, column=1, padx=5)
        
        ctk.CTkLabel(self.frame_end_pf, text="Cidade:", font=("Roboto", 12, "bold")).grid(row=2, column=0, padx=5, pady=(5,0), sticky="w")
        self.ent_cidade_pf = self.criar_entry(self.frame_end_pf, "Cidade", 220); self.ent_cidade_pf.grid(row=3, column=0, padx=5, pady=(0,5))
        
        ctk.CTkLabel(self.frame_end_pf, text="Complemento:", font=("Roboto", 12, "bold")).grid(row=2, column=1, padx=5, pady=(5,0), sticky="w")
        self.ent_comp_pf = self.criar_entry(self.frame_end_pf, "Complemento", 220); self.ent_comp_pf.grid(row=3, column=1, padx=5, pady=(0,5))

        # Bindings para Script 25 (Máscaras e Validações PF)
        self.ent_telefone_pf.bind("<KeyRelease>", lambda e: self.formatar_telefone_generico(self.ent_telefone_pf))
        self.ent_cpf_pf.bind("<KeyRelease>", self.formatar_cpf)

        # --- UI PESSOA JURÍDICA ---
        ctk.CTkLabel(self.tab_pj, text="Nome Fantasia:", font=("Roboto", 12, "bold")).pack(anchor="w", padx=150)
        self.ent_nome_pj = self.criar_entry(self.tab_pj, "Nome Fantasia"); self.ent_nome_pj.pack(pady=(0, 5))
        ctk.CTkLabel(self.tab_pj, text="Razão Social:", font=("Roboto", 12, "bold")).pack(anchor="w", padx=150)
        self.ent_razao_pj = self.criar_entry(self.tab_pj, "Razão Social"); self.ent_razao_pj.pack(pady=(0, 5))
        ctk.CTkLabel(self.tab_pj, text="CNPJ (Apenas números):", font=("Roboto", 12, "bold")).pack(anchor="w", padx=150)
        self.ent_cnpj_pj = self.criar_entry(self.tab_pj, "CNPJ (Apenas números)"); self.ent_cnpj_pj.pack(pady=(0, 5))
        ctk.CTkLabel(self.tab_pj, text="Telefone:", font=("Roboto", 12, "bold")).pack(anchor="w", padx=150)
        self.ent_telefone_pj = self.criar_entry(self.tab_pj, "Telefone"); self.ent_telefone_pj.pack(pady=(0, 5))
        ctk.CTkLabel(self.tab_pj, text="E-mail:", font=("Roboto", 12, "bold")).pack(anchor="w", padx=150)
        self.ent_email_pj = self.criar_entry(self.tab_pj, "E-mail"); self.ent_email_pj.pack(pady=(0, 5))

        self.frame_end_pj = ctk.CTkFrame(self.tab_pj, fg_color="transparent")
        self.frame_end_pj.pack(pady=5)
        
        ctk.CTkLabel(self.frame_end_pj, text="Rua/Avenida:", font=("Roboto", 12, "bold")).grid(row=0, column=0, padx=5, sticky="w")
        self.ent_rua_pj = self.criar_entry(self.frame_end_pj, "Rua/Avenida", 220); self.ent_rua_pj.grid(row=1, column=0, padx=5)
        
        ctk.CTkLabel(self.frame_end_pj, text="Bairro:", font=("Roboto", 12, "bold")).grid(row=0, column=1, padx=5, sticky="w")
        self.ent_bairro_pj = self.criar_entry(self.frame_end_pj, "Bairro", 220); self.ent_bairro_pj.grid(row=1, column=1, padx=5)
        
        ctk.CTkLabel(self.frame_end_pj, text="Cidade:", font=("Roboto", 12, "bold")).grid(row=2, column=0, padx=5, pady=(5,0), sticky="w")
        self.ent_cidade_pj = self.criar_entry(self.frame_end_pj, "Cidade", 220); self.ent_cidade_pj.grid(row=3, column=0, padx=5, pady=(0,5))
        
        ctk.CTkLabel(self.frame_end_pj, text="Complemento:", font=("Roboto", 12, "bold")).grid(row=2, column=1, padx=5, pady=(5,0), sticky="w")
        self.ent_comp_pj = self.criar_entry(self.frame_end_pj, "Complemento", 220); self.ent_comp_pj.grid(row=3, column=1, padx=5, pady=(0,5))

        # Bindings para Script 27 (Máscaras e Validações PJ)
        self.ent_telefone_pj.bind("<KeyRelease>", lambda e: self.formatar_telefone_generico(self.ent_telefone_pj))
        self.ent_cnpj_pj.bind("<KeyRelease>", self.formatar_cnpj)

        # --- FRAME DE AÇÕES (BOTÕES) ---
        self.frame_acoes = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_acoes.pack(pady=15)

        self.btn_salvar = ctk.CTkButton(self.frame_acoes, text="💾 Salvar / Atualizar", height=45, font=("Roboto", 15, "bold"), fg_color="green", command=self.validar_e_salvar_contextual)
        self.btn_salvar.pack(side="left", padx=10)

        self.btn_limpar = ctk.CTkButton(self.frame_acoes, text="🧹 Limpar", height=45, font=("Roboto", 15, "bold"), fg_color="gray", command=self.limpar_campos)
        self.btn_limpar.pack(side="left", padx=10)

        self.btn_excluir = ctk.CTkButton(self.frame_acoes, text="🗑️ Excluir", height=45, font=("Roboto", 15, "bold"), fg_color="red", state="disabled", command=self.confirmar_exclusao)
        self.btn_excluir.pack(side="left", padx=10)

        # Área de log/detalhes
        self.txt_resultado = ctk.CTkTextbox(self, width=650, height=100, font=("Roboto", 12))
        self.txt_resultado.pack(pady=10, padx=20)
        self.txt_resultado.insert("0.0", "Informações adicionais do cliente aparecerão aqui...")
        self.txt_resultado.configure(state="disabled")

    def mostrar_feedback(self, mensagem, cor="red"):
        self.lbl_status.configure(text=mensagem, text_color=cor)
        self.after(3500, lambda: self.lbl_status.configure(text=""))

    def criar_entry(self, master, texto, largura=450):
        return ctk.CTkEntry(
            master,
            placeholder_text=texto,
            width=largura,
            height=40,
            corner_radius=10
        )

    # --- MÉTODOS DE FORMATAÇÃO (SCRIPT 25) ---

    def validar_apenas_numeros(self, entry):
        texto = entry.get()
        limpo = "".join(filter(str.isdigit, texto))
        if texto != limpo:
            entry.delete(0, "end")
            entry.insert(0, limpo)
        return limpo

    def formatar_telefone(self, event):
        if event.keysym == "BackSpace": return
        nums = self.validar_apenas_numeros(self.ent_telefone_pf)
        if len(nums) > 11: nums = nums[:11]
        
        f = ""
        if len(nums) > 0: f += "(" + nums[:2]
        if len(nums) > 2: f += ") " + nums[2:6]
        if len(nums) > 6:
            if len(nums) == 11: # Celular
                f = f"({nums[:2]}) {nums[2:7]}-{nums[7:]}"
            else: # Fixo
                f = f"({nums[:2]}) {nums[2:6]}-{nums[6:]}"
        
        self.ent_telefone_pf.delete(0, "end")
        self.ent_telefone_pf.insert(0, f)

    def formatar_cpf(self, event):
        if event.keysym == "BackSpace": return
        nums = self.validar_apenas_numeros(self.ent_cpf_pf)
        if len(nums) > 11: nums = nums[:11]
        
        f = ""
        for i, n in enumerate(nums):
            if i in [3, 6]: f += "."
            if i == 9: f += "-"
            f += n
        
        self.ent_cpf_pf.delete(0, "end")
        self.ent_cpf_pf.insert(0, f)

    def formatar_telefone_generico(self, event_or_entry):
        # Pode ser chamado via Bind (event) ou manualmente (entry)
        entry = event_or_entry if isinstance(event_or_entry, ctk.CTkEntry) else event_or_entry.widget
        if hasattr(event_or_entry, 'keysym') and event_or_entry.keysym == "BackSpace": return
        
        nums = "".join(filter(str.isdigit, entry.get()))
        if len(nums) > 11: nums = nums[:11]
        f = ""
        if len(nums) > 0: f += "(" + nums[:2]
        if len(nums) > 2: f += ") " + nums[2:6]
        if len(nums) > 6: f = f"({nums[:2]}) {nums[2:7]}-{nums[7:]}" if len(nums) == 11 else f"({nums[:2]}) {nums[2:6]}-{nums[6:]}"

        entry.delete(0, "end")
        entry.insert(0, f)

    def formatar_cnpj(self, event):
        if event.keysym == "BackSpace": return
        nums = self.validar_apenas_numeros(self.ent_cnpj_pj)
        if len(nums) > 14: nums = nums[:14]
        
        f = ""
        for i, n in enumerate(nums):
            if i == 2: f += "."
            elif i == 5: f += "."
            elif i == 8: f += "/"
            elif i == 12: f += "-"
            f += n
        
        self.ent_cnpj_pj.delete(0, "end")
        self.ent_cnpj_pj.insert(0, f)

    def limpar_campos(self):
        for e in [self.ent_nome_pf, self.ent_rua_pf, self.ent_bairro_pf, self.ent_cidade_pf, self.ent_comp_pf,
                  self.ent_telefone_pf, self.ent_cpf_pf, self.ent_email_pf,
                  self.ent_nome_pj, self.ent_razao_pj, self.ent_cnpj_pj, self.ent_rua_pj, self.ent_bairro_pj, 
                  self.ent_cidade_pj, self.ent_comp_pj, self.ent_telefone_pj, self.ent_email_pj]:
            e.delete(0, "end")
        
        self.ent_busca_id.delete(0, "end")
        self.btn_cancelar.pack_forget()
        
        self.txt_resultado.configure(state="normal")
        self.txt_resultado.delete("1.0", "end")
        self.txt_resultado.insert("0.0", "Informações adicionais do cliente aparecerão aqui...")
        self.txt_resultado.configure(state="disabled")

        self.id_cliente_editando = None
        self.btn_salvar.configure(text="💾 Salvar / Atualizar", fg_color="green", state="normal")
        self.btn_excluir.configure(state="disabled")

    def buscar_cliente(self):
        id_digitado = self.ent_busca_id.get()
        if not id_digitado:
            self.mostrar_feedback("⚠️ Informe um ID.")
            return

        cliente = buscar_cliente_por_id(id_digitado)
        self.cliente_atual = cliente

        if cliente:
            self.preparar_edicao()
            self.btn_cancelar.pack(side="left", padx=5) 
            
            self.txt_resultado.configure(state="normal")
            self.txt_resultado.delete("1.0", "end")
            info = f"CLIENTE ENCONTRADO:\n\n"
            info += f"ID: {cliente['id']} | Nome: {cliente['nome']}\n"
            info += f"CPF: {cliente['cpf']}\nCNPJ: {cliente['cnpj']}\nEmail: {cliente['email']}"
            self.txt_resultado.insert("0.0", info)
            self.txt_resultado.configure(state="disabled")
            
            self.mostrar_feedback("✅ Cliente carregado para edição!", "green")
        else:
            self.btn_excluir.configure(state="disabled")
            self.mostrar_feedback("❌ Cliente não encontrado.")
            self.limpar_campos()

    def preparar_edicao(self):
        if not self.cliente_atual: return
        
        self.id_cliente_editando = self.cliente_atual['id']
        
        # Identificar se é PF ou PJ pela existência de CPF
        if self.cliente_atual['cpf'] and self.cliente_atual['cpf'].strip() != "":
            self.tabview.set("Pessoa Física")
            self.ent_nome_pf.delete(0, "end"); self.ent_nome_pf.insert(0, self.cliente_atual['nome'])
            self.ent_cpf_pf.delete(0, "end"); self.ent_cpf_pf.insert(0, self.cliente_atual['cpf'])
            self.ent_telefone_pf.delete(0, "end"); self.ent_telefone_pf.insert(0, self.cliente_atual['telefone'])
            self.ent_email_pf.delete(0, "end"); self.ent_email_pf.insert(0, self.cliente_atual['email'])
            self.ent_rua_pf.delete(0, "end"); self.ent_rua_pf.insert(0, self.cliente_atual['endereco'])
        else:
            self.tabview.set("Pessoa Jurídica")
            self.ent_nome_pj.delete(0, "end"); self.ent_nome_pj.insert(0, self.cliente_atual['nome'])
            self.ent_razao_pj.delete(0, "end"); self.ent_razao_pj.insert(0, self.cliente_atual['razao_social'] or "")
            self.ent_cnpj_pj.delete(0, "end"); self.ent_cnpj_pj.insert(0, self.cliente_atual['cnpj'] or "")
            self.ent_telefone_pj.delete(0, "end"); self.ent_telefone_pj.insert(0, self.cliente_atual['telefone'])
            self.ent_email_pj.delete(0, "end"); self.ent_email_pj.insert(0, self.cliente_atual['email'])
            self.ent_rua_pj.delete(0, "end"); self.ent_rua_pj.insert(0, self.cliente_atual['endereco'])

        self.btn_salvar.configure(text="🔄 Atualizar Cliente", fg_color="blue")

    def confirmar_exclusao(self):
        if self.cliente_atual and messagebox.askyesno("Confirmar Exclusão", f"Deseja excluir o cliente {self.cliente_atual['nome']}?"):
            if deletar_cliente_db(self.cliente_atual['id']):
                self.mostrar_feedback("🗑️ Cliente removido!", "orange")
                self.limpar_campos()

    def validar_e_salvar_contextual(self):
        # Decide qual aba está ativa para pegar os dados
        tipo = "PF" if self.tabview.get() == "Pessoa Física" else "PJ"
        self.validar_e_salvar(tipo)

    def validar_e_salvar(self, tipo):
        if tipo == "PF":
            rua, bairro, cidade, comp = self.ent_rua_pf.get(), self.ent_bairro_pf.get(), self.ent_cidade_pf.get(), self.ent_comp_pf.get()
            # Se for edição e o campo Bairro/Cidade estiver vazio (porque carregamos o endereço todo na Rua), 
            # mantemos apenas o que está na Rua.
            if bairro or cidade:
                endereco_completo = f"{rua}, {bairro}, {cidade} - {comp}".strip(", -")
            else:
                endereco_completo = rua

            dados = {
                "nome": self.ent_nome_pf.get(),
                "endereco": endereco_completo,
                "telefone": self.ent_telefone_pf.get(),
                "cpf": self.ent_cpf_pf.get(),
                "cnpj": "",
                "razao_social": "",
                "email": self.ent_email_pf.get()
            }
        else:
            rua, bairro, cidade, comp = self.ent_rua_pj.get(), self.ent_bairro_pj.get(), self.ent_cidade_pj.get(), self.ent_comp_pj.get()
            if bairro or cidade:
                endereco_completo_pj = f"{rua}, {bairro}, {cidade} - {comp}".strip(", -")
            else:
                endereco_completo_pj = rua

            dados = {
                "nome": self.ent_nome_pj.get(),
                "endereco": endereco_completo_pj,
                "telefone": self.ent_telefone_pj.get(),
                "cpf": "",
                "cnpj": self.ent_cnpj_pj.get(),
                "razao_social": self.ent_razao_pj.get(),
                "email": self.ent_email_pj.get()
            }

        if not dados["nome"] or not dados["telefone"] or not dados["email"]:
            self.mostrar_feedback("⚠️ Nome, Telefone e E-mail são obrigatórios.")
            return

        if "@" not in dados["email"]:
            self.mostrar_feedback("❌ E-mail inválido (falta '@').")
            return

        if self.id_cliente_editando:
            if atualizar_cliente_db(self.id_cliente_editando, **dados):
                self.mostrar_feedback(f"✅ Cliente '{dados['nome']}' atualizado!", "green")
                self.limpar_campos()
        else:
            id_gerado = salvar_cliente(**dados)
            if id_gerado:
                self.mostrar_feedback(f"✅ Cadastrado com ID: {id_gerado}", "green")
                self.limpar_campos()

# Removida a JanelaClientesPF duplicada ao final para manter o CRUD em uma janela única coerente.