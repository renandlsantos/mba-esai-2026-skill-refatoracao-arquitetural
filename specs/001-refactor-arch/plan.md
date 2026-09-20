# Implementation Plan: Refactor Arch

**Branch**: `feature/sdd-fase-295` | **Date**: 2026-09-19 | **Spec**: [spec.md](spec.md)

## Summary
Build and evaluate a portable Codex skill, audit the supplied baseline, obtain confirmation for concrete findings, then refactor three local backend fixtures with contract and regression evidence. Preserve domain routes and existing storage; document intentional safe rejection behavior.

## Technical Context

**Language/Version**: Python 3.12+; CommonJS JavaScript on Node (installed runtime recorded in logs).
**Primary Dependencies**: project 1 Flask 3.1.1/flask-cors 5.0.1; project 2 Express 4/sqlite3 5; project 3 Flask 3.0.0/Flask-SQLAlchemy 3.1.1. Preserve pinned frameworks unless installation proves incompatible.
**Storage**: SQLite per app, temporary isolated databases in tests; no production data.
**Testing**: Python unittest and Flask test clients; Node built-in test runner and real HTTP; Python HTTP smoke harness for all boot checks.
**Target Platform**: local macOS/Linux, loopback-only processes.
**Project Type**: three REST services and an agent skill.
**Performance Goals**: remove per-item SQL lookups from list/report paths; query-count tests bounded independently of fixture size. No unsupported throughput claim.
**Constraints**: no private course material, no global package changes, no external email/payment calls; synthetic payment simulator remains explicit.
**Scale/Scope**: four source files in project 1, three in project 2, fifteen Python files in project 3 (including package initializers and seed; audited inventory is authoritative).

## Constitution Check

Before research and after design: all five principles pass. Evidence/approval precedes source edits; route matrix defines compatibility; data is temporary for validation; layer responsibilities are explicit; identical skill copies contain generic detection and examples. No governance exception. Approval still pending when this plan was written.

## Project Structure

### Documentation (this feature)

`specs/001-refactor-arch/`: spec.md, plan.md, research.md, data-model.md, contracts/endpoints.md, quickstart.md, tasks.md, checklists/requirements.md.
`reports/`: manual baseline inventory, three audit reports, approval record, baseline/after validation logs, skill evaluation results and convergence record.

### Source Code (repository root)

- `code-smells-project/`: app.py composition root; config.py; database.py request-scoped connections; models/ product/user/order repositories; controllers/ use cases and validation; views/ routes and serializers; errors.py.
- `ecommerce-api-legacy/src/`: app.js composition root; config.js; models/database.js and repository.js; controllers/checkout.js and administration.js; views/routes.js; errors.js; services/password.js and payment.js.
- `task-manager-api/`: app.py factory; config.py; database.py; retain models/, add repositories/, controllers/ and views/; routes/ become thin adapters; central validation/errors and safe optional notifications.
- Each app: `.agents/skills/refactor-arch/` with identical SKILL.md, five references and evals/evals.json.
- `tests/`, `scripts/`: reproducible validation and portable skill/audit consistency checks. Temporary environments, SQLite files and baseline copies live in ignored `.work/`.

**Structure Decision**: Adapt to existing Flask/SQLAlchemy structure rather than adding a shared cross-language framework. Explicit dependency injection for repositories and payment service; no global mutable cache. Query parameterization, safe serializers, transaction boundaries, typed validation and deprecated API replacement address observed defects.

## Complexity Tracking

No constitution violations. Preserve existing relational schemas where possible. No production authentication platform or new UI is introduced. Dangerous admin utilities are disabled by default and require configured admin token; SQL console is constrained to read-only statements and cannot expose password columns. The local examples remain educational and are not claimed production-ready.
