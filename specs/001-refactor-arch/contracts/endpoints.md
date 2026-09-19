# Compatibility and route contracts

The source inventory and baseline route matrix in reports/ are the authoritative list. Preserve methods and paths:

- Project 1: `/`, `/health`; GET/POST `/produtos`, GET/PUT/DELETE `/produtos/<id>`, GET `/produtos/busca`; GET/POST `/usuarios`, GET `/usuarios/<id>`, POST `/login`; GET/POST `/pedidos`, GET `/pedidos/usuario/<id>`, PUT `/pedidos/<id>/status`, GET `/relatorios/vendas`; POST `/admin/reset-db`, POST `/admin/query` with explicit admin protection and safe SQL restrictions.
- Project 2: POST `/api/checkout`, GET `/api/admin/financial-report`, DELETE `/api/users/:id`; retain successful checkout/report shapes, protect admin operations and reject invalid checkout safely.
- Project 3: `/`, `/health`; GET/POST `/tasks`, GET/PUT/DELETE `/tasks/<id>`, GET `/tasks/search`, GET `/tasks/stats`; GET/POST `/users`, GET/PUT/DELETE `/users/<id>`, GET `/users/<id>/tasks`, POST `/login`; GET `/reports/summary`, GET `/reports/user/<id>`; GET/POST `/categories`, PUT/DELETE `/categories/<id>`.

Successful list/create/read/update/delete and reports are characterized with synthetic data before edits. Password/hash fields, debug settings, internal exceptions and fake tokens are not legitimate response guarantees. Administrative methods require a configured token and return controlled denial otherwise. Unknown path and method errors are centralized JSON. Missing/non-object JSON, invalid types, nonfinite numbers and invalid references are validated before persistence. Document every intentional contract change in reports/compatibility.md.
