import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, timedelta
from database import (
    buscar_cliente_por_id, 
    buscar_produto_por_id, 
    buscar_vendedor_por_barcode,
    registrar_venda_db,
    buscar_valor_frete_db
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

        # Script 36: Relógio em tempo real
        self.lbl_clock = ctk.CTkLabel(self, text="", font=("Roboto", 12, "bold"), text_color="gray")
        self.lbl_clock.place(x=20, y=20)
        self.atualizar_relogio()

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
        self.ent_qnt.bind("<KeyRelease>", self.validar_quantidade_venda)

        self.btn_add = ctk.CTkButton(self.frame_add, text="+ Adicionar", fg_color="green", command=self.adicionar_item)
        self.btn_add.pack(side="left", padx=10, pady=(15, 0))

        # Carrinho (Listagem/CRUD)
        self.lbl_cart = ctk.CTkLabel(self, text="Itens no Carrinho", font=("Roboto", 14))
        self.lbl_cart.pack(pady=5)

        self.cart_scroll = ctk.CTkScrollableFrame(self, width=800, height=300)
        self.cart_scroll.pack(padx=20, pady=5, fill="both", expand=True)

        # Frame Inferior: Total e Pagamento
        self.frame_fim = ctk.CTkFrame(self)
        self.frame_fim.pack(padx=20, pady=20, fill="x")

        # Linha 1: Configurações de Logística
        self.f_logistica = ctk.CTkFrame(self.frame_fim, fg_color="transparent")
        self.f_logistica.pack(fill="x", pady=5, padx=10)

        ctk.CTkLabel(self.f_logistica, text="Logística:", font=("Roboto", 11, "bold")).pack(side="left", padx=5)
        self.seg_logistica = ctk.CTkSegmentedButton(self.f_logistica, values=["Retirada", "Entrega"], width=150, command=self.ajustar_frete_automatico)
        self.seg_logistica.set("Retirada")
        self.seg_logistica.pack(side="left", padx=5)

        ctk.CTkLabel(self.f_logistica, text="Urgência:", font=("Roboto", 11, "bold")).pack(side="left", padx=(20, 5))
        self.seg_urgencia = ctk.CTkSegmentedButton(self.f_logistica, values=["Normal", "Urgente", "Crítico"], width=200, selected_color="orange", command=self.ajustar_frete_automatico)
        self.seg_urgencia.set("Normal")
        self.seg_urgencia.pack(side="left", padx=5)
        ctk.CTkLabel(self.f_logistica, text="Distância:", font=("Roboto", 11, "bold")).pack(side="left", padx=(20, 5))
        self.seg_distancia = ctk.CTkSegmentedButton(self.f_logistica, values=["20Km", "50Km", "100Km", "250Km", "500Km", ">500Km"], width=380, selected_color="orange", command=self.ajustar_frete_automatico)
        self.seg_distancia.set("20Km")
        self.seg_distancia.pack(side="left", padx=5)

        ctk.CTkLabel(self.f_logistica, text="Frete R$:", font=("Roboto", 11, "bold")).pack(side="left", padx=(20, 5))
        self.ent_frete = ctk.CTkEntry(self.f_logistica, width=80, state="readonly")
        self.ent_frete.insert(0, "0.00")
        self.ent_frete.pack(side="left", padx=5)

        ctk.CTkLabel(self.f_logistica, text="Entrega Estimada:", font=("Roboto", 11, "bold")).pack(side="left", padx=(20, 5))
        self.lbl_prazo = ctk.CTkLabel(self.f_logistica, text="---", font=("Roboto", 11), text_color="cyan")
        self.lbl_prazo.pack(side="left", padx=5)

        # Linha 2: Financeiro e Ação
        self.f_checkout = ctk.CTkFrame(self.frame_fim, fg_color="transparent")
        self.f_checkout.pack(fill="x", pady=10, padx=10)

        self.lbl_total = ctk.CTkLabel(self.f_checkout, text="TOTAL: R$ 0,00", font=("Roboto", 26, "bold"), text_color="orange")
        self.lbl_total.pack(side="left", padx=20)

        self.check_avista = ctk.CTkCheckBox(self.f_checkout, text="Pagamento à Vista (10% Desc.)", command=self.atualizar_total_display)
        self.check_avista.pack(side="left", padx=20)

        self.btn_finalizar = ctk.CTkButton(self.f_checkout, text="FINALIZAR VENDA", height=55, width=220, fg_color="blue", font=("Roboto", 18, "bold"), command=self.finalizar_venda)
        self.btn_finalizar.pack(side="right", padx=20)

    def atualizar_relogio(self):
        """Script 36: Mantém o tempo real atualizado na interface"""
        agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.lbl_clock.configure(text=f"🕒 Sistema: {agora}")
        self.after(1000, self.atualizar_relogio)

    def validar_numeros(self, entry):
        texto = entry.get()
        if not texto.isdigit() and texto != "":
            entry.delete(0, "end")
            entry.insert(0, "".join(filter(str.isdigit, texto)))
            
    def validar_quantidade_venda(self, event):
        """Script 41: Garante que a quantidade na venda não ultrapasse 100 com feedback visual."""
        texto = self.ent_qnt.get()
        limpo = "".join(filter(str.isdigit, texto))
        
        excedeu = False
        if len(limpo) > 3:
            limpo = limpo[:3]
            excedeu = True

        if limpo and int(limpo) > 100:
            limpo = "100"
            excedeu = True
            
        if excedeu:
            self.mostrar_feedback("⚠️ Máximo de 100 unidades por item.", "red")

        if texto != limpo:
            self.ent_qnt.delete(0, "end")
            self.ent_qnt.insert(0, limpo)

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

    def ajustar_frete_automatico(self, _=None):
        """Define o valor do frete e o prazo de entrega em dias úteis (Script 36)"""
        tipo_logistica = self.seg_logistica.get()
        nivel_urgencia = self.seg_urgencia.get()
        distancia_str = self.seg_distancia.get()
        
        valor_frete = 0.0
        prazo_info = "---"
        
        if tipo_logistica == "Entrega":
            valor_frete = buscar_valor_frete_db(nivel_urgencia, distancia_str)
            
            # Script 36: Regra de Dias Úteis
            dias_base = {"Normal": 5, "Urgente": 2, "Crítico": 1}.get(nivel_urgencia, 5)
            dias_km = {"20Km": 0, "50Km": 0, "100Km": 1, "250Km": 2, "500Km": 3, ">500Km": 5}.get(distancia_str, 0)
            total_uteis = dias_base + dias_km
            
            # Calcular data pulando Finais de Semana (Sáb/Dom)
            data_chegada = datetime.now()
            contagem = 0
            while contagem < total_uteis:
                data_chegada += timedelta(days=1)
                if data_chegada.weekday() < 5: # Segunda (0) a Sexta (4)
                    contagem += 1
            
            prazo_info = f"{total_uteis} dias úteis ({data_chegada.strftime('%d/%m/%Y')})"
        else:
            prazo_info = "Retirada Imediata"

        self.lbl_prazo.configure(text=prazo_info)
        
        self.ent_frete.configure(state="normal")
        self.ent_frete.delete(0, "end")
        self.ent_frete.insert(0, f"{valor_frete:.2f}")
        self.ent_frete.configure(state="readonly")
        self.atualizar_total_display()

    def adicionar_item(self):
        id_p = self.ent_id_prod.get()
        qtd_txt = self.ent_qnt.get()
        
        if not id_p or not qtd_txt: return
        
        prod = buscar_produto_por_id(id_p)
        if not prod:
            self.mostrar_feedback("❌ Produto não encontrado.")
            return

        # RN01 / Script 36: Validação de Validade contra relógio real
        try:
            val_prod = datetime.strptime(prod['validade'], "%d/%m/%Y")
            if val_prod.date() < datetime.now().date():
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
            
        try:
            frete = float(self.ent_frete.get().replace(",", ".")) if self.ent_frete.get() else 0.0
            total += frete
        except ValueError: pass
            
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
        frete = float(self.ent_frete.get().replace(",", ".")) if self.ent_frete.get() else 0.0
        forma = "À Vista" if self.check_avista.get() else "Prazo/Outros"
        tipo_venda = self.seg_logistica.get()
        urgencia = self.seg_urgencia.get()
        distancia = self.seg_distancia.get()

        confirmar = messagebox.askyesno("Confirmar", f"Finalizar venda no valor de R$ {total:.2f}?")
        if confirmar:
            id_venda = registrar_venda_db(
                self.vendedor_atual, 
                self.cliente_selecionado['id'],
                total,         # valor_total (já inclui o frete)
                frete,         # valor_frete
                forma,         # forma_pagamento
                tipo_venda,
                urgencia,
                distancia,
                self.carrinho
            )
            if id_venda:
                self.mostrar_feedback(f"✅ Venda #{id_venda} realizada com sucesso!", "green")
                self.carrinho = []
                self.cliente_selecionado = None
                self.vendedor_atual = None
                self.after(2000, self.destroy)
            else:
                self.mostrar_feedback("❌ Erro ao registrar venda (Verifique estoque).")