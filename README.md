# 🚀 Aprendendo Git Branches - SENAC Jaboticabal

Bem-vindo ao repositório de estudos sobre controle de versão com Git! Este projeto foi desenvolvido como parte das atividades do **Curso Técnico em Informática do SENAC Jaboticabal**, com o objetivo de dominar a manipulação de ramificações (branches) e o fluxo de trabalho colaborativo.

---

## 📋 Objetivo do Repositório

O foco principal deste projeto é praticar o isolamento do desenvolvimento de novas funcionalidades, correções de bugs e experimentos, garantindo que a linha principal de produção (`main`) permaneça sempre estável.

## 🛠️ Comandos Praticados

Durante as aulas, exploramos os seguintes comandos fundamentais:

* **Criar uma nova branch:** `git branch nome-da-branch`
* **Trocar de branch:** `git checkout nome-da-branch` (ou `git switch nome-da-branch`)
* **Criar e trocar simultaneamente:** `git checkout -b nova-funcionalidade`
* **Listar branches locais:** `git branch`
* **Mesclar alterações:** `git merge nome-da-branch`
* **Deletar uma branch (pós-merge):** `git branch -d nome-da-branch`

## 🌿 Estrutura de Trabalho

Para este exercício, estamos simulando um ambiente real com a seguinte hierarquia:

1.  **`main`**: Contém apenas o código final e estável.
2.  **`develop`**: Branch de integração onde as funcionalidades são testadas juntas.
3.  **`feature/`**: Branches temporárias para criação de recursos específicos.
4.  **`fix/`**: Branches dedicadas a correções rápidas de erros.

---

## 🎓 Informações do Aluno

Este repositório faz parte da Unidade Curricular de desenvolvimento de sistemas.

* **Instituição:** SENAC Jaboticabal - SP
* **Curso:** Técnico em Informática
* **Estudante:** Débora
* **Estudante:** Leonardo

---
*Documento gerado para fins educacionais e guia de consulta rápida.*
