# Transformation playbook

Choose transformations only for evidenced, approved findings. Examples omit surrounding domain code; adapt names and versions.

## T01: Parameterize SQL (AP01)
Before (Python): `db.execute("SELECT * FROM users WHERE email='" + email + "'")`
After: `db.execute("SELECT * FROM users WHERE email = ?", (email,))`
Validate injection strings and ordinary quotes; parameters cannot represent table/column names, which need an allowlist.

## T02: Separate public representation (AP02)
Before: `return jsonify(user.__dict__)`
After: `return jsonify({"id": user.id, "name": user.name, "email": user.email})`
Test nested lists/detail/login responses, not only one endpoint.

## T03: Extract use case from route (AP03)
Before (JS): `app.post('/orders', async (req,res) => { const row=await db.insert(req.body); res.json(row); });`
After: `app.post('/orders', asyncRoute(async (req,res) => res.status(201).json(await orders.create(validateOrder(req.body)))));`
The controller receives repository and side-effect collaborators at construction; the repository owns SQL. Test controller failures and actual HTTP behavior.

## T04: Replace global connection (AP04)
Before: `connection = sqlite3.connect(path, check_same_thread=False)` at import time.
After (Flask): `if "db" not in g: g.db = sqlite3.connect(current_app.config["DATABASE"])`; teardown pops/closes it.
Test independent apps and transaction rollback. A scoped handle does not make multiple transactions on a single shared handle safe.

## T05: Atomic multi-write operation (AP05)
Before: `await insertEnrollment(); await insertPayment();`
After: `await repository.transaction(async tx => { await tx.insertEnrollment(); await tx.insertPayment(); });`
Implement transaction serialization/isolation appropriate to the driver; callback rejection must rollback. Inject failure after the first write and run concurrent requests.

## T06: Password KDF with migration (AP06)
Before: `hashlib.md5(password.encode()).hexdigest()`
After: `generate_password_hash(password, method="scrypt")`, verified with `check_password_hash(stored, candidate)`.
Node equivalent uses `crypto.scrypt` with random salt and constant-time comparison. Do not silently accept legacy formats forever; upgrade verified legacy values or provide an explicit migration/reset policy.

## T07: Batch relationship reads (AP07)
Before: `for item in items: owner = session.get(User, item.user_id)`
After: `items = session.scalars(select(Item).options(selectinload(Item.user))).all()`
Or a parameterized JOIN in direct SQL. Measure query counts with several distinct owners so the identity map does not conceal N+1.

## T08: Validate before mutation (AP08)
Before: `task.title = body["title"]; task.priority = int(body["priority"])`
After: `values = validate_task(body); apply_values(task, values)`.
Validator rejects non-object JSON, bool-as-int, wrong types, nonfinite numbers, invalid references and out-of-range values. Test failed updates leave all stored fields unchanged.

## T09: Centralize errors (AP09)
Before: `except Exception as exc: return {"error": str(exc)}, 500`
After: raise a typed domain error for expected failures; central handler maps it to safe JSON and logs internal details privately. In Express use an async wrapper forwarding rejection to `next(error)` and one final error middleware.
Preserve HTTPException status (404/405); rollback persistence before a failed request is reused.

## T10: Replace deprecated APIs (AP10)
Before: `User.query.get(user_id)`; after: `db.session.get(User, user_id)` for SQLAlchemy 2.x.
Before: `datetime.utcnow()`; after: `datetime.now(timezone.utc)` for an aware value. If the legacy schema requires UTC-naive values, convert explicitly at its boundary; do not compare aware and naive objects accidentally.
Run with applicable deprecation warnings treated as errors; cite official migration documentation.

## T11: Name a domain policy (AP11)
Before: `discount = total * 0.1 if total > 10000 else 0`
After: `discount = total * HIGH_VOLUME_DISCOUNT if total > HIGH_VOLUME_THRESHOLD else 0`
Preserve strict/inclusive boundary semantics with tests; avoid changing business rates under the guise of refactoring.

## T12: Rename and remove verified dead code (AP12)
Before: `let u = req.body.usr; let totalRevenue = 0;`
After: `const customerName = req.body.usr;` and remove the unused global only after reference search.
Keep external field names when part of the compatibility contract.

## T13: Restrict privileged capability (AP13)
Before: `app.post('/admin/reset', resetAll)`
After: `app.post('/admin/reset', requireConfiguredAdmin, requireResetEnabled, resetAll)`.
Default to denied when configuration is absent. Do not trust a client-supplied role. For SQL consoles, prefer predefined read operations rather than general execution. Test denial and limited authorized success using a temporary database.
