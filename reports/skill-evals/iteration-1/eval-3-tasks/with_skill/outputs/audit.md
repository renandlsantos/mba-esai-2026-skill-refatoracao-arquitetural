# Architecture Audit Report: task-manager-api

Baseline: `6d1ce6248c3e956801010a89d8bdaab48029bf30`
Stack observada: Python / Flask 3.0.0 / Flask-SQLAlchemy 3.1.1 / SQLAlchemy 2.0.54 / SQLite.
Domínio: Gerenciamento de usuários, tarefas, categorias e produtividade.
Arquitetura atual: Camadas nominais existentes; rotas concentram regras, SQL e apresentação.
Arquivos fonte: 15; linhas: 1158. Dependências instaladas registradas no baseline; arquivos de skill/testes/dependências excluídos da contagem.

## Summary

CRITICAL: 2 | HIGH: 3 | MEDIUM: 4 | LOW: 2

## Findings

### [CRITICAL] P3-01: Hash de senha exposto e fraco

File: `task-manager-api/models/user.py:16-32`
Description: to_dict inclui password e MD5 sem salt; baseline confirmou hash em respostas.
Impact: Dicionários offline e vazamento de credenciais.
Recommendation: scrypt e serializer público; migração explícita de legado.
Validation: Criar/ler/login nunca expõe hash; senha correta valida.

### [CRITICAL] P3-02: Credenciais hardcoded

File: `task-manager-api/services/notification_service.py:7-10`
Description: Configuração de SMTP contém usuário e senha fixos; app.py:11-13 define secret_key.
Impact: Segredos versionados e risco de envio inadvertido.
Recommendation: Configuração por ambiente; notificações externas desligadas por padrão.
Validation: Nenhum SMTP abre sem configuração/opt-in e testes não fazem rede.

### [HIGH] P3-03: Falso token de autenticação

File: `task-manager-api/routes/user_routes.py:197-211`
Description: Login retorna token derivado apenas do ID e sem assinatura.
Impact: Consumidor pode interpretar identificador forjável como credencial.
Recommendation: Token assinado com expiração quando configurado; explicitar escopo local e ausência de sistema completo de autorização.
Validation: Token alterado falha verificação e expiração é testada.

### [HIGH] P3-04: Rotas acumulam responsabilidades

File: `task-manager-api/routes/task_routes.py:85-223`
Description: Rotas validam, buscam relacionamentos, mutam entidade, persistem e serializam.
Impact: Duplicação e acoplamento impedem testes isolados.
Recommendation: Controller de caso de uso, repositório, validador e view separados.
Validation: Rotas delegam e regressões exercitam caso de uso.

### [HIGH] P3-05: Seed destrutivo por padrão

File: `task-manager-api/seed.py:8-14`
Description: Executar seed elimina tasks, users e categories antes de inserir fixtures.
Impact: Apaga dados existentes sem revisão.
Recommendation: Seed somente para banco vazio; não apagar automaticamente.
Validation: Banco populado é recusado sem alteração.

### [MEDIUM] P3-06: N+1 em listagens

File: `task-manager-api/routes/task_routes.py:14-59`
Description: Cada tarefa busca usuário e categoria; relatórios repetem consultas por usuário.
Impact: Custo cresce com tamanho das listas.
Recommendation: Carregamento eager/consultas em lote e agregações.
Validation: Contagem de queries permanece limitada.

### [MEDIUM] P3-07: Tipos e datas inconsistentes

File: `task-manager-api/routes/task_routes.py:110-144`
Description: Comparação de prioridade e join de tags não verificam tipos.
Impact: Corpos inválidos causam 500; PUT diverge de POST.
Recommendation: Validar objeto e todos os campos antes de mutar.
Validation: JSON lista, boolean priority, tags inválidas e datas retornam 400.

### [MEDIUM] P3-08: API de consulta legada

File: `task-manager-api/routes/task_routes.py:65-67`
Description: Task.query.get é API legada em SQLAlchemy 2.0; outros usos em users/reports.
Impact: Avisos e custo de evolução; não significa método removido.
Recommendation: Usar db.session.get e select/scalars no repositório.
Validation: Testes executam com LegacyAPIWarning convertido em erro.

### [MEDIUM] P3-09: UTC obsoleto no runtime alvo

File: `task-manager-api/models/task.py:15-17`
Description: datetime.utcnow está deprecated desde Python 3.12; há usos em routes/models/helpers.
Impact: Timestamp sem timezone e avisos na evolução do runtime.
Recommendation: Relógio UTC consciente; converter explicitamente ao formato SQLite legado.
Validation: Testes de atraso e data sem DeprecationWarning de utcnow.

### [LOW] P3-10: Imports sem uso

File: `task-manager-api/app.py:7-7`
Description: os, sys e json são importados sem uso; padrões repetidos em outras rotas.
Impact: Ruído dificulta identificar dependências reais.
Recommendation: Remover imports sem uso e manter imports por responsabilidade.
Validation: Compilação e revisão dos imports alterados.

### [LOW] P3-11: Constantes duplicadas

File: `task-manager-api/utils/helpers.py:110-116`
Description: Constantes existem mas rotas repetem status/limites e números mágicos.
Impact: Regras podem divergir entre criação e atualização.
Recommendation: Uma fonte de constantes de validação.
Validation: Mesmos limites aceitos/rejeitados nos dois fluxos.

## Deprecated APIs

Projeto 3: Query.get e datetime.utcnow confirmados pela documentação oficial listada em specs/001-refactor-arch/research.md.

## Proposed Phase 3 scope

Aplicar as recomendações acima preservando métodos/paths, com testes de regressão e dados sintéticos isolados. Configuração, MVC, validação e erros centralizados. Nenhuma exclusão de banco existente nem integração externa. Mudanças de segurança e limites em reports/compatibility.md.

## Confirmation

Phase 2 complete. Proceed with the scoped refactoring (Phase 3)? Aguardar confirmação explícita do relatório concreto antes de modificar fontes. Ver reports/approval.md para decisão e hashes.
