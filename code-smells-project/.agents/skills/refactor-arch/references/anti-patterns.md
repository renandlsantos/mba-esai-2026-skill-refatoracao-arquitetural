# Anti-pattern catalog

Severity reflects observed impact and reachability. CRITICAL: direct serious exposure or architecture combining incompatible responsibilities in one component. HIGH: major MVC/SOLID/testability or integrity defect. MEDIUM: validation, duplication or moderate performance issue. LOW: local naming/readability/constant issue. Escalate/downgrade only with stated rationale.

| ID | Pattern / default severity | Detection and verification | Remedy / regression |
|---|---|---|---|
| AP01 | SQL injection / CRITICAL | User-controlled text concatenated into executable SQL; trace source to sink. An integer-only route may limit exploitability. | Bound parameters; malicious text remains data. |
| AP02 | Credential exposure / CRITICAL | Hardcoded credential values, passwords/hashes in serializers, secrets/cards in reachable logs. Redact values in report. | Environment/secret provider, allowlisted public fields, log redaction. |
| AP03 | God component / CRITICAL or HIGH | Same component owns routing, persistence, business decisions and effects; describe concrete coupling rather than line-count threshold alone. | MVC/use-case boundaries and injected collaborators. |
| AP04 | Unsafe global state / HIGH | Mutable caches/connections shared across requests, transaction ownership unclear. | Request/app scope, explicit lifecycle and isolated-state tests. |
| AP05 | Non-atomic workflow / HIGH | Multi-write operation can partly commit, missing rollback, callback ignores failure. | Transaction boundary around whole use case, failure-injection test. |
| AP06 | Weak password handling / HIGH | Plaintext, reversible encoding, fast unsalted hash or default passwords. | Supported salted password KDF and explicit legacy migration. |
| AP07 | N+1 / MEDIUM | SQL/ORM queries inside result loops or lazy relation serialization; measure with multiple records. | Join/eager loading/batch fetch; bounded query-count test. |
| AP08 | Inconsistent validation / MEDIUM | Missing type/range/finite checks; POST/PUT drift; mutations before all checks. | Shared validation before write and invalid-input regressions. |
| AP09 | Leaky/inconsistent errors / MEDIUM | Raw exception sent to client, bare except swallowing state, async error ignored. | Central error mapping, rollback and sanitized logs. |
| AP10 | Deprecated APIs / MEDIUM | Confirm symbol, package/runtime version and official deprecation notice; distinguish legacy from removed. | Supported equivalent with semantic/compatibility tests. |
| AP11 | Magic constants / LOW | Domain threshold/rate/limit duplicated or unnamed. | Named policy values and boundary tests; avoid configuring every literal. |
| AP12 | Unclear names/dead code / LOW | Abbreviations hide domain meaning; unused imports/variables verified by references. | Meaningful names and deletion of confirmed dead code. |
| AP13 | Unprotected destructive/admin operation / CRITICAL or HIGH | Caller can execute arbitrary SQL/reset data or access restricted operation without a guard. | Explicit authorization, restricted capability, deny-by-default test. |

For every finding cite exact file and line range at the captured revision. Document checks with no confirmed issue. Do not treat callback style, ORM presence or a small file as proof of architecture quality. SQLAlchemy Query.get is legacy in 2.x (use Session.get); Python datetime.utcnow is deprecated from 3.12 (use timezone-aware now, with explicit storage conversion if required). Verify these against the installed version and official docs before reporting in another project.
