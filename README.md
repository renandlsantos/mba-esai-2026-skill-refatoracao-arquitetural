# Refactor Arch: auditoria e refatoração MVC

Fase 295 do MBA. Fluxo documentado em [specs/001-refactor-arch](specs/001-refactor-arch/spec.md).

## Análise Manual

Baseline auditado: `6d1ce6248c3e956801010a89d8bdaab48029bf30`. As linhas apontam para essa revisão, não para o código refatorado. Fontes lidas integralmente; nenhuma transcrição privada foi incluída.

### Projeto 1: code-smells-project

Python / Flask 3.1.1 / SQLite. Monólito em quatro arquivos; SQL, validação, representação e efeitos colaterais misturados.

- **CRITICAL P1-01**: SQL concatenado, `code-smells-project/models.py:105-111`. Autenticação pode ser contornada.
- **CRITICAL P1-02**: Credenciais expostas, `code-smells-project/models.py:72-86`. Credenciais e configuração interna vazam pela API.
- **CRITICAL P1-03**: Administração irrestrita, `code-smells-project/app.py:47-78`. Qualquer cliente altera ou extrai o banco.
- **HIGH P1-04**: Conexão global mutável, `code-smells-project/database.py:4-11`. Requisições podem compartilhar transação e estado.
- **HIGH P1-05**: Pedido sem invariantes atômicas, `code-smells-project/models.py:133-169`. Pedidos podem reduzir estoque abaixo de zero ou persistir parcialmente.
- **MEDIUM P1-06**: Consultas N+1, `code-smells-project/models.py:171-232`. Número de consultas cresce com itens e pedidos.
- **MEDIUM P1-07**: Validação de tipos ausente, `code-smells-project/controllers.py:24-62`. Inputs inválidos geram 500 e regras inconsistentes.
- **MEDIUM P1-08**: Erros duplicados e detalhes internos, `code-smells-project/controllers.py:5-22`. Respostas inconsistentes e informações internas.
- **LOW P1-09**: Política de descontos sem nomes, `code-smells-project/models.py:256-262`. Mudanças comerciais são difíceis de localizar e revisar.
- **LOW P1-10**: Identificadores genéricos e import morto, `code-smells-project/models.py:1-3`. Leitura e rastreio de responsabilidades ficam menos claros.

### Projeto 2: ecommerce-api-legacy

JavaScript / Express 4.22.1 / sqlite3 5.1.7. God Class coordena persistência, HTTP, checkout, relatórios e configuração.

- **CRITICAL P2-01**: God Class, `ecommerce-api-legacy/src/AppManager.js:4-138`. Mudanças em qualquer domínio afetam todos; difícil isolar falhas.
- **CRITICAL P2-02**: Dados sensíveis em logs e configuração, `ecommerce-api-legacy/src/AppManager.js:43-46`. Logs expõem informações financeiras e segredos.
- **HIGH P2-03**: Senha com hash inadequado, `ecommerce-api-legacy/src/utils.js:17-22`. Senha é recuperável/previsível e função desperdiça CPU.
- **HIGH P2-04**: Checkout sem transação, `ecommerce-api-legacy/src/AppManager.js:50-61`. Falha pode deixar matrícula sem pagamento ou afirmar sucesso indevido.
- **HIGH P2-05**: Rotas administrativas sem guarda, `ecommerce-api-legacy/src/AppManager.js:80-135`. Dados financeiros e exclusão expostos.
- **MEDIUM P2-06**: Relatório N+1 e erro ignorado, `ecommerce-api-legacy/src/AppManager.js:83-128`. Custo cresce e falha de banco pode causar exceção.
- **MEDIUM P2-07**: Validação e integridade referencial, `ecommerce-api-legacy/src/AppManager.js:28-35`. Inputs causam exceções e exclusão deixa relacionamentos inconsistentes.
- **LOW P2-08**: Nomes opacos no checkout, `ecommerce-api-legacy/src/AppManager.js:29-34`. Aumenta o custo de revisão de um fluxo sensível.
- **LOW P2-09**: Estado e import sem uso, `ecommerce-api-legacy/src/utils.js:9-10`. Código morto confunde a origem do faturamento; cache sem finalidade definida.

### Projeto 3: task-manager-api

Python / Flask 3.0.0 / Flask-SQLAlchemy 3.1.1 / SQLAlchemy 2.0.54 / SQLite. Camadas nominais existentes; rotas concentram regras, SQL e apresentação.

