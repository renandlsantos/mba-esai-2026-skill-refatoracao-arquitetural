# Resolução dos 30 achados

Escopo: achados da auditoria aprovada. IDs e linhas do baseline não foram reescritos. Cada correção foi revista e os cenários abaixo foram executados. Limitações globais em compatibility.md.

| ID | Estado | Evidência |
|---|---|---|
| P1-01 | Resolvido no escopo aprovado | models/users.py e models/products.py; test_passwords_and_sql_injection |
| P1-02 | Resolvido no escopo aprovado | models/users.py / controllers/admin.py; test_passwords_and_sql_injection |
| P1-03 | Resolvido no escopo aprovado | controllers/admin.py; test_admin_guards_errors_and_bounded_queries |
| P1-04 | Resolvido no escopo aprovado | database.py; test_discount_boundaries_and_explicit_legacy_migration (instância isolada) |
| P1-05 | Resolvido no escopo aprovado | models/orders.py; test_invalid_inputs_and_atomic_order |
| P1-06 | Resolvido no escopo aprovado | models/orders.py; teste de limite de duas SELECTs |
| P1-07 | Resolvido no escopo aprovado | controllers/validation.py; test_invalid_inputs_and_atomic_order |
| P1-08 | Resolvido no escopo aprovado | errors.py; testes de 400/404/405/500 e rollback |
| P1-09 | Resolvido no escopo aprovado | DISCOUNT_TIERS; test_discount_boundaries_and_explicit_legacy_migration |
| P1-10 | Resolvido no escopo aprovado | modelos por domínio e Ruff F sem erros |
| P2-01 | Resolvido no escopo aprovado | src/models/,controllers/,views/,services/; createApp aceita payment injetável |
| P2-02 | Resolvido no escopo aprovado | config.js e payment.js; invalid input and secrets never enter logs |
| P2-03 | Resolvido no escopo aprovado | services/password.js; password hashes use independent salts |
| P2-04 | Resolvido no escopo aprovado | repository.js fila/transação; failed payment insert e concurrent checkouts |
| P2-05 | Resolvido no escopo aprovado | administration.js; all routes/admin guard tests |
| P2-06 | Resolvido no escopo aprovado | repository.financialReport; uma consulta com oito matrículas |
| P2-07 | Resolvido no escopo aprovado | checkout validation e deleteUser transacional; invalid input e dependent cleanup |
| P2-08 | Resolvido no escopo aprovado | controllers/checkout.js traduz nomes HTTP para nomes de domínio; contrato preservado |
| P2-09 | Resolvido no escopo aprovado | utils.js removido, nenhum globalCache/totalRevenue; relatório calculado do banco |
| P3-01 | Resolvido no escopo aprovado | models/user.py + views/serializers.py; credentials_tokens_and_duplicate_email |
| P3-02 | Resolvido no escopo aprovado | config.py + notification_service.py; disabled_notifications com mock SMTP |
| P3-03 | Resolvido no escopo aprovado | services/tokens.py; adulteração e expiração rejeitadas; limite de auth geral documentado |
| P3-04 | Resolvido no escopo aprovado | controllers/ + repositories/ + views/; all_routes e atomic_update |
| P3-05 | Resolvido no escopo aprovado | seed.py; seed_guard e seed sintético vazio |
| P3-06 | Resolvido no escopo aprovado | Store eager/batch; n_plus_one (1/2/3 queries) |
| P3-07 | Resolvido no escopo aprovado | controllers/validation.py; validation_and_atomic_update |
| P3-08 | Resolvido no escopo aprovado | Store usa Session.get/select; LegacyAPIWarning tratado como erro |
| P3-09 | Resolvido no escopo aprovado | utils/clock.py; DeprecationWarning tratado como erro |
| P3-10 | Resolvido no escopo aprovado | Ruff F sem erros; imports explícitos |
| P3-11 | Resolvido no escopo aprovado | utils/constants.py e validators compartilhados; criação/atualização testadas |
