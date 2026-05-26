import customtkinter as ctk
from tkinter import messagebox
from database import (
    obter_todos_usuarios_db,
    atualizar_credenciais_usuario_db,
    obter_tabela_fretes_db,
    salvar_configuracao_frete_db
)

class JanelaConfiguracoes(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("Configurações do Sistema - Xô Sujeira")
        self.geometry("800x700")
        self.resizable(False, False)
        self.grab_set()
        self.focus()

        self.entradas_frete = {}
        self.entradas_usuario = {}

        ctk.CTkLabel(self, text="⚙️ Configurações e Regras de Negócio", font=("Roboto", 24, "bold")).pack(pady=20)

        self.tabview = ctk.CTkTabview(self, width=750, height=550)
        self.tabview.pack(padx=20, pady=10, fill="both", expand=True)

        self.tab_usuarios = self.tabview.add("Gestão de Acessos")
        self.tab_fretes = self.tabview.add("Preços Base de Frete")

        self._setup_ui_usuarios()
        self._setup_ui_fretes()
        
        self.carregar_dados()

    def _setup_ui_usuarios(self):
        header = ctk.CTkFrame(self.tab_usuarios, fg_color="gray30")
        header.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(header, text="Tipo", width=120, font=("", 11, "bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Nome de Usuário", width=200, font=("", 11, "bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Nova Senha", width=200, font=("", 11, "bold")).pack(side="left", padx=5)
        
        self.scroll_users = ctk.CTkScrollableFrame(self.tab_usuarios, width=700, height=400)
        self.scroll_users.pack(fill="both", expand=True, padx=10, pady=5)

    def _setup_ui_fretes(self):
        header = ctk.CTkFrame(self.tab_fretes, fg_color="gray30")
        header.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(header, text="Urgência", width=180, font=("", 12, "bold")).pack(side="left", padx=10)
        ctk.CTkLabel(header, text="Distância", width=180, font=("", 12, "bold")).pack(side="left", padx=10)
        ctk.CTkLabel(header, text="Preço Unitário (R$)", width=180, font=("", 12, "bold")).pack(side="left", padx=10)

        self.scroll_fretes = ctk.CTkScrollableFrame(self.tab_fretes, width=700, height=380)
        self.scroll_fretes.pack(fill="both", expand=True, padx=10, pady=5)

        ctk.CTkButton(self.tab_fretes, text="💾 SALVAR TABELA DE FRETES", fg_color="green", command=self.salvar_fretes).pack(pady=10)

    def carregar_dados(self):
        # 1. Carregar Usuários
        for w in self.scroll_users.winfo_children(): w.destroy()
        self.entradas_usuario = {}
        
        for id_u, nome, senha, tipo in obter_todos_usuarios_db():
            f = ctk.CTkFrame(self.scroll_users)
            f.pack(fill="x", pady=2)
            
            ctk.CTkLabel(f, text=tipo, width=120, text_color="cyan").pack(side="left", padx=5)
            
            ent_nome = ctk.CTkEntry(f, width=200); ent_nome.insert(0, nome); ent_nome.pack(side="left", padx=5)
            ent_senha = ctk.CTkEntry(f, width=200, show="*"); ent_senha.insert(0, senha); ent_senha.pack(side="left", padx=5)
            
            btn_save = ctk.CTkButton(f, text="💾", width=40, command=lambda i=id_u, n=ent_nome, s=ent_senha: self.salvar_usuario(i, n, s))
            btn_save.pack(side="left", padx=5)

        # 2. Carregar Fretes
        for w in self.scroll_fretes.winfo_children(): w.destroy()
        self.entradas_frete = {}
        for urg, dist, valor in obter_tabela_fretes_db():
            f = ctk.CTkFrame(self.scroll_fretes)
            f.pack(fill="x", pady=2)
            ctk.CTkLabel(f, text=urg, width=180).pack(side="left", padx=10)
            ctk.CTkLabel(f, text=dist, width=180).pack(side="left", padx=10)
            e = ctk.CTkEntry(f, width=180)
            e.insert(0, f"{valor:.2f}")
            e.pack(side="left", padx=10)
            self.entradas_frete[(urg, dist)] = e

    def salvar_usuario(self, id_u, entry_nome, entry_senha):
        novo_n = entry_nome.get()
        nova_s = entry_senha.get()
        if not novo_n or not nova_s:
            messagebox.showwarning("Atenção", "Nome e senha não podem ser vazios.")
            return
            
        if atualizar_credenciais_usuario_db(id_u, novo_n, nova_s):
            messagebox.showinfo("Sucesso", "Usuário atualizado com sucesso!")
            self.carregar_dados()

    def salvar_fretes(self):
        try:
            for (urg, dist), widget in self.entradas_frete.items():
                valor = float(widget.get().replace(",", "."))
                salvar_configuracao_frete_db(urg, dist, valor)
            messagebox.showinfo("Sucesso", "Tabela de fretes atualizada!")
        except ValueError:
            messagebox.showerror("Erro", "Insira valores numéricos válidos.")