- **CRITICAL P3-01**: Hash de senha exposto e fraco, `task-manager-api/models/user.py:16-32`. Dicionários offline e vazamento de credenciais.
- **CRITICAL P3-02**: Credenciais hardcoded, `task-manager-api/services/notification_service.py:7-10`. Segredos versionados e risco de envio inadvertido.
- **HIGH P3-03**: Falso token de autenticação, `task-manager-api/routes/user_routes.py:197-211`. Consumidor pode interpretar identificador forjável como credencial.
- **HIGH P3-04**: Rotas acumulam responsabilidades, `task-manager-api/routes/task_routes.py:85-223`. Duplicação e acoplamento impedem testes isolados.
- **HIGH P3-05**: Seed destrutivo por padrão, `task-manager-api/seed.py:8-14`. Apaga dados existentes sem revisão.
- **MEDIUM P3-06**: N+1 em listagens, `task-manager-api/routes/task_routes.py:14-59`. Custo cresce com tamanho das listas.
- **MEDIUM P3-07**: Tipos e datas inconsistentes, `task-manager-api/routes/task_routes.py:110-144`. Corpos inválidos causam 500; PUT diverge de POST.
- **MEDIUM P3-08**: API de consulta legada, `task-manager-api/routes/task_routes.py:65-67`. Avisos e custo de evolução; não significa método removido.
- **MEDIUM P3-09**: UTC obsoleto no runtime alvo, `task-manager-api/models/task.py:15-17`. Timestamp sem timezone e avisos na evolução do runtime.
- **LOW P3-10**: Imports sem uso, `task-manager-api/app.py:7-7`. Ruído dificulta identificar dependências reais.
- **LOW P3-11**: Constantes duplicadas, `task-manager-api/utils/helpers.py:110-116`. Regras podem divergir entre criação e atualização.


## Construção da Skill

A skill `refactor-arch` usa Codex e fica em `.agents/skills/refactor-arch/` dentro de cada aplicação. As três cópias são idênticas. Seu `SKILL.md` coordena três fases: análise; auditoria com confirmação explícita; refatoração e validação. Cinco referências Markdown fornecem heurísticas, catálogo, template, MVC e playbook. Há 13 antipadrões e 13 transformações com antes/depois, incluindo APIs deprecated. As regras são independentes de linguagem; exemplos Python e JavaScript explicam mecanismos, sem paths de fixtures na lógica da skill.

A construção seguiu a skill oficial `skill-creator`: intenção, rascunho, três prompts reais, execução/evidências, grading e visualizador oficial. A avaliação foi sequencial pelo mesmo agente, pois a tarefa vedava novos agentes. Não há comparação cega, baseline de modelo ou alegação de taxa de acerto universal. [Avaliações](reports/skill-evals/iteration-1/assessment.md) e [visualizador](reports/skill-evals/review.html) permitem revisar as saídas e 15 critérios com evidências.

O workflow SDD seguiu Spec Kit 1.0.8: constitution, specify, plan, tasks, implement e converge. [Especificação](specs/001-refactor-arch/spec.md), [plano](specs/001-refactor-arch/plan.md), [tarefas](specs/001-refactor-arch/tasks.md) e [aprovação concreta](reports/approval.md) preservam decisões. A confirmação foi do coordenador autorizado, não uma nova mensagem humana. A skill em uso continua pedindo confirmação para cada auditoria concreta.

Desafios: o Express iniciava listener ao importar o módulo; a factory remove esse efeito. O SQLite nativo exigiu instalar seu binding após inspeção do install script; bun é o gerenciador escolhido. O Task Manager tinha pastas de camadas, mas regras/consultas permaneciam nas rotas; preservar os models e extrair responsabilidades foi menor que reescrever a stack. As aplicações usam SQLite existente; migração de senhas legadas é opt-in e documentada, nunca uma gravação silenciosa em dados existentes.

## Resultados

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Rotas preservadas/testadas | Testes de regressão |
|---|---:|---:|---:|---:|---:|---:|
| E-commerce Flask | 3 | 2 | 3 | 2 | 19/19 | 5 |
| LMS Express | 2 | 3 | 2 | 2 | 3/3 | 5 |
| Task Manager Flask | 2 | 3 | 4 | 2 | 22/22 | 5 |

Relatórios de Fase 2: [projeto 1](reports/audit-project-1.md), [projeto 2](reports/audit-project-2.md), [projeto 3](reports/audit-project-3.md). As linhas desses relatórios referem-se ao commit original. [Resolução dos achados](reports/resolution.md) liga cada correção a testes. O baseline reproduzível demonstrou SQL injection no login e vazamento de senhas/chave, dados de pagamento em logs e falso token. Nenhum valor sensível foi incluído nos logs publicados.

Antes/depois:

| Projeto | Antes | Depois |
|---|---|---|
| Shop | app + controllers.py + models.py + database global | app factory; config/errors; models por domínio; controller de uso/validação; views/routes; conexão por contexto |
| LMS | AppManager com SQL, HTTP, checkout e relatórios | app factory; models/repository; controllers; views/routes; password/payment services; config/errors |
| Tasks | models/routes/services/utils, com regras e SQL nas rotas | models preservados; repository; controllers por domínio; serializers; rotas finas; config/errors/clock; seed não destrutivo |

