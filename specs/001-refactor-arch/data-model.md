# Data model and invariants

The audit representation has Finding(id, severity, path, startLine, endLine, revision, description, impact, recommendation, validation). Severity is CRITICAL/HIGH/MEDIUM/LOW. Approval binds report hashes, project paths and scope to a reviewer response.

Project 1 preserves produtos, usuarios, pedidos and itens_pedido. Product name is a string of 2..200 characters; price is finite and nonnegative; stock is a nonnegative integer. Order items have positive integer quantities and existing products/users; duplicate products are combined before stock checks. Order creation is one transaction. Status is pendente/aprovado/enviado/entregue/cancelado. User passwords are hashed and never serialized. Existing data is not reseeded.

Project 2 preserves users, courses, enrollments, payments and audit_logs. Checkout requires nonempty usr/eml/pwd/card and positive integer c_id; card is handled only by the local payment simulator, never logged or persisted. Paid checkout inserts enrollment, payment and audit record atomically. User deletion must not orphan dependent data. User pass holds salted hashes; duplicate emails are handled deterministically.

Project 3 preserves users, tasks and categories. Title is 3..200 characters; priority is integer 1..5; status is pending/in_progress/done/cancelled. User role is user/admin/manager; password minimum is 4 characters to preserve the fixture's explicit contract. Due dates use YYYY-MM-DD; tags are a list of strings or comma-separated text; foreign IDs must reference existing records or be null. Colors are six hexadecimal digits prefixed by #. Unknown resources return 404; conflicts return 409. Safe serializers omit credentials. Updates validate all fields before mutation; delete behavior is explicit and tested.
