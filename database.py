import sqlite3  

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