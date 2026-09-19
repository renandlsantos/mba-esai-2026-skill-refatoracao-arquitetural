# Compatibilidade e limites

Métodos e paths: 44/44 preservados e testados; nomes internos dos parâmetros de rota podem mudar sem alterar URLs. Payloads válidos principais, listagens, CRUD e relatórios são caracterizados no baseline e exercitados após refatorar.

Mudanças intencionais de segurança:

- Shop: senha/hash e secret_key/debug/db_path deixam respostas. SQL sempre usa parâmetros. Números finitos, tipos e IDs são validados; inexistentes retornam 404, email duplicado 409. Itens repetidos são combinados antes de checar estoque. Pedido inteiro faz rollback em falha. `/admin/reset-db` exige token e opt-in; `/admin/query` exige token e permite apenas `SELECT 1 AS value`, `SELECT COUNT(*) AS total FROM produtos`, `SELECT COUNT(*) AS total FROM pedidos`. SQL arbitrário foi removido. CORS wildcard e debug foram retirados.
- LMS: checkout exige senha não vazia, email válido, ID inteiro e cartão sintético textual de 13..19 dígitos. Conta existente exige senha correta. Pagamento continua simulador local: prefixo 4 aprova; não use dados reais. Erro/recusa não deixam usuário/matrícula/pagamento parcial. Relatório e exclusão exigem token; exclusão remove pagamentos/matrículas dependentes. Resposta de exclusão já não afirma que há dados órfãos. Corpo excessivo retorna 413; erros retornam JSON sanitizado. Sem cache global. Catálogo de exemplo só entra com SEED_DEMO=true em banco vazio; nenhuma conta com senha fixa é criada.
- Tasks: serializers omitem hashes; login emite token assinado e temporizado. Isso não instala autenticação geral: nenhum consumidor deve tratar as rotas locais como serviço multiusuário protegido. Verificador limita token a 3600 s por padrão, detecta alteração e testa expiração. SECRET_KEY aleatória por instância se não configurada; tokens deixam de validar após restart nesse caso. Atualizações validam tudo antes de mutar. Deletar categoria torna referências nulas; deletar usuário remove tarefas, como no comportamento original. Seed exige --demo, senha explícita e banco vazio. UTC-naive é mantido explicitamente na fronteira SQLite para compatibilidade com schema existente.

Dados e migração:

Nenhum banco preexistente foi utilizado no desenvolvimento. Schemas existentes não são destruídos. Shop/Tasks reconhecem senhas antigas somente com ALLOW_LEGACY_PASSWORDS=true; uma autenticação correta atualiza o hash para scrypt. O modo fica desligado por padrão, deve ser habilitado apenas em migração planejada e depois removido. LMS rejeita hashes legados inadequados; contas existentes precisam reset/migração fora deste escopo, não são reinterpretadas como hashes seguros. Os testes exercitam o opt-in Shop/Tasks e a rejeição LMS.

Erros, observabilidade e produção:

Respostas internas de exceção são sanitizadas. Logs de teste não incluem senhas/cartões/chaves. Ausência de achados remanescentes no escopo não prova ausência de toda vulnerabilidade. Não há gateway real, autenticação geral, autorização por recurso, rate limiting, backups ou hardening de produção; são aplicações educacionais locais. Não há claims de throughput; contagens de consultas são medidas nos testes.

Isolamento de configuração: a primeira rodada de smoke do Tasks revelou avisos do python-dotenv tentando interpretar um .env ancestral. O arquivo externo não foi lido nem exibido pelo agente. Boot agora usa app.run(load_dotenv=False) nos dois Flask e o harness define FLASK_SKIP_DOTENV=1, com URLs de banco temporário explícitas. Smoke foi repetido após a correção.
