import customtkinter as ctk
import os
from tkinter import messagebox
from PIL import Image
from clientes import JanelaClientes


class abrir_menu(ctk.CTk):

    def __init__(self, perfil_usuario):
        super().__init__()

        self.title("Xô Sujeira - Menu Principal")
        self.geometry("1100x700")

        self.perfil = perfil_usuario

        self.frame_menu = ctk.CTkFrame(
            self,
            width=250,
            corner_radius=20
        )

        self.frame_menu.pack(side="left", padx=20, pady=20, fill="y")

        caminho_logo = os.path.join(os.path.dirname(__file__), "logo.png")

        img_logo = ctk.CTkImage(
            Image.open(caminho_logo),
            size=(120, 120)
        )

        self.lbl_logo_menu = ctk.CTkLabel(
            self.frame_menu,
            image=img_logo,
            text=""
        )

        self.lbl_logo_menu.pack(pady=(20, 10))

        self.label_titulo = ctk.CTkLabel(
            self.frame_menu,
            text="Menu Principal",
            font=("Roboto", 26, "bold")
        )

        self.label_titulo.pack(pady=20)

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
            padx=20,
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
        messagebox.showinfo(
            "Produtos",
            "Módulo de produtos em desenvolvimento."
        )

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
