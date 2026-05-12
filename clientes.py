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
        
        self.tab_cadastro = self.tabview.add("Cadastrar Cliente")
        self.tab_busca = self.tabview.add("Buscar Cliente")

        # --- UI DA ABA CADASTRO ---
        
        self.ent_nome = self.criar_entry(self.tab_cadastro, "Nome / Razão Social")
        self.ent_endereco = self.criar_entry(self.tab_cadastro, "Endereço Completo")
        self.ent_telefone = self.criar_entry(self.tab_cadastro, "Telefone de Contato")
        self.ent_cpf = self.criar_entry(self.tab_cadastro, "CPF")
        self.ent_cnpj = self.criar_entry(self.tab_cadastro, "CNPJ")
        self.ent_razao_social = self.criar_entry(self.tab_cadastro, "Razão Social (opcional)")
        self.ent_email = self.criar_entry(self.tab_cadastro, "E-mail")

        # Posicionamento
        for entry in [self.ent_nome, self.ent_endereco, self.ent_telefone, self.ent_cpf, self.ent_cnpj, self.ent_razao_social, self.ent_email]:
            entry.pack(pady=8)

        self.frame_botoes_cadastro = ctk.CTkFrame(self.tab_cadastro, fg_color="transparent")
        self.frame_botoes_cadastro.pack(pady=15)

        self.btn_salvar = ctk.CTkButton(
            self.frame_botoes_cadastro,
            text="Salvar Cliente",
            height=45,
            font=("Roboto", 16, "bold"),
            fg_color="green",
            hover_color="darkgreen",
            command=self.validar_e_salvar
        )
        self.btn_salvar.pack(side="left", padx=10)

        # Sprint 13: Botão Limpar Campos
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
        self.ent_nome.delete(0, "end")
        self.ent_endereco.delete(0, "end")
        self.ent_telefone.delete(0, "end")
        self.ent_cpf.delete(0, "end")
        self.ent_cnpj.delete(0, "end")
        self.ent_razao_social.delete(0, "end")
        self.ent_email.delete(0, "end")
        self.id_cliente_editando = None
        self.btn_salvar.configure(text="Salvar Cliente", fg_color="green")

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
            self.ent_nome.insert(0, self.cliente_atual['nome'])
            self.ent_endereco.insert(0, self.cliente_atual['endereco'])
            self.ent_telefone.insert(0, self.cliente_atual['telefone'])
            self.ent_cpf.insert(0, self.cliente_atual['cpf'] or "")
            self.ent_cnpj.insert(0, self.cliente_atual['cnpj'] or "")
            self.ent_razao_social.insert(0, self.cliente_atual['razao_social'] or "")
            self.ent_email.insert(0, self.cliente_atual['email'])
            self.btn_salvar.configure(text="Atualizar Cliente", fg_color="blue")
            self.tabview.set("Cadastrar Cliente")

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

    def validar_e_salvar(self):
        nome = self.ent_nome.get()
        endereco = self.ent_endereco.get()
        telefone = self.ent_telefone.get()
        email = self.ent_email.get()
        
        if not all([nome, endereco, telefone, email]):
            messagebox.showwarning("Campos Obrigatórios", "Nome, Endereço, Telefone e E-mail são obrigatórios (RN02).")
            return
            
        if self.id_cliente_editando:
            sucesso = atualizar_cliente_db(self.id_cliente_editando, nome, endereco, telefone, self.ent_cpf.get(), self.ent_cnpj.get(), self.ent_razao_social.get(), email)
            if sucesso:
                messagebox.showinfo("Sucesso", "Dados do cliente atualizados!")
                self.limpar_campos()
                self.tabview.set("Buscar Cliente")
        else:
            id_gerado = salvar_cliente(nome, endereco, telefone, self.ent_cpf.get(), self.ent_cnpj.get(), self.ent_razao_social.get(), email)
            if id_gerado:
                messagebox.showinfo("Sucesso", f"Cliente cadastrado com ID {id_gerado}.")
                self.limpar_campos()