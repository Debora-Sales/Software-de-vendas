import customtkinter as ctk
from tkinter import messagebox
from database import salvar_cliente


class JanelaClientes(ctk.CTkToplevel):

    def __init__(self, parent):
        super().__init__(parent)

        self.title("Cadastro de Clientes - Xô Sujeira")
        self.geometry("700x700")
        self.resizable(False, False)

        self.grab_set()
        self.focus()

        self.label_titulo = ctk.CTkLabel(
            self,
            text="Novo Cadastro de Cliente",
            font=("Roboto", 28, "bold")
        )
        self.label_titulo.pack(pady=20)

        self.frame_campos = ctk.CTkFrame(self)
        self.frame_campos.pack(padx=30, pady=20, fill="both", expand=True)

        self.seg_tipo = ctk.CTkSegmentedButton(
            self.frame_campos,
            values=["Pessoa Física", "Pessoa Jurídica"],
            command=self.configurar_tipo_pessoa
        )

        self.seg_tipo.pack(pady=20)
        self.seg_tipo.set("Pessoa Física")

        self.ent_nome = self.criar_entry("Nome / Nome Fantasia")
        self.ent_razao = self.criar_entry("Razão Social")
        self.ent_cpf = self.criar_entry("CPF")
        self.ent_cnpj = self.criar_entry("CNPJ")
        self.ent_endereco = self.criar_entry("Endereço")
        self.ent_telefone = self.criar_entry("Telefone")
        self.ent_email = self.criar_entry("E-mail")

        self.ent_nome.pack(pady=10)

        self.configurar_tipo_pessoa("Pessoa Física")

        self.btn_salvar = ctk.CTkButton(
            self,
            text="Salvar Cliente",
            height=45,
            font=("Roboto", 16, "bold"),
            fg_color="green",
            hover_color="darkgreen",
            command=self.validar_e_salvar
        )

        self.btn_salvar.pack(pady=25)

    def criar_entry(self, texto):
        return ctk.CTkEntry(
            self.frame_campos,
            placeholder_text=texto,
            width=450,
            height=40,
            corner_radius=10
        )

    def configurar_tipo_pessoa(self, tipo):

        self.ent_razao.pack_forget()
        self.ent_cpf.pack_forget()
        self.ent_cnpj.pack_forget()
        self.ent_endereco.pack_forget()
        self.ent_telefone.pack_forget()
        self.ent_email.pack_forget()

        if tipo == "Pessoa Física":
            self.ent_cpf.pack(pady=10)
        else:
            self.ent_razao.pack(pady=10)
            self.ent_cnpj.pack(pady=10)

        self.ent_endereco.pack(pady=10)
        self.ent_telefone.pack(pady=10)
        self.ent_email.pack(pady=10)

    def validar_e_salvar(self):

        dados = {
            "nome": self.ent_nome.get(),
            "endereco": self.ent_endereco.get(),
            "telefone": self.ent_telefone.get(),
            "cpf": self.ent_cpf.get(),
            "cnpj": self.ent_cnpj.get(),
            "razao_social": self.ent_razao.get(),
            "email": self.ent_email.get()
        }

        if not dados["nome"] or not dados["endereco"] or not dados["telefone"]:
            messagebox.showwarning(
                "Campos obrigatórios",
                "Preencha nome, endereço e telefone."
            )
            return

        tipo = self.seg_tipo.get()

        if tipo == "Pessoa Física" and not dados["cpf"]:
            messagebox.showwarning("CPF obrigatório", "Informe o CPF.")
            return

        if tipo == "Pessoa Jurídica" and not dados["cnpj"]:
            messagebox.showwarning("CNPJ obrigatório", "Informe o CNPJ.")
            return

        id_cliente = salvar_cliente(**dados)

        if id_cliente:
            messagebox.showinfo(
                "Sucesso",
                f"Cliente cadastrado com sucesso!\nID Gerado: {id_cliente}"
            )

            self.destroy()
