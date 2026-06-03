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

---

## Sprit 7

Criar botão de edição de cadastro de produtos na seção de produtos

---

## Sprint 8 

Criação de botão de exclusão de produto na seção de produtos

---

## Sprint 9 

Criação de botão para limpar o formulário de cadastro de produtos na seção produtos

---

## Sprint 10

Criação de alerta de estoque mínimo na seção de produtos onde a mensagem aparecerá na area de buscar produtos por ID


## Sprit 11

Criar botão de edição de cadastro de clientes na seção de clientes

---

## Sprint 12

Criação de botão de exclusão de clientes na seção de clientes

---

## Sprint 13 

Criação de botão para limpar o formulário de cadastro de clientes na seção clientes

---

## Nota 

Ao finalizar um cadastro, salvar dados, a janela não pode se fechar

---

# Nota 1

No cadastro de clientes os campos de CPF e CNPJ e Razão social foram desbloqueados. Necessário concertar.

---

## Script 14

Criação da janela Funcionários

## Script 15

Os IDs devem ser registrados com base de 5 números aleatórios que não se repetem

## Script 16 

As guias devem ter os campos "Nome completo", "CPF", "RG", "Data de nascimento", "Estado civil", "Endereço", "Cargo", "Salário"

## Script 17

Cancele a busca de ID dos funcionários com 5 dígitos aleatórios e volte a criar normalmente os IDs com 1 dígito


## Script 18

Crie um campo que criará a matricula dos funcionários com 5 dígitos de forma aleatória no banco de dados.

---

## Script 19 

Na seção Clientes, deverá ser necessário mais uma janela para cadastro dos clientes por CPF (Pessoa Física), que de preferência deverá ficar ao lado esquerdo do botão "Buscar Clientes".

## Script 20

Mescle a pasta produtos_ui.py com a produtos.py

---

## Script 21

Mescle a pasta funcionarios_ui.py com a funcionarios.py

---

## Script 22

Faça o código ficar coerente e funcional

---

## Script 23 

A erros no código, corrija

## Script 24 

No módulo Produtos nos é necessário a formatação dos campos 

Campo "nome" segue sem alteração no código

Campo "categoria" segue sem alteração no código

Campo "Lote" deverá conter apenas números 

Campo "Data de validade devera ser formatada automaticamente no formato DD/MM/AAAA

Campo "Estoque" deverá conter apenas números, e apenas de 0 à 100

Campo "Preço de custo" deverá ser formatado automaticamente para R$ 0,00

Campo "Preço de venda" deverá ser formatado automaticamente para R$ 0,00

## Script 25

No módulo Clientes nos é necessário a formatação dos campos e adição de novos campos

Na guia "Pessoa física" altere os seguintes campos:

Campo "Nome" segue sem alteração no código

Campo "Endereço" será repartidos em novos campos inclundo "Rua/Avenida", "Bairro", "Cidade", "Complemento" e deverá ser inserido automaticamente no banco de dados como um dado único.

O campo telefone deverá ser formatato automaticamente no formado 

Formatar campo "telefone" automaticamente para (XX) XXXXX-XXXX para celulares e (XX) XXXX-XXXX para telefones fixos

O campo "telefone" deve introduzir apenas números

Formatar campo "CPF" automaticamente para XXX.XXX.XXX-XX

Formatar campo "RG" automaticamente para XX.XXX.XXX-X

os campos "RG" e "CPF" devem receber apenas números

o campo "e-mail" deve obrigatóriamente ter um @ para ser validado

## Script 26

O módulo funcionarios_ui.py deve ser mesclado com a pasta funcionarios.py

---

O modulo clientes_ui.py deve ser mesclado com a pasta clientes.py

---

Faça o código ficar coerente e funcional

---

finalizando, apague a pasta funcionarios_ui.py e clientes_ui.py


## Script 27

No módulo Clientes nos é necessário a formatação dos campos e adição de novos campos

Na guia "Pessoa Juridica" altere os seguintes campos:

Campo "Nome" segue sem alteração no código

Campo "Endereço" será repartidos em novos campos inclundo "Rua/Avenida", "Bairro", "Cidade", "Complemento" e deverá ser inserido automaticamente no banco de dados como um dado único.

O campo telefone deverá ser formatato automaticamente no formado 

Formatar campo "telefone" automaticamente para (XX) XXXXX-XXXX para celulares e (XX) XXXX-XXXX para telefones fixos

O campo "telefone" deve introduzir apenas números

Formatar campo "CNPJ" automaticamente para XX.XXX.XXX/XXXX-XX

o campo "e-mail" deve obrigatóriamente ter um @ para ser validado

## Script 28 

Na guia "buscar cliente" deverá ser introduzido apenas números

## script 29

-função de abrir janela seguindo a mesma lógica dos outros arquivos
--

## erro 29 c+

