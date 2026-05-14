import customtkinter as ctk
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

        self.title("Gerenciamento de Funcionários - Xô Sujeira")
        self.geometry("700x800")
        self.resizable(False, False)
        self.grab_set()

        self.id_editando = None
        self.func_atual = None

        ctk.CTkLabel(self, text="Módulo de Funcionários", font=("Roboto", 28, "bold")).pack(pady=20)

        self.tabview = ctk.CTkTabview(self, width=650, height=650)
        self.tabview.pack(padx=20, pady=10, fill="both", expand=True)
        
        self.tab_cad = self.tabview.add("Cadastrar")
        self.tab_bus = self.tabview.add("Buscar/Editar")

        self.ent_nome = self.criar_entry(self.tab_cad, "Nome Completo")
        self.ent_cpf = self.criar_entry(self.tab_cad, "CPF")
        self.ent_nasc = self.criar_entry(self.tab_cad, "Data de Nascimento (DD/MM/AAAA)")
        self.ent_civil = self.criar_entry(self.tab_cad, "Estado Civil")
        self.ent_end = self.criar_entry(self.tab_cad, "Endereço")
        self.ent_cargo = self.criar_entry(self.tab_cad, "Cargo")
        self.ent_salario = self.criar_entry(self.tab_cad, "Salário (Ex: 2500.00)")

        for e in [self.ent_nome, self.ent_cpf, self.ent_nasc, self.ent_civil, self.ent_end, self.ent_cargo, self.ent_salario]:
            e.pack(pady=5)

        self.btn_salvar = ctk.CTkButton(self.tab_cad, text="Salvar Funcionário", fg_color="green", command=self.validar_e_salvar)
        self.btn_salvar.pack(pady=20)

        self.frame_bus = ctk.CTkFrame(self.tab_bus, fg_color="transparent")
        self.frame_bus.pack(pady=10, fill="x", padx=20)
        
        self.ent_busca_id = ctk.CTkEntry(self.frame_bus, placeholder_text="ID de 5 dígitos...", width=200)
        self.ent_busca_id.pack(side="left", padx=10)
        
        ctk.CTkButton(self.frame_bus, text="Buscar", width=100, command=self.buscar_funcionario).pack(side="left")

        self.txt_res = ctk.CTkTextbox(self.tab_bus, width=550, height=250)
        self.txt_res.pack(pady=10)
        self.txt_res.configure(state="disabled")

        self.btn_edit = ctk.CTkButton(self.tab_bus, text="Editar", state="disabled", command=self.preparar_edicao)
        self.btn_edit.pack(side="left", padx=50, pady=10)

        self.btn_exc = ctk.CTkButton(self.tab_bus, text="Excluir", fg_color="red", state="disabled", command=self.excluir)
        self.btn_exc.pack(side="right", padx=50, pady=10)

    def criar_entry(self, master, txt):
        return ctk.CTkEntry(master, placeholder_text=txt, width=450, height=35)

    def limpar(self):
        for e in [self.ent_nome, self.ent_cpf, self.ent_nasc, self.ent_civil, self.ent_end, self.ent_cargo, self.ent_salario]:
            e.delete(0, "end")
        self.id_editando = None
        self.btn_salvar.configure(text="Salvar Funcionário", fg_color="green")

    def buscar_funcionario(self):
        id_digitado = self.ent_busca_id.get()
        res = buscar_funcionario_por_id_func(id_digitado)
        self.func_atual = res
        self.txt_res.configure(state="normal")
        self.txt_res.delete("1.0", "end")
        if res:
            info = f"ID: {res['id']}\nNome: {res['nome']}\nCPF: {res['cpf']}\nCargo: {res['cargo']}\nSalário: R$ {res['salario']:.2f}"
            self.txt_res.insert("0.0", info)
            self.btn_edit.configure(state="normal")
            self.btn_exc.configure(state="normal")
        else:
            self.txt_res.insert("0.0", "Funcionário não encontrado.")
            self.btn_edit.configure(state="disabled")
            self.btn_exc.configure(state="disabled")
        self.txt_res.configure(state="disabled")

    def preparar_edicao(self):
        if self.func_atual:
            self.limpar()
            self.id_editando = self.func_atual['id']
            self.ent_nome.insert(0, self.func_atual['nome'])
            self.ent_cpf.insert(0, self.func_atual['cpf'])
            self.ent_nasc.insert(0, self.func_atual['nascimento'] or "")
            self.ent_civil.insert(0, self.func_atual['estado_civil'] or "")
            self.ent_end.insert(0, self.func_atual['endereco'] or "")
            self.ent_cargo.insert(0, self.func_atual['cargo'] or "")
            self.ent_salario.insert(0, str(self.func_atual['salario']))
            self.btn_salvar.configure(text="Atualizar Dados", fg_color="blue")
            self.tabview.set("Cadastrar")

    def excluir(self):
        if self.func_atual and messagebox.askyesno("Confirmar", f"Excluir {self.func_atual['nome']} (ID: {self.func_atual['id']})?"):
            if deletar_funcionario_db(self.func_atual['id']):
                messagebox.showinfo("Sucesso", "Removido!")
                self.buscar_funcionario()

    def validar_e_salvar(self):
        nome, cpf = self.ent_nome.get(), self.ent_cpf.get()
        if not nome or not cpf:
            messagebox.showwarning("Atenção", "Nome e CPF são obrigatórios.")
            return
        try:
            salario = float(self.ent_salario.get() or 0)
        except:
            messagebox.showwarning("Erro", "Salário inválido.")
            return

        if self.id_editando:
            if atualizar_funcionario_db(self.id_editando, nome, cpf, self.ent_nasc.get(), self.ent_civil.get(), self.ent_end.get(), self.ent_cargo.get(), salario):
                messagebox.showinfo("Sucesso", "Atualizado!"); self.limpar(); self.tabview.set("Buscar/Editar")
        else:
            novo_id = salvar_funcionario(nome, cpf, self.ent_nasc.get(), self.ent_civil.get(), self.ent_end.get(), self.ent_cargo.get(), salario)
            if novo_id: messagebox.showinfo("Sucesso", f"Cadastrado! ID: {novo_id}"); self.limpar()