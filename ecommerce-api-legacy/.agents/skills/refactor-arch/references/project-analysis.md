# Project analysis

Read manifests and locked versions (pyproject/requirements, package.json/lock, pom, go.mod, Gemfile, etc.), then confirm imports and entry points. Detect Flask/FastAPI/Django, Express/Nest or equivalents from actual construction and routing. Do not infer language solely from README. Record exact installed versions separately from declared constraints.

Locate persistence: SQL drivers, ORM models, migrations, connection URLs and transaction ownership. Redact secrets. Map inbound route to controller/use case, model/repository, serializer and side effects. Search calls, not just filenames: a services folder can still contain a God Class.

Inventory first-party source files and logical routes/methods, excluding vendored/generated files, virtualenvs, tests and skill folders unless separately counted. Give both counts and rules. Record SHA/revision for stable line evidence. Inspect caller/callee context before judging a suspicious line.

List domain entities and relationships from schemas and route payloads. Note boot-time migrations/seeding, mutable global state, background work, network calls and unhandled async paths. Read existing tests and characterize a minimal full workflow. Isolate baseline with a disposable copy or worktree and temporary database; preserve existing data and use only synthetic identities. Never run a destructive seed against an existing database.

Print: project root and revision; language/runtime/framework/dependencies with evidence; persistence; domain; architecture map; source count and lines; route inventory; executed baseline commands and results; blockers/uncertainties. Analysis does not authorize changes.
