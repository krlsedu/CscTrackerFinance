Aqui está a proposta de Release Notes técnico para a versão **v26.29.005**, estruturada de forma clara e objetiva, ideal para o time de engenharia e stakeholders técnicos.

---

# Release Notes - v26.29.005

### 🚀 Features
*(Nenhuma nova funcionalidade adicionada nesta versão)*

### 🐛 Fixes
*(Nenhuma correção de bug reportada nesta versão)*

### 🔧 Chore
* **Testes & Refatoração:** Adição de cobertura de testes e adequações internas para a lógica de edição de cashback em parcelamentos do Nubank. 
  * **Detalhes técnicos:** Implementação de novos cenários de teste em `test_transaction_handler.py` e ajustes estruturais no serviço `TransactionHandler.py` para suportar a validação da regra de negócio.
  * *Commit:* `022c306` - por Carlos Eduardo Duarte Schwalm (krlsedu)