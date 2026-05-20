import customtkinter as ctk
from tkinter import messagebox
from database import (
    obter_vendas_por_vendedor,
    obter_relatorio_lucro_db,
    obter_historico_vendas_db,
    obter_entregas_pendentes_db,
    atualizar_status_entrega_db
)

class JanelaRelatorios(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)

        # Configurações Básicas da Janela (O "Básico no início")
        self.title("Relatórios Financeiros - Xô Sujeira")
        self.geometry("950x850")
        self.resizable(False, False)
        self.grab_set()  # Impede interação com a janela de trás
        self.focus()

        # Cabeçalho Principal
        ctk.CTkLabel(self, text="📊 Gestão Financeira e Resultados", font=("Roboto", 28, "bold")).pack(pady=20)

        # Sistema de Abas (Mesma lógica do Clientes/Produtos)
        self.tabview = ctk.CTkTabview(self, width=900, height=600)
        self.tabview.pack(padx=20, pady=10, fill="both", expand=True)

        self.tab_comissoes = self.tabview.add("Comissões")
        self.tab_lucro = self.tabview.add("Margem de Lucro")
        self.tab_historico = self.tabview.add("Histórico de Vendas")
        self.tab_logistica = self.tabview.add("Gestão de Entregas")

        # Inicialização das interfaces das abas
        self._setup_ui_comissoes()
        self._setup_ui_lucro()
        self._setup_ui_historico()
        self._setup_ui_logistica()

        # Botão de Ação Inferior
        self.btn_atualizar = ctk.CTkButton(
            self, 
            text="🔄 ATUALIZAR RELATÓRIOS", 
            height=50, 
            fg_color="teal", 
            hover_color="#006d6d",
            font=("Roboto", 18, "bold"),
            command=self.carregar_dados
        )
        self.btn_atualizar.pack(pady=25)

        # Carregamento inicial automático
        self.carregar_dados()

    def _setup_ui_comissoes(self):
        header = ctk.CTkFrame(self.tab_comissoes, fg_color="gray30")
        header.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(header, text="Vendedor", width=350, anchor="w", font=("", 12, "bold")).pack(side="left", padx=20)
        ctk.CTkLabel(header, text="Total Vendido", width=200, font=("", 12, "bold")).pack(side="left")
        ctk.CTkLabel(header, text="Comissão (5%)", width=200, font=("", 12, "bold")).pack(side="left")

        self.scroll_comissoes = ctk.CTkScrollableFrame(self.tab_comissoes, width=850, height=450)
        self.scroll_comissoes.pack(padx=10, pady=5, fill="both", expand=True)

    def _setup_ui_lucro(self):
        header = ctk.CTkFrame(self.tab_lucro, fg_color="gray30")
        header.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(header, text="Produto", width=280, anchor="w", font=("", 12, "bold")).pack(side="left", padx=20)
        ctk.CTkLabel(header, text="Qtd", width=60, font=("", 12, "bold")).pack(side="left")
        ctk.CTkLabel(header, text="Receita Bruta", width=150, font=("", 12, "bold")).pack(side="left")
        ctk.CTkLabel(header, text="Custo Total", width=150, font=("", 12, "bold")).pack(side="left")
        ctk.CTkLabel(header, text="Lucro Líquido", width=150, font=("", 12, "bold")).pack(side="left")

        self.scroll_lucro = ctk.CTkScrollableFrame(self.tab_lucro, width=850, height=450)
        self.scroll_lucro.pack(padx=10, pady=5, fill="both", expand=True)

    def _setup_ui_historico(self):
        header = ctk.CTkFrame(self.tab_historico, fg_color="gray30")
        header.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(header, text="ID", width=40, font=("", 11, "bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Vendedor", width=120, anchor="w", font=("", 11, "bold")).pack(side="left")
        ctk.CTkLabel(header, text="Cliente", width=120, anchor="w", font=("", 11, "bold")).pack(side="left")
        ctk.CTkLabel(header, text="Data", width=100, font=("", 11, "bold")).pack(side="left")
        ctk.CTkLabel(header, text="Pagto", width=80, font=("", 11, "bold")).pack(side="left")
        ctk.CTkLabel(header, text="Tipo", width=80, font=("", 11, "bold")).pack(side="left")
        ctk.CTkLabel(header, text="Urgência", width=80, font=("", 11, "bold")).pack(side="left")
        ctk.CTkLabel(header, text="Status", width=90, font=("", 11, "bold")).pack(side="left")
        ctk.CTkLabel(header, text="Total", width=100, font=("", 11, "bold")).pack(side="left")

        self.scroll_historico = ctk.CTkScrollableFrame(self.tab_historico, width=850, height=450)
        self.scroll_historico.pack(padx=10, pady=5, fill="both", expand=True)

    def _setup_ui_logistica(self):
        header = ctk.CTkFrame(self.tab_logistica, fg_color="gray30")
        header.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(header, text="ID", width=40, font=("", 11, "bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Cliente", width=150, anchor="w", font=("", 11, "bold")).pack(side="left")
        ctk.CTkLabel(header, text="Endereço de Entrega", width=250, anchor="w", font=("", 11, "bold")).pack(side="left")
        ctk.CTkLabel(header, text="Urgência", width=80, font=("", 11, "bold")).pack(side="left")
        ctk.CTkLabel(header, text="Status", width=100, font=("", 11, "bold")).pack(side="left")
        ctk.CTkLabel(header, text="Ações Logísticas", width=200, font=("", 11, "bold")).pack(side="left")

        self.scroll_logistica = ctk.CTkScrollableFrame(self.tab_logistica, width=850, height=450)
        self.scroll_logistica.pack(padx=10, pady=5, fill="both", expand=True)

    def mudar_status(self, id_venda, novo_status):
        """Atualiza o status e recarrega a lista."""
        if atualizar_status_entrega_db(id_venda, novo_status):
            messagebox.showinfo("Logística", f"Venda #{id_venda} marcada como '{novo_status}'.")
            self.carregar_dados()

    def carregar_dados(self):
        """Limpa os frames e recarrega os dados do Banco de Dados."""
        # 1. Comissões
        for w in self.scroll_comissoes.winfo_children(): w.destroy()
        for nome, total in obter_vendas_por_vendedor():
            f = ctk.CTkFrame(self.scroll_comissoes)
            f.pack(fill="x", pady=2)
            ctk.CTkLabel(f, text=nome, width=350, anchor="w").pack(side="left", padx=20)
            ctk.CTkLabel(f, text=f"R$ {total:,.2f}", width=200).pack(side="left")
            ctk.CTkLabel(f, text=f"R$ {total*0.05:,.2f}", width=200, text_color="#4CAF50", font=("", 12, "bold")).pack(side="left")

        # 2. Lucratividade (RN04)
        for w in self.scroll_lucro.winfo_children(): w.destroy()
        for nome, qtd, venda, custo in obter_relatorio_lucro_db():
            lucro = (venda or 0) - (custo or 0)
            f = ctk.CTkFrame(self.scroll_lucro)
            f.pack(fill="x", pady=2)
            ctk.CTkLabel(f, text=nome, width=280, anchor="w").pack(side="left", padx=20)
            ctk.CTkLabel(f, text=str(qtd), width=60).pack(side="left")
            ctk.CTkLabel(f, text=f"R$ {venda:,.2f}", width=150).pack(side="left")
            ctk.CTkLabel(f, text=f"R$ {custo:,.2f}", width=150).pack(side="left")
            cor_lucro = "cyan" if lucro >= 0 else "red"
            ctk.CTkLabel(f, text=f"R$ {lucro:,.2f}", width=150, text_color=cor_lucro, font=("", 12, "bold")).pack(side="left")

        # 3. Histórico de Vendas
        for w in self.scroll_historico.winfo_children(): w.destroy()
        dados_historico = obter_historico_vendas_db()
        for id_v, vend, cli, data, total, forma, tipo, urg, status in dados_historico:
            f = ctk.CTkFrame(self.scroll_historico)
            f.pack(fill="x", pady=2)
            ctk.CTkLabel(f, text=str(id_v), width=40).pack(side="left", padx=5)
            ctk.CTkLabel(f, text=vend, width=120, anchor="w").pack(side="left")
            ctk.CTkLabel(f, text=cli, width=120, anchor="w").pack(side="left")
            ctk.CTkLabel(f, text=data, width=100).pack(side="left")
            ctk.CTkLabel(f, text=forma, width=80).pack(side="left")
            
            # Cores para o tipo e urgência para facilitar leitura
            cor_urgencia = "orange" if urg in ["Urgente", "Crítico"] else "gray"
            cor_tipo = "cyan" if tipo == "Entrega" else "gray"
            
            # Lógica para o Status da Entrega (Sucesso)
            texto_status = status
            cor_status = "gray"
            if tipo == "Entrega" and status == "Entregue":
                texto_status = "✅ Sucesso"
                cor_status = "green"
            
            ctk.CTkLabel(f, text=tipo, width=80, text_color=cor_tipo).pack(side="left")
            ctk.CTkLabel(f, text=urg, width=80, text_color=cor_urgencia).pack(side="left")
            ctk.CTkLabel(f, text=texto_status, width=90, text_color=cor_status, font=("", 11, "bold")).pack(side="left")
            ctk.CTkLabel(f, text=f"R$ {total:,.2f}", width=100, text_color="orange", font=("", 11, "bold")).pack(side="left")

        # 4. Gestão de Logística
        for w in self.scroll_logistica.winfo_children(): w.destroy()
        dados_logistica = obter_entregas_pendentes_db()
        for id_v, cli, ender, urg, status in dados_logistica:
            f = ctk.CTkFrame(self.scroll_logistica)
            f.pack(fill="x", pady=2)
            
            ctk.CTkLabel(f, text=str(id_v), width=40).pack(side="left", padx=5)
            ctk.CTkLabel(f, text=cli, width=150, anchor="w").pack(side="left")
            ctk.CTkLabel(f, text=ender, width=250, anchor="w", font=("", 10)).pack(side="left")
            
            cor_urgencia = "red" if urg == "Crítico" else "orange" if urg == "Urgente" else "gray"
            ctk.CTkLabel(f, text=urg, width=80, text_color=cor_urgencia, font=("", 11, "bold")).pack(side="left")
            
            cor_status = "cyan" if status == "Em Rota" else "yellow"
            ctk.CTkLabel(f, text=status, width=100, text_color=cor_status).pack(side="left")

            # Botões de Ação Logística
            ctk.CTkButton(f, text="🚛 Em Rota", width=90, height=24, fg_color="#1f538d", 
                          command=lambda iv=id_v: self.mudar_status(iv, "Em Rota")).pack(side="left", padx=5)
            ctk.CTkButton(f, text="✅ Entregue", width=90, height=24, fg_color="green", 
                          command=lambda iv=id_v: self.mudar_status(iv, "Entregue")).pack(side="left", padx=5)

        if not dados_logistica:
            ctk.CTkLabel(self.scroll_logistica, text="Nenhuma entrega pendente encontrada.", text_color="gray").pack(pady=40)
        