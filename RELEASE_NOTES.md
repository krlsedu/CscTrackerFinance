# Release Notes - v26.29.003

**Data:** 2026

Abaixo estão as atualizações técnicas referentes à versão `v26.29.003`. 

### 🚀 Features
* **Cashback / Transações:** Adicionado o campo `category` para o mapeamento de transações de cashback dentro do serviço `TransactionHandler`. 
  *(Commit: `45380da` - por Carlos Eduardo Duarte Schwalm)*

### 🐛 Fixes
* *Nenhuma correção de bug registrada nesta versão.*

### 🔧 Chore
* *Nenhuma tarefa de manutenção ou refatoração estrutural registrada nesta versão.*

---
*Nota do Tech Lead: A alteração no `TransactionHandler.py` é pontual (1 linha), mas certifiquem-se de que os consumidores deste serviço (APIs ou workers) estejam preparados para receber e processar o novo payload contendo o campo `category`.*