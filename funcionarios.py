import customtkinter as ctk
import re
from tkinter import messagebox
from database import (
    salvar_funcionario,
    buscar_funcionario_por_id_func,
    atualizar_funcionario_db,
    deletar_funcionario_db
)

class JanelaFuncionarios(ctk.CTkToplevel): 
    def __init__(self, parent):
        super().__init__(parent)

        self.title("Cadastro de Funcionários - Xô Sujeira")
        self.geometry("750x850")
        self.resizable(False, False)
        self.grab_set()
        self.focus()

        # Estado
        self.id_editando = None
        self.func_atual = None

        # Título principal
        ctk.CTkLabel(self, text="Gerenciamento de Funcionários", font=("Roboto", 28, "bold")).pack(pady=15)

        # Status/Feedback
        self.lbl_status = ctk.CTkLabel(self, text="", font=("Roboto", 14, "bold"))
        self.lbl_status.pack(pady=5)

        # --- FRAME DE BUSCA (TOPO) ---
        self.frame_busca = ctk.CTkFrame(self)
        self.frame_busca.pack(padx=20, pady=10, fill="x")
        
        ctk.CTkLabel(self.frame_busca, text="Localizar (Matrícula/ID):", font=("Roboto", 12, "bold")).pack(side="left", padx=10)
        
        self.ent_busca_id = ctk.CTkEntry(self.frame_busca, placeholder_text="ID...", width=150)
        self.ent_busca_id.pack(side="left", padx=5)
        self.ent_busca_id.bind("<KeyRelease>", lambda e: self.validar_apenas_numeros(self.ent_busca_id))

        self.btn_buscar = ctk.CTkButton(self.frame_busca, text="🔍 Buscar / Editar", width=140, command=self.buscar_funcionario)
        self.btn_buscar.pack(side="left", padx=10)

        self.btn_cancelar = ctk.CTkButton(self.frame_busca, text="❌ Cancelar", width=100, fg_color="#444444", hover_color="#333333", command=self.limpar)

        # --- FRAME DO FORMULÁRIO ---
        self.frame_form = ctk.CTkFrame(self)
        self.frame_form.pack(padx=20, pady=10, fill="both", expand=True)

        ctk.CTkLabel(self.frame_form, text="Nome Completo:", font=("Roboto", 12, "bold")).pack(anchor="w", padx=150)
        self.ent_nome = self.criar_entry(self.frame_form, "Nome")
        self.ent_nome.pack(pady=(0, 8))

        ctk.CTkLabel(self.frame_form, text="CPF:", font=("Roboto", 12, "bold")).pack(anchor="w", padx=150)
        self.ent_cpf = self.criar_entry(self.frame_form, "000.000.000-00")
        self.ent_cpf.pack(pady=(0, 8))

        ctk.CTkLabel(self.frame_form, text="Data de Nascimento:", font=("Roboto", 12, "bold")).pack(anchor="w", padx=150)
        self.ent_nasc = self.criar_entry(self.frame_form, "DD/MM/AAAA")
        self.ent_nasc.pack(pady=(0, 8))

        ctk.CTkLabel(self.frame_form, text="Estado Civil:", font=("Roboto", 12, "bold")).pack(anchor="w", padx=150)
        self.ent_civil = self.criar_entry(self.frame_form, "Ex: Solteiro(a)")
        self.ent_civil.pack(pady=(0, 8))

        ctk.CTkLabel(self.frame_form, text="Endereço:", font=("Roboto", 12, "bold")).pack(anchor="w", padx=150)
        self.ent_end = self.criar_entry(self.frame_form, "Rua, Bairro, Cidade")
        self.ent_end.pack(pady=(0, 8))

        ctk.CTkLabel(self.frame_form, text="Cargo:", font=("Roboto", 12, "bold")).pack(anchor="w", padx=150)
        self.ent_cargo = self.criar_entry(self.frame_form, "Ex: Vendedor")
        self.ent_cargo.pack(pady=(0, 8))

        ctk.CTkLabel(self.frame_form, text="E-mail Pessoal:", font=("Roboto", 12, "bold")).pack(anchor="w", padx=150)
        self.ent_email = self.criar_entry(self.frame_form, "exemplo@gmail.com")
        self.ent_email.pack(pady=(0, 8))

        ctk.CTkLabel(self.frame_form, text="Salário:", font=("Roboto", 12, "bold")).pack(anchor="w", padx=150)
        self.ent_salario = self.criar_entry(self.frame_form, "R$ 0,00")
        self.ent_salario.pack(pady=(0, 8))

        # Bindings para Máscaras e Validações
        self.ent_cpf.bind("<KeyRelease>", self.formatar_cpf)
        self.ent_nasc.bind("<KeyRelease>", self.formatar_data)
        self.ent_salario.bind("<FocusOut>", lambda e: self.formatar_moeda(self.ent_salario))

        # --- FRAME DE AÇÕES (BOTÕES) ---
        self.frame_acoes = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_acoes.pack(pady=15)

        self.btn_salvar = ctk.CTkButton(self.frame_acoes, text="💾 Salvar / Atualizar", height=45, font=("Roboto", 15, "bold"), fg_color="green", command=self.validar_e_salvar)
        self.btn_salvar.pack(side="left", padx=10)

        self.btn_limpar = ctk.CTkButton(self.frame_acoes, text="🧹 Limpar", height=45, font=("Roboto", 15, "bold"), fg_color="gray", command=self.limpar)
        self.btn_limpar.pack(side="left", padx=10)

        self.btn_exc = ctk.CTkButton(self.frame_acoes, text="🗑️ Excluir", height=45, font=("Roboto", 15, "bold"), fg_color="red", state="disabled", command=self.excluir)
        self.btn_exc.pack(side="left", padx=10)

        # Área de log/detalhes
        self.txt_resultado = ctk.CTkTextbox(self, width=650, height=100, font=("Roboto", 12))
        self.txt_resultado.pack(pady=10, padx=20)
        self.txt_resultado.insert("0.0", "Detalhes do contrato do funcionário aparecerão aqui...")
        self.txt_resultado.configure(state="disabled")

    def mostrar_feedback(self, mensagem, cor="red"):
        self.lbl_status.configure(text=mensagem, text_color=cor)
        self.after(3500, lambda: self.lbl_status.configure(text=""))

    def criar_entry(self, master, txt):
        return ctk.CTkEntry(master, placeholder_text=txt, width=450, height=40, corner_radius=10)

    # --- MÉTODOS DE FORMATAÇÃO ---

    def validar_apenas_numeros(self, entry):
        texto = entry.get()
        limpo = "".join(filter(str.isdigit, texto))
        if texto != limpo:
            entry.delete(0, "end")
            entry.insert(0, limpo)
        return limpo

    def formatar_cpf(self, event):
        if event.keysym == "BackSpace": return
        nums = self.validar_apenas_numeros(self.ent_cpf)
        if len(nums) > 11: nums = nums[:11]
        f = ""
        for i, n in enumerate(nums):
            if i in [3, 6]: f += "."
            if i == 9: f += "-"
            f += n
        self.ent_cpf.delete(0, "end")
        self.ent_cpf.insert(0, f)

    def formatar_data(self, event):
        if event.keysym == "BackSpace": return
        nums = self.validar_apenas_numeros(self.ent_nasc)
        if len(nums) > 8: nums = nums[:8]
        f = ""
        for i, n in enumerate(nums):
            if i in [2, 4]: f += "/"
            f += n
        self.ent_nasc.delete(0, "end")
        self.ent_nasc.insert(0, f)

    def formatar_moeda(self, entry):
        texto = entry.get().replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".").strip()
        try:
            if not texto: return
            valor = float(texto)
            formatado = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            entry.delete(0, "end")
            entry.insert(0, formatado)
        except ValueError: pass

    def limpar(self):
        for e in [self.ent_nome, self.ent_cpf, self.ent_nasc, self.ent_civil, self.ent_end, self.ent_cargo, self.ent_salario]:
            e.delete(0, "end")
        self.ent_busca_id.delete(0, "end")
        
        self.txt_resultado.configure(state="normal")
        self.txt_resultado.delete("1.0", "end")
        self.txt_resultado.insert("0.0", "Detalhes do contrato do funcionário aparecerão aqui...")
        self.txt_resultado.configure(state="disabled")

        self.id_editando = None
        self.btn_salvar.configure(text="💾 Salvar / Atualizar", fg_color="green")
        self.btn_exc.configure(state="disabled")
        self.btn_cancelar.pack_forget()

    def buscar_funcionario(self):
        id_digitado = self.ent_busca_id.get()
        if not id_digitado: return
        
        res = buscar_funcionario_por_id_func(id_digitado)
        self.func_atual = res
        
        if res:
            self.preparar_edicao()
            self.btn_exc.configure(state="normal")
            self.btn_cancelar.pack(side="left", padx=5)
            
            self.txt_resultado.configure(state="normal")
            self.txt_resultado.delete("1.0", "end")
            info = f"FUNCIONÁRIO ENCONTRADO:\n\n"
            info += f"Matrícula: {res['id']} | Cargo: {res['cargo']}\n"
            info += f"CPF: {res['cpf']} | E-mail: {res['email']}\n"
            info += f"Salário: R$ {res['salario']:,.2f}"
            self.txt_resultado.insert("0.0", info)
            self.txt_resultado.configure(state="disabled")
            
            self.mostrar_feedback("✅ Dados carregados para edição!", "green")
        else:
            self.btn_exc.configure(state="disabled")
            self.mostrar_feedback("❌ Matrícula não encontrada.")
            self.limpar()

    def preparar_edicao(self):
        # Limpa sem esconder o botão cancelar
        self.ent_nome.delete(0, "end"); self.ent_nome.insert(0, self.func_atual['nome'])
        self.ent_cpf.delete(0, "end"); self.ent_cpf.insert(0, self.func_atual['cpf'])
        self.ent_nasc.delete(0, "end"); self.ent_nasc.insert(0, self.func_atual['nascimento'] or "")
        self.ent_civil.delete(0, "end"); self.ent_civil.insert(0, self.func_atual['estado_civil'] or "")
        self.ent_end.delete(0, "end"); self.ent_end.insert(0, self.func_atual['endereco'] or "")
        self.ent_cargo.delete(0, "end"); self.ent_cargo.insert(0, self.func_atual['cargo'] or "")
        self.ent_email.delete(0, "end"); self.ent_email.insert(0, self.func_atual['email'] or "")
        
        self.ent_salario.delete(0, "end")
        self.ent_salario.insert(0, f"R$ {self.func_atual['salario']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        
        self.id_editando = self.func_atual['id']
        self.btn_salvar.configure(text="🔄 Atualizar Funcionário", fg_color="blue")

    def excluir(self):
        if self.func_atual and messagebox.askyesno("Confirmar", f"Excluir {self.func_atual['nome']} (ID: {self.func_atual['id']})?"):
            if deletar_funcionario_db(self.func_atual['id']):
                self.mostrar_feedback("🗑️ Removido com sucesso!", "orange")
                self.limpar()

    def validar_e_salvar(self):
        nome, cpf, email = self.ent_nome.get(), self.ent_cpf.get(), self.ent_email.get()
        
        if not nome or not cpf or not email:
            self.mostrar_feedback("⚠️ Nome, CPF e E-mail são obrigatórios.")
            return

        # Script 41: Validação rigorosa de e-mail (Ex: nome@dominio.com)
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            self.mostrar_feedback("❌ E-mail incompleto (ex: nome@gmail.com).")
            return
            
        try:
            # Extrai apenas os números para converter para float
            val_str = self.ent_salario.get().replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")
            salario = float(val_str or 0)
        except:
            self.mostrar_feedback("❌ Salário inválido.")
            return

        # Script 41: Validação de salário irreal (deve ser positivo)
        if salario <= 0:
            self.mostrar_feedback("❌ O salário informado é inválido/irreal.")
            return

        if self.id_editando:
            if atualizar_funcionario_db(self.id_editando, nome, cpf, self.ent_nasc.get(), self.ent_civil.get(), self.ent_end.get(), self.ent_cargo.get(), salario, email):
                self.mostrar_feedback("✅ Dados atualizados!", "green")
                self.limpar()
        else:
            novo_id = salvar_funcionario(nome, cpf, self.ent_nasc.get(), self.ent_civil.get(), self.ent_end.get(), self.ent_cargo.get(), salario, email)
            if novo_id: 
                self.mostrar_feedback(f"✅ Cadastrado! ID: {novo_id}", "green")
                self.limpar()