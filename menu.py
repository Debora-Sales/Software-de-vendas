import customtkinter as ctk
import os
from PIL import Image






class abrir_menu(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Mantendo as configurações de janela que você já usa
        self.title("Xô Sujeira- Menu Principal")
        self.geometry("900x600")

       

    
        # Estrutura de Menu Lateral (Front-end)
        self.frame_menu = ctk.CTkFrame(self, width=200, corner_radius=15)
        self.frame_menu.pack(side="left", padx=20, pady=20, fill="y")

        
        caminho_logo = os.path.join(os.path.dirname(__file__), "logo.png")
        img_logo = ctk.CTkImage(Image.open(caminho_logo), size=(100, 100))

        self.lbl_logo_menu = ctk.CTkLabel(self.frame_menu, image=img_logo, text="")
        self.lbl_logo_menu.pack(pady=(20, 10))

        

   

        self.label_titulo = ctk.CTkLabel(self.frame_menu, text="Menu", font=("Roboto", 24, "bold"))
        self.label_titulo.pack(pady=20, padx=10)

      
        # Botões do Menu (Conforme os arquivos que você citou)
        self.btn_produtos = ctk.CTkButton(self.frame_menu, text="Produtos", command=self.abrir_produtos)
        self.btn_produtos.pack(pady=10, padx=20)

        self.btn_clientes = ctk.CTkButton(self.frame_menu, text="Clientes", command=self.abrir_clientes)
        self.btn_clientes.pack(pady=10, padx=20)

        self.btn_vendas = ctk.CTkButton(self.frame_menu, text="Vendas", command=self.abrir_vendas)
        self.btn_vendas.pack(pady=10, padx=20)

        self.btn_func = ctk.CTkButton(self.frame_menu, text="Funcionários", command=self.abrir_funcionarios)
        self.btn_func.pack(pady=10, padx=20)

        # Área de Conteúdo (Direita)
        self.frame_conteudo = ctk.CTkFrame(self, corner_radius=15)
        self.frame_conteudo.pack(side="right", padx=20, pady=20, fill="both", expand=True)
        
        self.label_welcome = ctk.CTkLabel(self.frame_conteudo, text="Selecione uma opção no menu", font=("Roboto", 16))
        self.label_welcome.pack(pady=50)

    # Funções de navegação
    def abrir_produtos(self):
        print("Abrindo produtos.py...")

    def abrir_clientes(self):
        print("Abrindo cadastro.py...")

    def abrir_vendas(self):
        print("Abrindo venda.py...")

    def abrir_funcionarios(self):
        print("Abrindo funcionários.py...")