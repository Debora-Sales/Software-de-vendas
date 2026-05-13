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
        self.ent_endereco_pf = self.criar_entry(self.tab_pf, "Endereço")
        self.ent_telefone_pf = self.criar_entry(self.tab_pf, "Telefone")
        self.ent_cpf_pf = self.criar_entry(self.tab_pf, "CPF")
        self.ent_email_pf = self.criar_entry(self.tab_pf, "E-mail")

        for entry in [self.ent_nome_pf, self.ent_endereco_pf, self.ent_telefone_pf, self.ent_cpf_pf, self.ent_email_pf]:
            entry.pack(pady=8)

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
        self.ent_endereco_pj = self.criar_entry(self.tab_pj, "Endereço Comercial")
        self.ent_telefone_pj = self.criar_entry(self.tab_pj, "Telefone")
        self.ent_email_pj = self.criar_entry(self.tab_pj, "E-mail")

        for entry in [self.ent_nome_pj, self.ent_razao_pj, self.ent_cnpj_pj, self.ent_endereco_pj, self.ent_telefone_pj, self.ent_email_pj]:
            entry.pack(pady=8)

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

        self.btn_buscar = ctk.CTkButton(
            self.frame_busca,
            text="Buscar",
            width=100,
            height=40,
            command=self.buscar_cliente
        )
        self.btn_buscar.pack(side="left")

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

    def limpar_campos(self):
        for e in [self.ent_nome_pf, self.ent_endereco_pf, self.ent_telefone_pf, self.ent_cpf_pf, self.ent_email_pf,
                  self.ent_nome_pj, self.ent_razao_pj, self.ent_cnpj_pj, self.ent_endereco_pj, self.ent_telefone_pj, self.ent_email_pj]:
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
            info = f"CLIENTE ENCONTRADO:\n\nID: {cliente['id']}\nNome: {cliente['nome']}\nEndereço: {cliente['endereco']}\nTelefone: {cliente['telefone']}\nCPF: {cliente['cpf']}\nCNPJ: {cliente['cnpj']}\nEmail: {cliente['email']}"
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
                self.ent_endereco_pf.insert(0, self.cliente_atual['endereco'])
                self.ent_telefone_pf.insert(0, self.cliente_atual['telefone'])
                self.ent_cpf_pf.insert(0, self.cliente_atual['cpf'])
                self.ent_email_pf.insert(0, self.cliente_atual['email'])
                self.btn_salvar_pf.configure(text="Atualizar PF", fg_color="blue")
            else:
                self.tabview.set("Pessoa Jurídica")
                self.ent_nome_pj.insert(0, self.cliente_atual['nome'])
                self.ent_razao_pj.insert(0, self.cliente_atual['razao_social'] or "")
                self.ent_cnpj_pj.insert(0, self.cliente_atual['cnpj'] or "")
                self.ent_endereco_pj.insert(0, self.cliente_atual['endereco'])
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
            dados = {
                "nome": self.ent_nome_pf.get(),
                "endereco": self.ent_endereco_pf.get(),
                "telefone": self.ent_telefone_pf.get(),
                "cpf": self.ent_cpf_pf.get(),
                "cnpj": "",
                "razao_social": "",
                "email": self.ent_email_pf.get()
            }
        else:
            dados = {
                "nome": self.ent_nome_pj.get(),
                "endereco": self.ent_endereco_pj.get(),
                "telefone": self.ent_telefone_pj.get(),
                "cpf": "",
                "cnpj": self.ent_cnpj_pj.get(),
                "razao_social": self.ent_razao_pj.get(),
                "email": self.ent_email_pj.get()
            }

        if not all([dados["nome"], dados["endereco"], dados["telefone"], dados["email"]]):
            messagebox.showwarning("Campos Obrigatórios", "Nome, Endereço, Telefone e E-mail são obrigatórios.")
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