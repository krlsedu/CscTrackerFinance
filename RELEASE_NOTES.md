# Release Notes - v26.30.001

**Resumo da Versão:** 
Esta release tem como foco principal a introdução e estruturação do motor de processamento de dividendos da B3, incluindo scripts de automação, rastreabilidade de requisições e rotinas de banco de dados para apuração de lucros e perdas.

---

### 🚀 Features

* **Motor de Processamento de Dividendos (B3):** Implementação do core de processamento de dividendos da B3, integrando a lógica de negócios no `TransactionHandler` e expondo via `app.py`.
* **Rastreabilidade de Transações:** Adicionado suporte para manipulação de `user_id` e `request_id` no fluxo de dividendos, garantindo melhor observabilidade e auditoria das operações.
* **Automação de Dividendos:** Criação do script standalone `process_dividends.py` para execução dedicada das rotinas de proventos.
* **Rotinas de Lucros e Perdas:** Criação do script SQL (`lancar_lucros_e_perdas.sql`) responsável por registrar e contabilizar as transações de lucros e perdas no banco de dados.

### 🐛 Fixes

* *Nenhuma correção de bug mapeada para esta versão.*

### 🔧 Chore

* **Cobertura de Testes:** Criação e expansão significativa dos testes unitários no `test_transaction_handler.py` (mais de 140 linhas de testes adicionadas) para garantir a estabilidade do novo motor de dividendos.
* **Atualização de Dependências:** Atualização do arquivo `requirements.txt` para suportar as novas rotinas implementadas.
* **Manutenção de Banco de Dados:** Refatoração e ajustes nas operações SQL do script `lancar_lucros_e_perdas.sql` para otimização das queries.