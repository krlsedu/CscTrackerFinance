Aqui está o Release Notes técnico para a versão v26.29.001, baseado no log de commits fornecido:

# Release Notes - v26.29.001

## 🚀 Features
- **TransactionHandler:** Adicionada lógica para detecção e tratamento de cashback.
- **TransactionHandler:** Adicionado suporte e refatoração para pagamentos parcelados (installments).
- **TransactionHandler:** Adicionada flag `is_installment` caso o `id` não exista na transação.
- **TransactionHandler:** Adicionada categoria 'Ignored' para determinadas transações.
- **CI/CD:** Adicionado workflow do GitHub Actions para releases baseadas em tags (`release-file.yml`).
- **CI/CD:** Atualizado `Jenkinsfile` para deploy automático, notificações e versionamento automático.
- **Testes:** Adicionados testes unitários para a lógica de cashback no `TransactionHandler`.

## 🐛 Fixes
- **TransactionHandler:** Corrigida a lógica de `save_transactions` e tratamento de mensagens de resposta.
- **TransactionHandler:** Removido o campo `id` da transação e adicionada verificação de existência do `id`.
- **TransactionHandler:** Refatorado o padrão regex para extração de nomes.
- **TransactionHandler:** Refatorado o parsing de datas.
- **TransactionHandler:** Substituídos caracteres especiais na chave da transação.
- **TransactionHandler:** Refatorada a lógica de verificação de existência da transação e tratamento de erros.
- **TransactionHandler:** Adicionado tratamento de exceções ao salvar transações.
- **App:** Removido `Interceptor.py` e `LoadBalancerRegister.py` não utilizados, refatorando o fluxo principal.

## 🔧 Chore
- **Docker:** Adicionado arquivo `.dockerignore` para excluir arquivos desnecessários da imagem.
- **Dependências:** Atualizações recorrentes da biblioteca `csctracker-py-core` e `csctracker-queue-scheduler` no `requirements.txt`.
- **Builds:** Múltiplos commits de trigger de build e atualização de versão no `version.txt`.
- **Merge:** Resolução de merges da branch `origin/master`.
- **Logs:** Refinamento dos logs de transação e impressão de erros no `TransactionHandler`.
- **Métricas:** Adicionada label padrão de métricas no `Jenkinsfile`.