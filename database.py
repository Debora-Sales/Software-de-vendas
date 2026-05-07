import sqlite3  
from tkinter import messagebox

def conectar(): 
#Cria a ponte com o arquivo local do banco de dados
    try: 
        # Conecta (ou cria) o arquivo do banco do seu projeto 
        return sqlite3.connect('xo_sujeira.db')  
    except Exception as e: 
        print(f"Erro de conexão: {e}") 
        return None 

def realizar_login(login_digitado, senha_digitada): 
    #Vai até o banco e checa se o usuário existe""" 
    conn = conectar() 
    if conn: 
        cursor = conn.cursor() 
        # O SQL usa os pontos de interrogação (?) para evitar invasões (SQL Injection) 
        comando = "SELECT tipo FROM usuarios WHERE nome = ? AND senha = ?" 
        cursor.execute(comando, (login_digitado, senha_digitada)) 

        resultado = cursor.fetchone() # Pega a resposta do banco 
        conn.close() 

        if resultado: 
            return resultado # Retorna o perfil (ex: 'Admin' ou 'Usuário') 
    return None # Retorna vazio se a senha estiver errada

#funções da janela clientes

def salvar_cliente(nome, endereco, telefone, cpf, cnpj, razao_social, email):
    """Insere um novo cliente no banco de dados."""
    conn = conectar()
    if conn:
        try:
            cursor = conn.cursor()
            comando = """
                INSERT INTO Clientes (nome, endereco, telefone, cpf, cnpj, razao_social, email)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(comando, (nome, endereco, telefone, cpf, cnpj, razao_social, email))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            messagebox.showerror("Erro SQL", f"Erro ao salvar: {e}")
            return False
    return False

def buscar_cliente_por_id(id_cliente):
    """Procura um cliente no Azure pelo ID e retorna os seus dados."""
    conn = conectar()
    if conn:
        try:
            cursor = conn.cursor()
            # Comando SQL para selecionar todos os dados obrigatórios do cliente (RN02)
            comando = "SELECT nome, endereco, telefone, cpf, cnpj, razao_social, email FROM Clientes WHERE id = ?"
            cursor.execute(comando, (id_cliente,))
           
            resultado = cursor.fetchone()
            conn.close()
           
            if resultado:
                # Retornamos os dados organizados
                return {
                    "nome": resultado[0], "endereco": resultado[1], "telefone": resultado[2],
                    "cpf": resultado[3], "cnpj": resultado[4], "razao_social": resultado[5],
                    "email": resultado[6]
                }
            else:
                return None
        except Exception as e:
            messagebox.showerror("Erro SQL", f"Erro ao salvar: {e}")
            return None
    return None