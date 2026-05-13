import customtkinter as ctk
from tkinter import messagebox
from database import salvar_cliente

class JanelaClientesPF(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("Cadastro de Cliente Pessoa Física - Xô Sujeira")
        self.geometry("550x600")
        self.resizable(False, False)

        # Faz a janela ser modal (foca apenas nela até ser fechada)
        self.grab_set()
        self.focus()

        self.label_titulo = ctk.CTkLabel(
            self, 
            text="Cadastro Simplificado (PF)", 
            font=("Roboto", 24, "bold")
        )
        self.label_titulo.pack(pady=20)

        # Campos específicos para Pessoa Física
        self.ent_nome = self.criar_entry("Nome Completo")
        self.ent_cpf = self.criar_entry("CPF")
        self.ent_telefone = self.criar_entry("Telefone de Contato")
        self.ent_email = self.criar_entry("E-mail")
        self.ent_endereco = self.criar_entry("Endereço de Entrega")

        for entry in [self.ent_nome, self.ent_cpf, self.ent_telefone, self.ent_email, self.ent_endereco]:
            entry.pack(pady=10)

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

    def validar_e_salvar(self):
        nome = self.ent_nome.get()
        cpf = self.ent_cpf.get()
        tel = self.ent_telefone.get()
        email = self.ent_email.get()
        end = self.ent_endereco.get()

        # Validação básica de campos obrigatórios
        if not all([nome, cpf, tel, email, end]):
            messagebox.showwarning("Atenção", "Todos os campos são obrigatórios para o cadastro PF.")
            return

        # Salva no banco de dados
        # Passamos strings vazias para CNPJ e Razão Social, pois é um cadastro PF
        id_gerado = salvar_cliente(nome, end, tel, cpf, "", "", email)
        
        if id_gerado:
            messagebox.showinfo(
                "Sucesso", 
                f"Cliente Pessoa Física cadastrado com sucesso!\nID Gerado: {id_gerado}"
            )
            self.destroy() # Fecha a janela após o sucesso