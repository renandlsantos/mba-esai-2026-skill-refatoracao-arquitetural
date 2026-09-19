# Architecture Audit Report: ecommerce-api-legacy

Baseline: `6d1ce6248c3e956801010a89d8bdaab48029bf30`
Stack observada: JavaScript / Express 4.22.1 / sqlite3 5.1.7.
Domínio: LMS com cursos, checkout, matrículas e pagamentos.
Arquitetura atual: God Class coordena persistência, HTTP, checkout, relatórios e configuração.
Arquivos fonte: 3; linhas: 180. Dependências instaladas registradas no baseline; arquivos de skill/testes/dependências excluídos da contagem.

## Summary

CRITICAL: 2 | HIGH: 3 | MEDIUM: 2 | LOW: 2

## Findings

### [CRITICAL] P2-01: God Class

File: `ecommerce-api-legacy/src/AppManager.js:4-138`
Description: A classe cria banco, seed, rotas, checkout e relatório.
Impact: Mudanças em qualquer domínio afetam todos; difícil isolar falhas.
Recommendation: Separar composition root, repositório, controllers, rotas e serviços.
Validation: Testar checkout com dependência de pagamento substituída.

### [CRITICAL] P2-02: Dados sensíveis em logs e configuração

File: `ecommerce-api-legacy/src/AppManager.js:43-46`
Description: Log inclui cartão inteiro e chave de pagamento; src/utils.js:1-6 contém credenciais.
Impact: Logs expõem informações financeiras e segredos.
Recommendation: Configuração por ambiente e logs sem cartão/chaves.
Validation: Captura de logs não contém cartão, senha ou token.

### [HIGH] P2-03: Senha com hash inadequado

File: `ecommerce-api-legacy/src/utils.js:17-22`
Description: Repetição de base64 truncado não fornece hash de senha seguro.
Impact: Senha é recuperável/previsível e função desperdiça CPU.
Recommendation: scrypt com salt aleatório e comparação adequada.
Validation: Mesmo password gera hashes distintos e verificação funciona.

### [HIGH] P2-04: Checkout sem transação

File: `ecommerce-api-legacy/src/AppManager.js:50-61`
Description: Matrícula, pagamento e auditoria têm commits independentes; erro de auditoria é ignorado.
Impact: Falha pode deixar matrícula sem pagamento ou afirmar sucesso indevido.
Recommendation: Unidade transacional com rollback e tratamento explícito de erro.
Validation: Injetar falha entre inserts não deixa registros parciais.

### [HIGH] P2-05: Rotas administrativas sem guarda

File: `ecommerce-api-legacy/src/AppManager.js:80-135`
Description: Relatório financeiro e remoção de usuário não autenticam autorização.
Impact: Dados financeiros e exclusão expostos.
Recommendation: Exigir token administrativo configurado e não registrado em logs.
Validation: 403 sem token; fluxo autorizado mantém resposta.

### [MEDIUM] P2-06: Relatório N+1 e erro ignorado

File: `ecommerce-api-legacy/src/AppManager.js:83-128`
Description: Loops consultam matrículas, usuários e pagamentos; callback acessa enrollments.length sem tratar err.
Impact: Custo cresce e falha de banco pode causar exceção.
Recommendation: JOIN/agrupamento com propagação de erros.
Validation: Relatório completo com número limitado de queries e falha controlada.

### [MEDIUM] P2-07: Validação e integridade referencial

File: `ecommerce-api-legacy/src/AppManager.js:28-35`
Description: Tipos de usr/eml/pwd/card não são validados; DELETE linhas 131-135 ignora erro e órfãos.
Impact: Inputs causam exceções e exclusão deixa relacionamentos inconsistentes.
Recommendation: Validador de tipos e transação para limpeza dependente.
Validation: 400 para cartão não textual; exclusão não deixa órfãos.

### [LOW] P2-08: Nomes opacos no checkout

File: `ecommerce-api-legacy/src/AppManager.js:29-34`
Description: Variáveis u/e/p/cid/cc escondem significado.
Impact: Aumenta o custo de revisão de um fluxo sensível.
Recommendation: Manter campos HTTP compatíveis e traduzir para nomes de domínio claros.
Validation: Contrato usr/eml/pwd/c_id/card preservado.

### [LOW] P2-09: Estado e import sem uso

File: `ecommerce-api-legacy/src/utils.js:9-10`
Description: globalCache cresce sem limite e totalRevenue não participa de cálculo; import em AppManager.js:2.
Impact: Código morto confunde a origem do faturamento; cache sem finalidade definida.
Recommendation: Remover estado sem uso; relatório deriva do banco.
Validation: Relatório usa dados persistidos e teste não depende de global.

## Deprecated APIs

Nenhuma API deprecated confirmada neste projeto na inspeção. Estilo antigo, callbacks e biblioteca com versão antiga não são por si prova de depreciação.

## Proposed Phase 3 scope

Aplicar as recomendações acima preservando métodos/paths, com testes de regressão e dados sintéticos isolados. Configuração, MVC, validação e erros centralizados. Nenhuma exclusão de banco existente nem integração externa. Mudanças de segurança e limites em reports/compatibility.md.

## Confirmation

Phase 2 complete. Proceed with the scoped refactoring (Phase 3)? Aguardar confirmação explícita do relatório concreto antes de modificar fontes. Ver reports/approval.md para decisão e hashes.
