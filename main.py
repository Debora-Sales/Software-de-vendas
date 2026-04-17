import customtkinter as ctk 
from database import realizar_login  
from tkinter import messagebox 
import os 
from PIL import Image 
from menu import abrir_menu # Importando o novo arquivo

caminho_logo = os.path.join(os.path.dirname(__file__), "logo.png")

imagem_logo = ctk.CTkImage(
        light_image=Image.open(caminho_logo),
        dark_image=Image.open(caminho_logo),
        size=(120, 120) 
    )

def acao_login(event=None): 
    usuario = ent_usuario.get() 
    senha = ent_senha.get()
    
    perfil = realizar_login(usuario, senha)

    if perfil: 
        messagebox.showinfo("Sucesso", f"Bem-vindo! Perfil: {perfil}") 
        janela.destroy() # Fecha a janela de login
        
        # Inicia o menu que está no outro arquivo
        app_menu = abrir_menu()
        app_menu.mainloop()
    else: 
        messagebox.showerror("Erro", "Usuário ou senha inválidos.")

ctk.set_appearance_mode("dark") 
ctk.set_default_color_theme("blue") 


    # --- area da logo ---



# --- O RESTANTE DO SEU CÓDIGO DO MAIN.PY CONTINUA IGUAL ---
janela = ctk.CTk() 
janela.title("Xô Sujeira - Login") 
janela.geometry("400x500") 
janela.resizable(False, False) 

janela.bind('<Return>', lambda event: acao_login())

janela.resizable(False, False) 




frame = ctk.CTkFrame(master=janela, corner_radius=15) 
frame.pack(pady=40, padx=40, fill="both", expand=True)

label_imagem = ctk.CTkLabel(master=frame, image=imagem_logo, text="" ) 
label_imagem.pack(pady=(20, 10))

ent_usuario = ctk.CTkEntry(frame, placeholder_text="Nome de Usuário") 
ent_usuario.pack(pady=12, padx=30, fill="x") 

ent_senha = ctk.CTkEntry(frame, placeholder_text="Senha", show="*") 
ent_senha.pack(pady=12, padx=30, fill="x") 

btn_entrar = ctk.CTkButton(frame, text="Entrar", command=acao_login) 
btn_entrar.pack(pady=25, padx=30, fill="x") 


janela.mainloop()