Checklist por projeto:

| Critério | Shop | LMS | Tasks |
|---|---|---|---|
| Stack/domínio/fontes detectados e evidenciados | OK | OK | OK |
| Pelo menos 5 findings, arquivo/linha/severidade | OK | OK | OK |
| Pelo menos 1 CRITICAL/HIGH, 2 MEDIUM, 2 LOW | OK | OK | OK |
| Confirmação concreta antes de editar fontes | OK | OK | OK |
| Models, views/routes, controllers e entry point | OK | OK | OK |
| Configuração e erros centralizados, sem segredos fixos | OK | OK | OK |
| Boot real local e rotas originais funcionais | OK | OK | OK |
| Regressões/integridade/serialização/N+1 | OK | OK | OK |
| Deprecated APIs | nenhuma confirmada | nenhuma confirmada | Query.get/utcnow substituídos |

[Resultado estruturado](reports/after-validation.json) registra comandos, saídas, 44 rotas e três boots reais; logs: [Shop](reports/tests-shop.txt), [LMS](reports/tests-lms.txt), [Tasks](reports/tests-tasks.txt). Os testes usam bases temporárias e identidades sintéticas. A cobertura é de métodos/paths e cenários explícitos, não uma alegação de cobertura total de branches ou segurança de produção.

## Como Executar

Pré-requisitos: Python 3.12+, uv, Node (validado em 26.9.0), bun (validado em 1.2.22) e Codex configurado para usar skills. Não é necessária chave de LLM para executar as aplicações/testes; a interação com a skill usa sua sessão Codex. Pacotes Python ficam em dois ambientes isolados e versões resolvidas estão nos requirements-lock.txt.

Na raiz:

```bash
bash scripts/setup.sh
python3 scripts/validate.py
python3 scripts/reproduce_baseline.py
```

O primeiro comando instala dependências nos ambientes locais. O segundo executa 15 testes, compara inventários de 44 rotas, faz boot em portas efêmeras loopback e confere cópias da skill. O terceiro exporta o commit original para área descartável e reproduz apenas o baseline, sem substituir o código atual. Nunca execute o app legado diretamente: ele contém falhas intencionais.

Para usar a skill, entre em cada diretório e inicie Codex:

```bash
cd code-smells-project
codex
# Na conversa: $refactor-arch analise e audite este projeto; aguarde minha confirmação.
```

Repita em `ecommerce-api-legacy/` e `task-manager-api/`. Revise a Fase 1 e o relatório da Fase 2; somente depois responda explicitamente autorizando a Fase 3. Para avaliar novamente as falhas originais, use uma cópia isolada do commit baseline; no código já refatorado não se deve fabricar cinco problemas só para cumprir uma contagem.

Boot manual, a partir da raiz, em terminais separados:

```bash
PORT=5101 .work/venv-shop/bin/python code-smells-project/app.py
PORT=5102 .work/venv-tasks/bin/python task-manager-api/app.py
PORT=5103 node ecommerce-api-legacy/src/app.js
```

As três escutam apenas `127.0.0.1`; interrompa com Ctrl-C. Shop e Tasks criam somente tabelas ausentes, sem seed automático. LMS usa memória por padrão; para o catálogo sintético habilite `SEED_DEMO=true` somente em banco vazio. Para persistência configure `DATABASE_PATH` no Shop/LMS e `DATABASE_URL` no Tasks. `SECRET_KEY` do Tasks deve vir do ambiente se tokens precisarem sobreviver ao restart. Sem ela, a chave é aleatória por instância.

Administração Shop/LMS exige `ADMIN_TOKEN` configurado e header `Authorization: Bearer <valor>`; não versione esse valor. Reset do Shop também exige `ALLOW_RESET=true` e deve ser usado apenas em base descartável. `/admin/query` aceita somente três consultas públicas predefinidas, descritas em [compatibilidade](reports/compatibility.md).

Para seed Task Manager, configure um `DATABASE_URL` apontando a base sintética vazia e `SEED_PASSWORD`, então execute `.work/venv-tasks/bin/python task-manager-api/seed.py --demo`. Banco com qualquer registro é recusado e preservado. SMTP fica desligado por padrão; não é chamado pelas rotas nem pelos testes.

Limites: não há serviço real de pagamento, envio de e-mail ou plataforma completa de autenticação/autorização. O token assinado do Task Manager demonstra integridade/expiração; suas rotas de demonstração continuam sem autenticação geral. Não publique essas APIs na internet. O risco das versões de dependência não foi atestado pelo Endor porque o conector não estava disponível ([registro](reports/dependency-review.json)); isso não é aprovação nem diagnóstico de vulnerabilidade. Não foi realizada submissão na plataforma do curso.
