import customtkinter as ctk
from tkinter import messagebox
from database import (
    salvar_cliente, 
    buscar_cliente_por_id, 
    atualizar_cliente_db, 
    deletar_cliente_db
)

class JanelaClientes(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("Cadastro de Clientes - Xô Sujeira")
        self.geometry("700x750")
        self.resizable(False, False)

        self.grab_set()
        self.focus()

        self.id_cliente_editando = None
        self.cliente_atual = None

        self.label_titulo = ctk.CTkLabel(
            self,
            text="Gerenciamento de Clientes",
            font=("Roboto", 28, "bold")
        )
        self.label_titulo.pack(pady=20)

        # Criação das Abas (Tabs)
        self.tabview = ctk.CTkTabview(self, width=650, height=600)
        self.tabview.pack(padx=20, pady=10, fill="both", expand=True)
        
        self.tab_pf = self.tabview.add("Pessoa Física")
        self.tab_pj = self.tabview.add("Pessoa Jurídica")
        self.tab_busca = self.tabview.add("Buscar Cliente")

        # --- UI PESSOA FÍSICA ---
        self.ent_nome_pf = self.criar_entry(self.tab_pf, "Nome Completo")
        self.ent_rua_pf = self.criar_entry(self.tab_pf, "Rua/Avenida")
        self.ent_bairro_pf = self.criar_entry(self.tab_pf, "Bairro")
        self.ent_cidade_pf = self.criar_entry(self.tab_pf, "Cidade")
        self.ent_comp_pf = self.criar_entry(self.tab_pf, "Complemento")
        self.ent_telefone_pf = self.criar_entry(self.tab_pf, "Telefone")
        self.ent_cpf_pf = self.criar_entry(self.tab_pf, "CPF")
        self.ent_email_pf = self.criar_entry(self.tab_pf, "E-mail")

        for entry in [self.ent_nome_pf, self.ent_rua_pf, self.ent_bairro_pf, self.ent_cidade_pf, self.ent_comp_pf, 
                      self.ent_telefone_pf, self.ent_cpf_pf, self.ent_email_pf]:
            entry.pack(pady=8)

        # Bindings para Script 25 (Máscaras e Validações PF)
        self.ent_telefone_pf.bind("<KeyRelease>", self.formatar_telefone)
        self.ent_cpf_pf.bind("<KeyRelease>", self.formatar_cpf)

        self.btn_salvar_pf = ctk.CTkButton(
            self.tab_pf,
            text="Salvar Pessoa Física",
            height=45,
            font=("Roboto", 16, "bold"),
            fg_color="green",
            command=lambda: self.validar_e_salvar("PF")
        )
        self.btn_salvar_pf.pack(pady=20)

        # --- UI PESSOA JURÍDICA ---
        self.ent_nome_pj = self.criar_entry(self.tab_pj, "Nome Fantasia")
        self.ent_razao_pj = self.criar_entry(self.tab_pj, "Razão Social")
        self.ent_cnpj_pj = self.criar_entry(self.tab_pj, "CNPJ")
        self.ent_rua_pj = self.criar_entry(self.tab_pj, "Rua/Avenida")
        self.ent_bairro_pj = self.criar_entry(self.tab_pj, "Bairro")
        self.ent_cidade_pj = self.criar_entry(self.tab_pj, "Cidade")
        self.ent_comp_pj = self.criar_entry(self.tab_pj, "Complemento")
        self.ent_telefone_pj = self.criar_entry(self.tab_pj, "Telefone")
        self.ent_email_pj = self.criar_entry(self.tab_pj, "E-mail")

        for entry in [self.ent_nome_pj, self.ent_razao_pj, self.ent_cnpj_pj, self.ent_rua_pj, self.ent_bairro_pj, 
                      self.ent_cidade_pj, self.ent_comp_pj, self.ent_telefone_pj, self.ent_email_pj]:
            entry.pack(pady=8)

        # Bindings para Script 27 (Máscaras e Validações PJ)
        self.ent_telefone_pj.bind("<KeyRelease>", lambda e: self.formatar_telefone_generico(self.ent_telefone_pj))
        self.ent_cnpj_pj.bind("<KeyRelease>", self.formatar_cnpj)

        self.btn_salvar_pj = ctk.CTkButton(
            self.tab_pj,
            text="Salvar Pessoa Jurídica",
            height=45,
            font=("Roboto", 16, "bold"),
            fg_color="green",
            command=lambda: self.validar_e_salvar("PJ")
        )
        self.btn_salvar_pj.pack(pady=20)

        # --- Botão Limpar Global (em ambas as abas de cadastro) ---
        self.btn_limpar = ctk.CTkButton(
            self,
            text="Limpar Formulário",
            height=45,
            font=("Roboto", 16, "bold"),
            fg_color="gray",
            command=self.limpar_campos
        )
        self.btn_limpar.pack(pady=10)

        # --- UI DA ABA BUSCA ---
        
        self.frame_busca = ctk.CTkFrame(self.tab_busca, fg_color="transparent")
        self.frame_busca.pack(pady=20, padx=20, fill="x")

        self.ent_busca_id = ctk.CTkEntry(
            self.frame_busca, 
            placeholder_text="Digite o ID do cliente...",
            width=300,
            height=40
        )
        self.ent_busca_id.pack(side="left", padx=10)
        self.ent_busca_id.bind("<KeyRelease>", lambda e: self.validar_apenas_numeros(self.ent_busca_id))

        self.btn_buscar = ctk.CTkButton(
            self.frame_busca,
            text="Buscar",
            width=100,
            height=40,
            command=self.buscar_cliente
        )
        self.btn_buscar.pack(side="left")

        # Script 19: Botão adicional para cadastro simplificado PF
        self.btn_novo_pf = ctk.CTkButton(
            self.frame_busca,
            text="+ Novo PF",
            width=100,
            height=40,
            fg_color="teal",
            command=lambda: JanelaClientesPF(self)
        )
        self.btn_novo_pf.pack(side="left", padx=10)

        self.txt_resultado = ctk.CTkTextbox(
            self.tab_busca,
            width=550,
            height=300,
            font=("Roboto", 14)
        )
        self.txt_resultado.pack(pady=20, padx=20)
        self.txt_resultado.insert("0.0", "Os detalhes do cliente aparecerão aqui...")
        self.txt_resultado.configure(state="disabled")

        # Sprints 11 e 12: Botões de Ação na Busca
        self.frame_acoes_busca = ctk.CTkFrame(self.tab_busca, fg_color="transparent")
        self.frame_acoes_busca.pack(pady=10)

        self.btn_editar = ctk.CTkButton(
            self.frame_acoes_busca,
            text="Editar Cliente",
            state="disabled",
            command=self.preparar_edicao
        )
        self.btn_editar.pack(side="left", padx=10)

        self.btn_excluir = ctk.CTkButton(
            self.frame_acoes_busca,
            text="Excluir Cliente",
            state="disabled",
            fg_color="red",
            hover_color="darkred",
            command=self.confirmar_exclusao
        )
        self.btn_excluir.pack(side="left", padx=10)

    def criar_entry(self, master, texto):
        return ctk.CTkEntry(
            master,
            placeholder_text=texto,
            width=450,
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

    def formatar_telefone_generico(self, entry):
        nums = self.validar_apenas_numeros(entry)
        if len(nums) > 11: nums = nums[:11]
        
        f = ""
        if len(nums) > 0: f += "(" + nums[:2]
        if len(nums) > 2: f += ") " + nums[2:6]
        if len(nums) > 6:
            if len(nums) == 11: # Celular
                f = f"({nums[:2]}) {nums[2:7]}-{nums[7:]}"
            else: # Fixo
                f = f"({nums[:2]}) {nums[2:6]}-{nums[6:]}"
        
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
        
        self.id_cliente_editando = None
        self.btn_salvar_pf.configure(text="Salvar Pessoa Física", fg_color="green")
        self.btn_salvar_pj.configure(text="Salvar Pessoa Jurídica", fg_color="green")

    def buscar_cliente(self):
        id_digitado = self.ent_busca_id.get()
        cliente = buscar_cliente_por_id(id_digitado)
        self.cliente_atual = cliente
        
        self.txt_resultado.configure(state="normal")
        self.txt_resultado.delete("1.0", "end")
        
        if cliente:
            self.btn_editar.configure(state="normal")
            self.btn_excluir.configure(state="normal")
            info = f"CLIENTE ENCONTRADO:\n\nID: {cliente['id']}\nNome: {cliente['nome']}\nEndereço: {cliente['endereco']}\nTelefone: {cliente['telefone']}\n"
            info += f"CPF: {cliente['cpf']}\nCNPJ: {cliente['cnpj']}\nEmail: {cliente['email']}"
            self.txt_resultado.insert("0.0", info)
        else:
            self.btn_editar.configure(state="disabled")
            self.btn_excluir.configure(state="disabled")
            self.txt_resultado.insert("0.0", "Cliente não encontrado.")
        self.txt_resultado.configure(state="disabled")

    def preparar_edicao(self):
        if self.cliente_atual:
            self.limpar_campos()
            self.id_cliente_editando = self.cliente_atual['id']
            
            if self.cliente_atual['cpf']:
                self.tabview.set("Pessoa Física")
                self.ent_nome_pf.insert(0, self.cliente_atual['nome'])
                # Para edição, insere o endereço completo no campo Rua e permite ajuste
                self.ent_rua_pf.insert(0, self.cliente_atual['endereco'])
                self.ent_telefone_pf.insert(0, self.cliente_atual['telefone'])
                self.ent_cpf_pf.insert(0, self.cliente_atual['cpf'])
                self.ent_email_pf.insert(0, self.cliente_atual['email'])
                self.btn_salvar_pf.configure(text="Atualizar PF", fg_color="blue")
            else:
                self.tabview.set("Pessoa Jurídica")
                self.ent_nome_pj.insert(0, self.cliente_atual['nome'])
                self.ent_razao_pj.insert(0, self.cliente_atual['razao_social'] or "")
                self.ent_cnpj_pj.insert(0, self.cliente_atual['cnpj'] or "")
                self.ent_rua_pj.insert(0, self.cliente_atual['endereco'])
                self.ent_telefone_pj.insert(0, self.cliente_atual['telefone'])
                self.ent_email_pj.insert(0, self.cliente_atual['email'])
                self.btn_salvar_pj.configure(text="Atualizar PJ", fg_color="blue")

    def confirmar_exclusao(self):
        if self.cliente_atual and messagebox.askyesno("Confirmar Exclusão", f"Deseja excluir o cliente {self.cliente_atual['nome']}?"):
            if deletar_cliente_db(self.cliente_atual['id']):
                messagebox.showinfo("Sucesso", "Cliente removido com sucesso.")
                self.limpar_campos()
                self.ent_busca_id.delete(0, "end")
                self.txt_resultado.configure(state="normal")
                self.txt_resultado.delete("1.0", "end")
                self.txt_resultado.insert("0.0", "Os detalhes do cliente aparecerão aqui...")
                self.txt_resultado.configure(state="disabled")

    def validar_e_salvar(self, tipo):
        if tipo == "PF":
            # Script 25: Junção do endereço e novos campos
            rua, bairro, cidade, comp = self.ent_rua_pf.get(), self.ent_bairro_pf.get(), self.ent_cidade_pf.get(), self.ent_comp_pf.get()
            endereco_completo = f"{rua}, {bairro}, {cidade} - {comp}".strip(", -")
            
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
            # Script 27: Junção do endereço PJ
            rua, bairro, cidade, comp = self.ent_rua_pj.get(), self.ent_bairro_pj.get(), self.ent_cidade_pj.get(), self.ent_comp_pj.get()
            endereco_completo_pj = f"{rua}, {bairro}, {cidade} - {comp}".strip(", -")

            dados = {
                "nome": self.ent_nome_pj.get(),
                "endereco": endereco_completo_pj,
                "telefone": self.ent_telefone_pj.get(),
                "cpf": "",
                "cnpj": self.ent_cnpj_pj.get(),
                "razao_social": self.ent_razao_pj.get(),
                "email": self.ent_email_pj.get()
            }

        if not all([dados["nome"], dados["endereco"], dados["telefone"], dados["email"]]):
            messagebox.showwarning("Campos Obrigatórios", "Nome, Endereço, Telefone e E-mail são obrigatórios.")
            return

        # Script 25: Validação de E-mail
        if "@" not in dados["email"]:
            messagebox.showwarning("E-mail Inválido", "O campo e-mail deve conter '@'.")
            return

        if self.id_cliente_editando:
            if atualizar_cliente_db(self.id_cliente_editando, **dados):
                messagebox.showinfo("Sucesso", "Cadastro atualizado!")
                self.limpar_campos()
                self.tabview.set("Buscar Cliente")
        else:
            id_gerado = salvar_cliente(**dados)
            if id_gerado:
                messagebox.showinfo("Sucesso", f"Cadastrado com ID {id_gerado}.")
                self.limpar_campos()

# --- Script 26: Mesclagem do módulo de interface PF (ex-clientes_pf_ui.py) ---

class JanelaClientesPF(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("Cadastro de Cliente Pessoa Física - Xô Sujeira")
        self.geometry("550x650")
        self.resizable(False, False)

        self.grab_set()
        self.focus()

        self.label_titulo = ctk.CTkLabel(
            self, 
            text="Cadastro Simplificado (PF)", 
            font=("Roboto", 24, "bold")
        )
        self.label_titulo.pack(pady=20)

        self.ent_nome = self.criar_entry("Nome Completo")
        self.ent_cpf = self.criar_entry("CPF")
        self.ent_telefone = self.criar_entry("Telefone de Contato")
        self.ent_email = self.criar_entry("E-mail")
        self.ent_endereco = self.criar_entry("Endereço de Entrega")

        for entry in [self.ent_nome, self.ent_cpf, self.ent_telefone, self.ent_email, self.ent_endereco]:
            entry.pack(pady=10)

        # Script 26: Mantendo a coerência com as máscaras do Script 25
        self.ent_cpf.bind("<KeyRelease>", self.formatar_cpf)
        self.ent_telefone.bind("<KeyRelease>", self.formatar_telefone)

        self.btn_salvar = ctk.CTkButton(
            self,
            text="Cadastrar Cliente PF",
            height=45,
            font=("Roboto", 16, "bold"),
            fg_color="green",
            hover_color="darkgreen",
            command=self.validar_e_salvar
        )
        self.btn_salvar.pack(pady=30)

    def criar_entry(self, placeholder):
        return ctk.CTkEntry(
            self, 
            placeholder_text=placeholder, 
            width=400, 
            height=40,
            corner_radius=10
        )

    def validar_apenas_numeros(self, entry):
        texto = entry.get()
        limpo = "".join(filter(str.isdigit, texto))
        if texto != limpo:
            entry.delete(0, "end")
            entry.insert(0, limpo)
        return limpo

    def formatar_cpf(self, event):
        if event.keysym == "BackSpace": return
        nums = self.validar_apenas_numeros(self.ent_cpf)
        if len(nums) > 11: nums = nums[:11]
        f = ""
        for i, n in enumerate(nums):
            if i in [3, 6]: f += "."
            if i == 9: f += "-"
            f += n
        self.ent_cpf.delete(0, "end")
        self.ent_cpf.insert(0, f)

    def formatar_telefone(self, event):
        if event.keysym == "BackSpace": return
        nums = self.validar_apenas_numeros(self.ent_telefone)
        if len(nums) > 11: nums = nums[:11]
        f = ""
        if len(nums) > 0: f += "(" + nums[:2]
        if len(nums) > 2: f += ") " + nums[2:6]
        if len(nums) > 6:
            if len(nums) == 11: f = f"({nums[:2]}) {nums[2:7]}-{nums[7:]}"
            else: f = f"({nums[:2]}) {nums[2:6]}-{nums[6:]}"
        self.ent_telefone.delete(0, "end")
        self.ent_telefone.insert(0, f)

    def validar_e_salvar(self):
        nome = self.ent_nome.get()
        cpf = self.ent_cpf.get()
        tel = self.ent_telefone.get()
        email = self.ent_email.get()
        end = self.ent_endereco.get()

        if not all([nome, cpf, tel, email, end]):
            messagebox.showwarning("Atenção", "Todos os campos são obrigatórios.")
            return

        if "@" not in email:
            messagebox.showwarning("E-mail Inválido", "O campo e-mail deve conter '@'.")
            return

        # Chamada corrigida com 8 argumentos para manter coerência com database.py
        id_gerado = salvar_cliente(
            nome=nome, 
            endereco=end, 
            telefone=tel, 
            cpf=cpf, 
            cnpj="", 
            razao_social="", 
            email=email
        )
        
        if id_gerado:
            messagebox.showinfo("Sucesso", f"Cliente PF cadastrado!\nID: {id_gerado}")
            self.destroy()