-ele não identifica o vendedor por que? como? e como resolver isso
-O estoque não diminui, só aplica o limite de compra
--ele deve diminuir quando o cliente atingir o limite, mesmo que ele adicione o produto depois

## erro 29.1

Não entendi o do vendedor, eu coloco o código de barra deles não identifica

# script 30 

reset do banco de dados para registrar vendas no relatório

# script 31 PRODUTOS V 0.02

CRUD realizado X
botão ação_cancelar busca X
-objetivo fazer o crud em uma única janela em todas as janelas X
-sistema de entrega
-forma de pagamento negativo


# script 32

-cancelamento de venda, aguardar, mensagem
-nivel de urgencia X
-alerta de prazo ?
pré estoque atual---preciso ver uma janela de produtos e também alerta
demandas, metas

gestão de entregas
Controle de Status (O Ciclo de Vida): No banco de dados, criamos o campo status_entrega como "Pendente". Porém, ainda não temos uma tela para o pessoal do estoque/logística mudar esse status para "Em Rota" ou "Entregue". 

Impressão de Romaneio/Etiqueta: Para uma entrega B2B, é comum precisar imprimir um papel com o endereço do cliente e a lista de produtos para o motorista levar.

Variação de Frete por Urgência: Atualmente, "Normal" e "Crítico" custam os mesmos R$ 10,00. Em sistemas mais complexos, uma entrega "Crítica" costuma ter uma taxa de urgência maior.


# script 33

-tabela de frete, aumento de preço do combustivel
-gráficos na tabela do adm
preço dos produtos
-layout



Segunda-feira 25 de maio de 2026

# script 

Deverá ser adicionado 3 tipos de usuários

- Administrador (manteremos o login e a senha atual - Login: Admin - Senha: Admin123)
- Vendedor (Login: Vendedor - Senha: Vendedor123)
- Estoquista (Login: Estoquista - Senha: Estoquista123)

- O login de vendedores deverá Aparecer somente o módulo de "vendas" e "clientes" 
- O login de estoquistas deverá aparecer somente o módulo de "Produtos"
- O login do Administrador não deverá ser alterado

# script 

- Os vendedores poderão adicionar clientes, mas só o administrador poderá excluir e alterar os dados dos clientes
- Os estoquistas poderão adicionar produtos, editar produtos e apagar produtos

# script

O software irá trabalhar com o relogio de tempo em tempo real, será atualizado através do relógio da maquina que ele está trabalhando
Com ele, iremos estippular algumas regras 

- No módulo de vendas, deverá ser introduzido uma regra onde o usuário não poderá cadastrar um produto com a data de validade anterior ao dia atual (data de validade vencida)
- Na janela de vendas, será estipulado em quantos dias o frete chegará ao nosso cliente (contando em dias uteis)

# script

Queremos criar um looby na primeira janela que abrimos logo após logarmos no software. 
Quando logarmos como Administrador, ele devera nos mostrar informações relevantes para administrar as vendas
-Deverá aparecer os produtos mais vendidos organizados em posições 1°, 2°, 3° e assim por diante com relação a quantidade vendida
-Deverá aparecer os produtos que estão em baixo estoque organizados por qual está com o estoque mais baixo
-Deverá aparecer os vendedores organizados em posições 1°, 2°, 3° e assim por diante com relação a quem está vendendo mais, mostrando o valor que cada funcionário fez no mês

# script

- No login de administrador, deverá ser introduzido um módulo novo de configurações do software onde ele poderá alterar alguns detalhes financeiros de regras de negócio

- O Administrador vai conseguir alterar o preço base dos fretes 
- O administrador poderá alterar o nome dos de usurários de todos os usuários
- O Administrador poderá alterar a senha dos logins de totos os usuários

# script 39

Abaixo do indicador de vendedores do mês, adicione modulos iguais porém representando "Dia" e "Semestre". A ordem deverá ser "Dia" abaixo "Mês" e logo abaixo "Semestre".


# script 40

Iremos adicionar um novo módulo para controle de estoque: 
-Os estoquistas: Terão acesso ao terminal de cadastro de produtos e controle de estoque.
-gerecniamento,inventário
-vai aparecer pra vendedor e estoquista esse módulo, o adm vai poder ter acesso 
-entrada e saída de produtos
-total de produtos


# script 41

TRATAMENTO DE ERROS:
limite de estoque X + ou - falta deixar a mesma função e outro limite x
 preenchimento correto de endereço, email X
ajuste de  preço X
saldo global????
estoque minimo  X
 painel
 noção de id
 --vai aparecer no momento de pesquisa, cadastro?????? como saber o id


 # script 42

botão de voltar 
logout
única jánela

# script 43 

No módulo de relatórios, é necessário adicionar dois botões ao lado do botão "Atualizar relatórios"
Botão de exportar dados para "PDF"
Botão de exportar dados para "Excel"