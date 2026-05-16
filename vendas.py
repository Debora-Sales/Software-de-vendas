import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from database import (
    buscar_cliente_por_id, 
    buscar_produto_por_id, 
    buscar_vendedor_por_barcode,
    registrar_venda_db
)

class JanelaVendas(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("Sistema de Vendas - Xô Sujeira")
        self.geometry("900x800")
        self.resizable(False, False)
        self.grab_set()

        # Estado da Venda
        self.carrinho = []
        self.cliente_selecionado = None
        self.vendedor_atual = None

        # --- UI LAYOUT ---
        ctk.CTkLabel(self, text="Ponto de Venda (Checkout)", font=("Roboto", 28, "bold")).pack(pady=15)

        # Label de Status/Feedback (para erros de busca e estoque)
        self.lbl_status = ctk.CTkLabel(self, text="", font=("Roboto", 14, "bold"))
        self.lbl_status.pack(pady=5)

        # Frame Superior: Cliente e Vendedor
        self.frame_topo = ctk.CTkFrame(self)
        self.frame_topo.pack(padx=20, pady=10, fill="x")

        # Coluna Cliente
        self.frame_cli = ctk.CTkFrame(self.frame_topo, fg_color="transparent")
        self.frame_cli.grid(row=0, column=0, padx=10, pady=10)
        ctk.CTkLabel(self.frame_cli, text="ID Cliente:", font=("Roboto", 12, "bold")).pack()
        self.ent_id_cliente = ctk.CTkEntry(self.frame_cli, placeholder_text="Ex: 1", width=100)
        self.ent_id_cliente.pack()
        self.ent_id_cliente.bind("<KeyRelease>", lambda e: self.validar_numeros(self.ent_id_cliente))
        
        self.btn_buscar_cli = ctk.CTkButton(self.frame_topo, text="Validar Cliente", width=120, command=self.buscar_cliente)
        self.btn_buscar_cli.grid(row=0, column=1, padx=5, pady=(20, 0))

        self.lbl_cliente_nome = ctk.CTkLabel(self.frame_topo, text="Cliente: Não selecionado", font=("Roboto", 12, "italic"))
        self.lbl_cliente_nome.grid(row=0, column=2, padx=20, pady=(20, 0))

        # Coluna Vendedor (Bipar Barcode)
        self.frame_vend = ctk.CTkFrame(self.frame_topo, fg_color="transparent")
        self.frame_vend.grid(row=0, column=3, padx=10)
        ctk.CTkLabel(self.frame_vend, text="Código Vendedor:", font=("Roboto", 12, "bold")).pack()
        self.ent_barcode_vend = ctk.CTkEntry(self.frame_vend, placeholder_text="Bipar Barcode", width=180)
        self.ent_barcode_vend.pack()
        self.ent_barcode_vend.bind("<KeyRelease>", self.verificar_vendedor_automatico)

        self.lbl_vendedor_nome = ctk.CTkLabel(self.frame_topo, text="Vendedor: ---", font=("Roboto", 12, "bold"), text_color="teal")
        self.lbl_vendedor_nome.grid(row=0, column=4, padx=10, pady=(20, 0))

        # Frame Central: Adicionar Produtos
        self.frame_prod = ctk.CTkLabel(self, text="Adicionar Itens ao Carrinho", font=("Roboto", 16, "bold"))
        self.frame_prod.pack(pady=(10,0))
        
        self.frame_add = ctk.CTkFrame(self)
        self.frame_add.pack(padx=20, pady=5, fill="x")

        self.frame_id_p = ctk.CTkFrame(self.frame_add, fg_color="transparent")
        self.frame_id_p.pack(side="left", padx=10, pady=10)
        ctk.CTkLabel(self.frame_id_p, text="ID Produto:", font=("Roboto", 11)).pack()
        self.ent_id_prod = ctk.CTkEntry(self.frame_id_p, placeholder_text="ID", width=120)
        self.ent_id_prod.pack()
        self.ent_id_prod.bind("<KeyRelease>", lambda e: self.validar_numeros(self.ent_id_prod))

        self.frame_qnt_p = ctk.CTkFrame(self.frame_add, fg_color="transparent")
        self.frame_qnt_p.pack(side="left", padx=5)
        ctk.CTkLabel(self.frame_qnt_p, text="Qtd:", font=("Roboto", 11)).pack()
        self.ent_qnt = ctk.CTkEntry(self.frame_qnt_p, placeholder_text="Qtd", width=70)
        self.ent_qnt.pack()
        self.ent_qnt.insert(0, "1")

        self.btn_add = ctk.CTkButton(self.frame_add, text="+ Adicionar", fg_color="green", command=self.adicionar_item)
        self.btn_add.pack(side="left", padx=10, pady=(15, 0))

        # Carrinho (Listagem/CRUD)
        self.lbl_cart = ctk.CTkLabel(self, text="Itens no Carrinho", font=("Roboto", 14))
        self.lbl_cart.pack(pady=5)

        self.cart_scroll = ctk.CTkScrollableFrame(self, width=800, height=300)
        self.cart_scroll.pack(padx=20, pady=5, fill="both", expand=True)

        # Frame Inferior: Total e Pagamento
        self.frame_fim = ctk.CTkFrame(self, height=100)
        self.frame_fim.pack(padx=20, pady=20, fill="x")

        self.lbl_total = ctk.CTkLabel(self.frame_fim, text="TOTAL: R$ 0,00", font=("Roboto", 24, "bold"), text_color="orange")
        self.lbl_total.pack(side="left", padx=20)

        self.check_avista = ctk.CTkCheckBox(self.frame_fim, text="Pagamento à Vista (10% Desc.)", command=self.atualizar_total_display)
        self.check_avista.pack(side="left", padx=20)

        self.btn_finalizar = ctk.CTkButton(self.frame_fim, text="FINALIZAR VENDA", height=50, fg_color="blue", font=("Roboto", 18, "bold"), command=self.finalizar_venda)
        self.btn_finalizar.pack(side="right", padx=20)

    def validar_numeros(self, entry):
        texto = entry.get()
        if not texto.isdigit() and texto != "":
            entry.delete(0, "end")
            entry.insert(0, "".join(filter(str.isdigit, texto)))
            
    def mostrar_feedback(self, mensagem, cor="red"):
        """Exibe uma mensagem na janela por 3 segundos e depois limpa"""
        self.lbl_status.configure(text=mensagem, text_color=cor)
        self.after(3000, lambda: self.lbl_status.configure(text=""))

    def buscar_cliente(self):
        id_cli = self.ent_id_cliente.get()
        cli = buscar_cliente_por_id(id_cli)
        if cli:
            self.cliente_selecionado = cli
            self.lbl_cliente_nome.configure(text=f"Cliente: {cli['nome']}", text_color="cyan")
        else:
            self.mostrar_feedback("⚠️ Cliente não encontrado.")
            self.cliente_selecionado = None

    def verificar_vendedor_automatico(self, event):
        """Busca o vendedor em tempo real conforme o código é inserido ou apagado"""
        barcode = self.ent_barcode_vend.get().strip()
        
        if not barcode:
            self.lbl_vendedor_nome.configure(text="Vendedor: ---", text_color="teal")
            self.vendedor_atual = None
            return

        nome = buscar_vendedor_por_barcode(barcode)
        if nome:
            self.vendedor_atual = barcode
            self.lbl_vendedor_nome.configure(text=f"Vendedor: {nome}", text_color="green")
        else:
            self.lbl_vendedor_nome.configure(text="Vendedor: Não encontrado", text_color="red")
            self.vendedor_atual = None

    def adicionar_item(self):
        id_p = self.ent_id_prod.get()
        qtd_txt = self.ent_qnt.get()
        
        if not id_p or not qtd_txt: return
        
        prod = buscar_produto_por_id(id_p)
        if not prod:
            self.mostrar_feedback("❌ Produto não encontrado.")
            return

        # RN01: Validação de Validade
        try:
            val_prod = datetime.strptime(prod['validade'], "%d/%m/%Y")
            if val_prod < datetime.now():
                self.mostrar_feedback("🚫 Produto VENCIDO! Venda proibida.")
                return
        except: pass

        # RN05: Estoque Real
        qtd = int(qtd_txt)
        
        # Verifica quanto desse produto já existe no carrinho para validar o limite real
        qtd_no_carrinho = sum(item['qnt'] for item in self.carrinho if item['id_prod'] == prod['id'])
        total_desejado = qtd + qtd_no_carrinho

        if prod['quantidade'] < total_desejado:
            self.mostrar_feedback(f"⚠️ Sem estoque! (Disp: {prod['quantidade']} | No carrinho: {qtd_no_carrinho})")
            return

        # Adicionar ao Carrinho (CRUD - Create)
        item = {
            "id_prod": prod['id'],
            "nome": prod['nome'],
            "preco": prod['preco_venda'],
            "qnt": qtd,
            "subtotal": prod['preco_venda'] * qtd
        }
        self.carrinho.append(item)
        self.atualizar_carrinho_ui()
        self.ent_id_prod.delete(0, "end")
        self.ent_qnt.delete(0, "end")
        self.ent_qnt.insert(0, "1")

    def remover_item(self, index): # CRUD - Delete
        self.carrinho.pop(index)
        self.atualizar_carrinho_ui()

    def atualizar_carrinho_ui(self): # CRUD - Read
        for widget in self.cart_scroll.winfo_children():
            widget.destroy()

        for i, item in enumerate(self.carrinho):
            f = ctk.CTkFrame(self.cart_scroll)
            f.pack(fill="x", pady=2)
            
            ctk.CTkLabel(f, text=f"{item['nome']}", width=250, anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(f, text=f"Qtd: {item['qnt']}", width=100).pack(side="left")
            ctk.CTkLabel(f, text=f"UN: R$ {item['preco']:.2f}", width=120).pack(side="left")
            ctk.CTkLabel(f, text=f"Sub: R$ {item['subtotal']:.2f}", width=120, font=("", 12, "bold")).pack(side="left")
            
            ctk.CTkButton(f, text="X", width=30, fg_color="red", command=lambda idx=i: self.remover_item(idx)).pack(side="right", padx=10)

        self.atualizar_total_display()

    def calcular_total(self):
        total = sum(item['subtotal'] for item in self.carrinho)
        if self.check_avista.get(): # RN03: Desconto 10%
            total *= 0.90
        return total

    def atualizar_total_display(self):
        t = self.calcular_total()
        self.lbl_total.configure(text=f"TOTAL: R$ {t:.2f}")

    def finalizar_venda(self):
        if not self.cliente_selecionado:
            messagebox.showwarning("Atenção", "Selecione um cliente.")
            return
        if not self.vendedor_atual:
            messagebox.showwarning("Atenção", "Identifique o vendedor (bipar barcode).")
            return
        if not self.carrinho:
            messagebox.showwarning("Carrinho", "Adicione produtos.")
            return

        total = self.calcular_total()
        forma = "À Vista" if self.check_avista.get() else "Prazo/Outros"

        confirmar = messagebox.askyesno("Confirmar", f"Finalizar venda no valor de R$ {total:.2f}?")
        if confirmar:
            id_venda = registrar_venda_db(
                self.vendedor_atual, 
                self.cliente_selecionado['id'], 
                total, 
                forma, 
                self.carrinho
            )
            if id_venda:
                messagebox.showinfo("Sucesso", f"Venda #{id_venda} realizada com sucesso!")
                self.carrinho = []
                self.cliente_selecionado = None
                self.vendedor_atual = None
                self.destroy()