import customtkinter as ctk
import os
from tkinter import messagebox
from PIL import Image
from clientes import JanelaClientes
from produtos import JanelaProdutos
from funcionarios import JanelaFuncionarios
from vendas import JanelaVendas
from relatorios import JanelaRelatorios
from configuracoes import JanelaConfiguracoes
from estoque import JanelaEstoque
from database import (
    obter_ranking_produtos_db,
    obter_estoque_baixo_db,
    obter_ranking_vendedores_db
)


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

        if self.perfil in ["Administrador", "Estoquista"]:
            self.criar_botao("Produtos", self.abrir_produtos)

        if self.perfil in ["Administrador", "Vendedor"]:
            self.criar_botao("Clientes", self.abrir_clientes)
            self.criar_botao("Vendas", self.abrir_vendas)

        if self.perfil in ["Administrador", "Vendedor", "Estoquista"]:
            self.criar_botao("Controle de Estoque", self.abrir_estoque)

        if self.perfil == "Administrador":
            self.criar_botao("Funcionários", self.abrir_funcionarios)
            self.criar_botao(
                "Relatórios Financeiros",
                self.abrir_relatorios
            )
            self.criar_botao(
                "Configurações",
                self.abrir_configuracoes
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

        # Script 37: Lobby do Administrador
        if self.perfil == "Administrador":
            self.label_welcome.configure(text="Painel de Controle Administrativo", font=("Roboto", 24, "bold"))
            self._setup_dashboard_adm()

    def _setup_dashboard_adm(self):
        """Constrói a interface de rankings e alertas para o Administrador."""
        self.frame_dash = ctk.CTkFrame(self.frame_conteudo, fg_color="transparent")
        self.frame_dash.pack(fill="both", expand=True, padx=20, pady=20)

        # Configuração de Colunas
        self.frame_dash.grid_columnconfigure((0, 1, 2), weight=1, pad=10)

        # 1. Ranking de Produtos
        col_prod = ctk.CTkFrame(self.frame_dash, fg_color="gray20", corner_radius=10)
        col_prod.grid(row=0, column=0, sticky="nsew", padx=5)
        ctk.CTkLabel(col_prod, text="🏆 Mais Vendidos", font=("", 14, "bold"), text_color="orange").pack(pady=10)
        
        for i, (nome, qtd) in enumerate(obter_ranking_produtos_db(), 1):
            txt = f"{i}º {nome[:15]}... ({qtd} un)"
            ctk.CTkLabel(col_prod, text=txt, font=("", 11), anchor="w").pack(fill="x", padx=10, pady=2)

        # 2. Estoque Baixo
        col_est = ctk.CTkFrame(self.frame_dash, fg_color="gray20", corner_radius=10)
        col_est.grid(row=0, column=1, sticky="nsew", padx=5)
        ctk.CTkLabel(col_est, text="📉 Estoque Crítico", font=("", 14, "bold"), text_color="red").pack(pady=10)
        
        for nome, qtd, mini in obter_estoque_baixo_db():
            cor = "red" if qtd <= mini else "white"
            txt = f"• {nome[:15]}... [{qtd}/{mini}]"
            ctk.CTkLabel(col_est, text=txt, font=("", 11), text_color=cor, anchor="w").pack(fill="x", padx=10, pady=2)

        # 3. Ranking Vendedores (Mês)
        col_vend = ctk.CTkFrame(self.frame_dash, fg_color="gray20", corner_radius=10)
        col_vend.grid(row=0, column=2, sticky="nsew", padx=5)
        ctk.CTkLabel(col_vend, text="💰 Top Vendedores (Mês)", font=("", 14, "bold"), text_color="cyan").pack(pady=10)
        
        for i, (nome, total) in enumerate(obter_ranking_vendedores_db(), 1):
            txt = f"{i}º {nome[:12]} - R$ {total:,.0f}"
            ctk.CTkLabel(col_vend, text=txt, font=("", 11), anchor="w").pack(fill="x", padx=10, pady=2)

        # Botão de Atualização Manual do Dashboard
        ctk.CTkButton(
            self.frame_conteudo, 
            text="🔄 Atualizar Indicadores", 
            width=200, 
            height=32, 
            fg_color="#333333",
            command=self._refresh_dash
        ).pack(pady=10)

    def _refresh_dash(self):
        """Recarrega os widgets do dashboard."""
        for widget in self.frame_dash.winfo_children():
            widget.destroy()
        self.frame_dash.destroy()
        
        # Verifica se o botão de refresh antigo ainda existe para não duplicar
        for widget in self.frame_conteudo.winfo_children():
            if isinstance(widget, ctk.CTkButton) and widget.cget("text") == "🔄 Atualizar Indicadores":
                widget.destroy()
        
        self._setup_dashboard_adm()

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
        JanelaClientes(self, self.perfil)

    def abrir_vendas(self):
        JanelaVendas(self)

    def abrir_funcionarios(self):
        JanelaFuncionarios(self)

    def abrir_relatorios(self):
        JanelaRelatorios(self)

    def abrir_configuracoes(self):
        JanelaConfiguracoes(self)

    def abrir_estoque(self):
        JanelaEstoque(self, self.perfil)
