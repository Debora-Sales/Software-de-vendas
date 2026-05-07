# Especificação Técnica: Loja Xô Sujeira

Este documento serve como referência para o desenvolvimento do sistema de gestão da Loja Xô Sujeira, focando em controle de estoque, logística B2B e rastreabilidade de validade.

---

## 1. Visão Geral do Projeto
* **Segmento:** Indústria e Comércio de Produtos de Limpeza.
* **Objetivos Principais:** Gestão de estoque com controle de lotes, logística B2B, rastreio de validade e automação de comissões.

---

## 2. Perfis de Acesso (User Personas)

| Perfil | Permissões e Responsabilidades |
| :--- | :--- |
| **Administrador** | Acesso total: relatórios financeiros, margens de lucro, auditoria de estoque (entrada/saída) e controle de validade. |
| **Vendedor** | Registro de pedidos, consulta de preços, cadastro de clientes e consulta de estoque disponível. |
| **Geral / Comum** | Login único com visualização limitada para operações básicas de consulta. |

> **Regra de Identificação:** O sistema de vendas deve integrar a identificação do vendedor via **ID único (Código de Barras)**. Este ID deve ser "bipado" ou inserido obrigatoriamente no ato da venda para processamento e cálculo de comissão.

---

## 3. Requisitos Funcionais (RF)

### 3.1 Módulo de Cadastro e Inventário
* **RF01:** Realizar o cadastro de produtos vinculando obrigatoriamente o **lote** e a **data de validade**.
* **RF01.1:** Realizar o cadastro completo de clientes.
* **RF01.2:** Realizar o cadastro de vendedores (associando o ID único).
* **RF02:** Emitir alertas automáticos quando o estoque atingir a quantidade mínima definida (**Estoque Crítico**).

### 3.2 Módulo de Vendas e Logística
* **RF03:** Permitir a venda de itens exclusivamente por unidade.
* **RF04:** Gerar relatórios de vendas por representante comercial para o cálculo automático de comissões.
* **RF05:** Implementar sistema de frete para gestão de entregas B2B.

---

## 4. Regras de Negócio (RN) e Segurança

### 4.1 Controle de Qualidade e Estoque
* **RN01 (Bloqueio de Validade):** O sistema deve impedir a saída/venda de produtos com data de validade vencida. O controle deve ser feito via cadastro de lotes.
* **RN05 (Estoque Real):** Não permitir a venda de produtos sem saldo disponível em estoque (bloqueio de estoque negativo).

### 4.2 Dados e Financeiro
* **RN02 (Dados Obrigatórios):** Nome/Razão Social, CPF/CNPJ, Endereço de Entrega, Telefone de contato e e-mail.
* **RN03 (Política de Descontos):** Implementar sistema de descontos automáticos para pagamentos realizados à vista.
* **RN04 (Privacidade Financeira):** O cálculo da margem de lucro e relatórios financeiros associados são de visualização exclusiva do perfil **Administrador**.

---

## 5. Estrutura de Acesso e Login
* **Login Individual:** Cada vendedor deve possuir um login único e pessoal para rastreabilidade de ações.
* **Interface de Vendas:** O fluxo de checkout deve exigir o "bip" do ID do vendedor (ou entrada manual do código) para validar a transação.

---

## 6. Checklist de Validação para Desenvolvimento
Antes de considerar uma funcionalidade concluída, valide:
- [ ] O requisito inicia com um verbo de ação claro?
- [ ] O responsável (perfil de acesso) está identificado?
- [ ] Todos os dados obrigatórios de entrada foram validados pelo sistema?
- [ ] Existem travas de segurança para evitar erros humanos (Ex: venda de produto vencido)?