import customtkinter as ctk 
from database import realizar_login  
from tkinter import messagebox 

# 1. Configuração da Janela 

def acao_login(): 
    # 1. Pega o que o usuário digitou 
    usuario = ent_usuario.get() 
    senha = ent_senha.get()

    # 2. Chama a função do arquivo database.py 
    perfil = realizar_login(usuario, senha)

    # 3. O Desfecho 
    if perfil: 
        messagebox.showinfo("Sucesso", f"Bem-vindo! Perfil: {perfil}") 
        # Aqui a janela de login fecha e o seu menu principal abre! 
        janela.destroy()  
    else: 
        messagebox.showerror("Erro", "Usuário ou senha inválidos.")


janela = ctk.CTk() 
janela.title("Meu Projeto - Login") 
janela.geometry("400x500") 

# 2. O Container Central (Frame) 
frame = ctk.CTkFrame(janela, corner_radius=15) 
frame.pack(pady=40, padx=40, fill="both", expand=True) 


# 3. Os Widgets 
ctk.CTkLabel(frame, text="Login", font=("Roboto", 24, "bold")).pack(pady=20) 

ent_usuario = ctk.CTkEntry(frame, placeholder_text="Nome de Usuário") 
ent_usuario.pack(pady=12, padx=30, fill="x") 

ent_senha = ctk.CTkEntry(frame, placeholder_text="Senha", show="*") 
ent_senha.pack(pady=12, padx=30, fill="x") 

btn_entrar = ctk.CTkButton(frame, text="Entrar", command=acao_login) 
btn_entrar.pack(pady=25, padx=30, fill="x") 


janela.mainloop() 