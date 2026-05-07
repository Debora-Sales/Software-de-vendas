import customtkinter as ctk
from tkinter import messagebox
from database import salvar_cliente

class JanelaClientes(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Cadastro de Clientes - Xô Sujeira")
        self.geometry("500x650")
        self.resizable(False, False)

        # Faz com que a janela apareça na frente das outras
        self.grab_set()
        self.focus()

        self.label_titulo = ctk.CTkLabel(self, text="Novo Cadastro de Cliente", font=("Roboto", 24, "bold"))
        self.label_titulo.pack(pady=20)

        # Container para os campos de entrada (RN02: Dados Obrigatórios)
        self.frame_campos = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_campos.pack(pady=10, padx=40, fill="both", expand=True)

        # Seletor de Tipo de Pessoa (PF ou PJ) para evitar conflitos de dados (RN)
        self.seg_tipo = ctk.CTkSegmentedButton(self.frame_campos, values=["Pessoa Física", "Pessoa Jurídica"], command=self.configurar_tipo_pessoa)
        self.seg_tipo.set("Pessoa Física")
        self.seg_tipo.pack(pady=10)

        self.ent_nome = ctk.CTkEntry(self.frame_campos, placeholder_text="Nome / Nome Fantasia", width=350)
        self.ent_nome.pack(pady=10)

        self.ent_razao = ctk.CTkEntry(self.frame_campos, placeholder_text="Razão Social", width=350)
        self.ent_cpf = ctk.CTkEntry(self.frame_campos, placeholder_text="CPF", width=350)
        self.ent_cnpj = ctk.CTkEntry(self.frame_campos, placeholder_text="CNPJ", width=350)
        self.ent_endereco = ctk.CTkEntry(self.frame_campos, placeholder_text="Endereço de Entrega", width=350)
        self.ent_telefone = ctk.CTkEntry(self.frame_campos, placeholder_text="Telefone de Contato", width=350)
        self.ent_email = ctk.CTkEntry(self.frame_campos, placeholder_text="E-mail", width=350)

        # Chamamos a configuração inicial apenas após todos os objetos existirem
        # Isso evita o erro de 'AttributeError' e garante que a tela monte corretamente
        self.configurar_tipo_pessoa("Pessoa Física")

        self.btn_salvar = ctk.CTkButton(self, text="Salvar Cliente", command=self.validar_e_salvar, fg_color="green", hover_color="darkgreen")
        self.btn_salvar.pack(pady=20)

    def configurar_tipo_pessoa(self, tipo):
        """Oculta ou exibe campos conforme a escolha para evitar conflito de dados (PF/PJ)."""
        # Limpamos os dados para não enviar informações residuais ao banco
        self.ent_razao.delete(0, 'end')
        self.ent_cpf.delete(0, 'end')
        self.ent_cnpj.delete(0, 'end')

        # Removemos todos os campos dinâmicos e os que vêm depois deles para reorganizar a ordem
        self.ent_razao.pack_forget()
        self.ent_cpf.pack_forget()
        self.ent_cnpj.pack_forget()
        self.ent_endereco.pack_forget()
        self.ent_telefone.pack_forget()
        self.ent_email.pack_forget()

        if tipo == "Pessoa Física":
            # Exibe apenas CPF
            self.ent_cpf.pack(pady=10)
        else:
            # Exibe Razão Social e CNPJ
            self.ent_razao.pack(pady=10)
            self.ent_cnpj.pack(pady=10)

        # Repacotamos os campos fixos que ficam na parte de baixo, garantindo a ordem
        self.ent_endereco.pack(pady=10)
        self.ent_telefone.pack(pady=10)
        self.ent_email.pack(pady=10)

    def validar_e_salvar(self):
        # Coleta os dados dos campos
        dados = {
            "nome": self.ent_nome.get(),
            "endereco": self.ent_endereco.get(),
            "telefone": self.ent_telefone.get(),
            "cpf": self.ent_cpf.get(),
            "cnpj": self.ent_cnpj.get(),
            "razao_social": self.ent_razao.get(),
            "email": self.ent_email.get()
        }

        # Validação dinâmica para garantir que apenas o documento correto foi preenchido
        tipo = self.seg_tipo.get()
        documento_valido = False
        
        if tipo == "Pessoa Física" and dados["cpf"]:
            documento_valido = True
        elif tipo == "Pessoa Jurídica" and (dados["cnpj"] and dados["razao_social"]):
            documento_valido = True

        if not dados["nome"] or not dados["telefone"] or not dados["endereco"] or not documento_valido:
            messagebox.showwarning("Atenção", "Preencha Nome, Telefone, Endereço e os dados obrigatórios do tipo selecionado.")
            return

        # Chama a função do banco de dados
        if salvar_cliente(**dados):
            messagebox.showinfo("Sucesso", "Cliente cadastrado com sucesso!")
            self.destroy()