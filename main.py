import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os

from database import realizar_login, criar_tabelas
from menu import abrir_menu


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

criar_tabelas()

caminho_logo = os.path.join(os.path.dirname(__file__), "logo.png")

imagem_logo = ctk.CTkImage(
    light_image=Image.open(caminho_logo),
    dark_image=Image.open(caminho_logo),
    size=(120, 120)
)


def acao_login(event=None):

    usuario = ent_usuario.get()
    senha = ent_senha.get()

    if not usuario or not senha:
        messagebox.showwarning(
            "Campos obrigatórios",
            "Informe usuário e senha."
        )
        return

    perfil = realizar_login(usuario, senha)

    if perfil:

        messagebox.showinfo(
            "Sucesso",
            f"Bem-vindo! Perfil: {perfil[0]}"
        )

        janela.destroy()

        app_menu = abrir_menu(perfil[0])
        app_menu.mainloop()

    else:
        messagebox.showerror(
            "Erro",
            "Usuário ou senha inválidos."
        )


janela = ctk.CTk()

janela.title("Xô Sujeira - Login")
janela.geometry("420x520")
janela.resizable(False, False)

janela.bind("<Return>", acao_login)

frame = ctk.CTkFrame(
    master=janela,
    corner_radius=20
)

frame.pack(
    pady=40,
    padx=40,
    fill="both",
    expand=True
)

label_imagem = ctk.CTkLabel(
    master=frame,
    image=imagem_logo,
    text=""
)

label_imagem.pack(pady=(20, 10))

titulo = ctk.CTkLabel(
    frame,
    text="Sistema Comercial",
    font=("Roboto", 24, "bold")
)

titulo.pack(pady=10)

ent_usuario = ctk.CTkEntry(
    frame,
    placeholder_text="Usuário",
    height=40
)

ent_usuario.pack(
    pady=12,
    padx=30,
    fill="x"
)

ent_senha = ctk.CTkEntry(
    frame,
    placeholder_text="Senha",
    show="*",
    height=40
)

ent_senha.pack(
    pady=12,
    padx=30,
    fill="x"
)

btn_entrar = ctk.CTkButton(
    frame,
    text="Entrar",
    height=45,
    font=("Roboto", 15, "bold"),
    command=acao_login
)

btn_entrar.pack(
    pady=25,
    padx=30,
    fill="x"
)

info_login = ctk.CTkLabel(
    frame,
    text="Login padrão: admin | Senha: admin123",
    font=("Roboto", 12)
)

info_login.pack(pady=10)

janela.mainloop()
