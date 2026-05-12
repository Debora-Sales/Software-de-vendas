import customtkinter as ctk
import os
from tkinter import messagebox
from PIL import Image
from clientes import JanelaClientes
from produtos_ui import JanelaProdutos


class abrir_menu(ctk.CTkToplevel):

    def __init__(self, parent, perfil_usuario):
        super().__init__(parent)

        self.title("Xô Sujeira - Menu Principal")
        self.geometry("900x600")

        self.perfil = perfil_usuario

        self.frame_menu = ctk.CTkFrame(
            self,
            width=200,
            corner_radius=20
        )

        self.frame_menu.pack(side="left", padx=20, pady=20, fill="y")

        caminho_logo = os.path.join(os.path.dirname(__file__), "logo.png")

        self.img_logo = ctk.CTkImage(
            Image.open(caminho_logo),
            size=(100, 100)
        )

        self.lbl_logo_menu = ctk.CTkLabel(
            self.frame_menu,
            image=self.img_logo,
            text=""
        )

        self.lbl_logo_menu.pack(pady=(20, 10))

        self.label_titulo = ctk.CTkLabel(
            self.frame_menu,
            text="Menu Principal",
            font=("Roboto", 24, "bold")
        )

        self.label_titulo.pack(pady=20, padx=20)

        self.criar_botao("Produtos", self.abrir_produtos)
        self.criar_botao("Clientes", self.abrir_clientes)
        self.criar_botao("Vendas", self.abrir_vendas)
        self.criar_botao("Funcionários", self.abrir_funcionarios)

        if self.perfil == "Administrador":
            self.criar_botao(
                "Relatórios Financeiros",
                self.abrir_relatorios
            )

        self.frame_conteudo = ctk.CTkFrame(
            self,
            corner_radius=20
        )

        self.frame_conteudo.pack(
            side="right",
            padx=10,
            pady=20,
            fill="both",
            expand=True
        )

        self.label_welcome = ctk.CTkLabel(
            self.frame_conteudo,
            text="Sistema Comercial Xô Sujeira",
            font=("Roboto", 30, "bold")
        )

        self.label_welcome.pack(pady=40)

        self.label_info = ctk.CTkLabel(
            self.frame_conteudo,
            text=f"Usuário logado: {self.perfil}",
            font=("Roboto", 18)
        )

        self.label_info.pack()

    def criar_botao(self, texto, comando):

        btn = ctk.CTkButton(
            self.frame_menu,
            text=texto,
            command=comando,
            width=200,
            height=45,
            font=("Roboto", 15, "bold")
        )

        btn.pack(pady=10)

    def abrir_produtos(self):
        JanelaProdutos(self)
    
    def abrir_clientes(self):
        JanelaClientes(self)

    def abrir_vendas(self):
        messagebox.showinfo(
            "Vendas",
            "Módulo de vendas em desenvolvimento."
        )

    def abrir_funcionarios(self):
        messagebox.showinfo(
            "Funcionários",
            "Módulo de funcionários em desenvolvimento."
        )

    def abrir_relatorios(self):
        messagebox.showinfo(
            "Relatórios",
            "Módulo financeiro em desenvolvimento."
        )
