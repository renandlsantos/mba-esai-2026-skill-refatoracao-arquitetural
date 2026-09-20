# Architecture Audit Report: code-smells-project

Baseline: `6d1ce6248c3e956801010a89d8bdaab48029bf30`
Stack observada: Python / Flask 3.1.1 / SQLite.
Domínio: E-commerce de produtos, usuários e pedidos.
Arquitetura atual: Monólito em quatro arquivos; SQL, validação, representação e efeitos colaterais misturados.
Arquivos fonte: 4; linhas: 780. Dependências instaladas registradas no baseline; arquivos de skill/testes/dependências excluídos da contagem.

## Summary

CRITICAL: 3 | HIGH: 2 | MEDIUM: 3 | LOW: 2

## Findings

### [CRITICAL] P1-01: SQL concatenado

File: `code-smells-project/models.py:105-111`
Description: Login concatena email e senha em SQL; baseline aceitou expressão de bypass com status 200.
Impact: Autenticação pode ser contornada.
Recommendation: Parametrizar consultas e verificar hash fora do SQL.
Validation: SQL injection não autentica e strings com aspas persistem como dados.

### [CRITICAL] P1-02: Credenciais expostas

File: `code-smells-project/models.py:72-86`
Description: Listagem serializa senha; controllers.py:264-289 inclui secret_key na saúde.
Impact: Credenciais e configuração interna vazam pela API.
Recommendation: Hashes de senha e serializers com lista explícita de campos públicos.
Validation: Nenhuma resposta contém senha/hash/secret_key.

### [CRITICAL] P1-03: Administração irrestrita

File: `code-smells-project/app.py:47-78`
Description: Rotas permitem apagar tabelas e executar SQL fornecido sem autenticação.
Impact: Qualquer cliente altera ou extrai o banco.
Recommendation: Token administrativo configurado, reset explicitamente habilitado e console limitado a consultas públicas somente leitura.
Validation: Sem token retorna 403 e SQL fora do subconjunto permitido é rejeitado.

### [HIGH] P1-04: Conexão global mutável

File: `code-smells-project/database.py:4-11`
Description: Uma conexão SQLite é compartilhada com check_same_thread=False.
Impact: Requisições podem compartilhar transação e estado.
Recommendation: Conexões por contexto e fechamento no teardown.
Validation: Duas instâncias isoladas não compartilham dados; rollback por request.

### [HIGH] P1-05: Pedido sem invariantes atômicas

File: `code-smells-project/models.py:133-169`
Description: Estoque é verificado por item antes da baixa; produtos repetidos não são agregados e usuário não é validado.
Impact: Pedidos podem reduzir estoque abaixo de zero ou persistir parcialmente.
Recommendation: Validar/combinar itens e executar verificação/baixa/inserção em transação.
Validation: Repetição e falha intermediária preservam estoque e total de pedidos.

### [MEDIUM] P1-06: Consultas N+1

File: `code-smells-project/models.py:171-232`
Description: Cada pedido consulta itens, e cada item consulta nome do produto.
Impact: Número de consultas cresce com itens e pedidos.
Recommendation: Buscar pedidos e itens em lotes com JOIN.
Validation: Consulta de lista mantém contagem limitada com mais itens.

### [MEDIUM] P1-07: Validação de tipos ausente

File: `code-smells-project/controllers.py:24-62`
Description: Preço e estoque são comparados antes de verificar o tipo; atualização diverge da criação.
Impact: Inputs inválidos geram 500 e regras inconsistentes.
Recommendation: Validação compartilhada de objeto, tipos, limites, categorias e números finitos.
Validation: Tipos errados, NaN e quantidades inválidas retornam 400 sem gravação.

### [MEDIUM] P1-08: Erros duplicados e detalhes internos

File: `code-smells-project/controllers.py:5-22`
Description: Handlers repetem try/except e devolvem str(e).
Impact: Respostas inconsistentes e informações internas.
Recommendation: Erros de domínio e handler central com resposta sanitizada.
Validation: JSON malformado e falhas de persistência recebem formato estável.

### [LOW] P1-09: Política de descontos sem nomes

File: `code-smells-project/models.py:256-262`
Description: Limiares e percentuais de desconto aparecem como números literais.
Impact: Mudanças comerciais são difíceis de localizar e revisar.
Recommendation: Constantes nomeadas e função de domínio testada nos limites.
Validation: Testes dos limiares preservam cálculo.

### [LOW] P1-10: Identificadores genéricos e import morto

File: `code-smells-project/models.py:1-3`
Description: sqlite3 é importado sem uso; funções usam id para diferentes domínios, por exemplo linha 24.
Impact: Leitura e rastreio de responsabilidades ficam menos claros.
Recommendation: Remover import morto e usar product_id/user_id em módulos de domínio.
Validation: Compilação e revisão estática sem import sem uso nessas áreas.

## Deprecated APIs

Nenhuma API deprecated confirmada neste projeto na inspeção. Estilo antigo, callbacks e biblioteca com versão antiga não são por si prova de depreciação.

## Proposed Phase 3 scope

Aplicar as recomendações acima preservando métodos/paths, com testes de regressão e dados sintéticos isolados. Configuração, MVC, validação e erros centralizados. Nenhuma exclusão de banco existente nem integração externa. Mudanças de segurança e limites em reports/compatibility.md.

## Confirmation

Phase 2 complete. Proceed with the scoped refactoring (Phase 3)? Aguardar confirmação explícita do relatório concreto antes de modificar fontes. Ver reports/approval.md para decisão e hashes.
