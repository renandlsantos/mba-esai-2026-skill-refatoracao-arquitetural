# Tasks: Refactor Arch

Input: reviewed spec.md, plan.md, research.md, data-model.md and contracts/. Tests are required by FR-009.

## Phase 1: Setup

- [X] T001 Record baseline revision, source counts, line counts and hashes in reports/baseline-inventory.json (FR-003, FR-012).
- [X] T002 Configure ignored isolated environments in .gitignore and scripts/validate.py without modifying system packages (Constitution IV).

## Phase 2: Foundational

- [X] T003 Capture all original routes and baseline boot/workflow behavior in reports/baseline-validation.json and tests/baseline.py (FR-009).

## Phase 3: User Story 1 - Review an evidenced audit

Goal: auditable diagnosis with unchanged application sources. Independent test: line references resolve at baseline and source hashes remain identical before confirmation.

- [X] T004 [US1] Document manual findings in README.md and reports/audit-project-{1,2,3}.md, at least one CRITICAL/HIGH, two MEDIUM and two LOW each (FR-001, FR-006).
- [X] T005 [US1] Create code-smells-project/.agents/skills/refactor-arch/SKILL.md and five references with three phases, at least eight patterns/transforms and version-specific deprecations (FR-002, FR-004, FR-005).
- [X] T006 [US1] Execute the skill analysis/audit workflow for all three projects, check findings against manual analysis and present concrete reports to the delegated reviewer; record hashes and decision in reports/approval.md (FR-007).

## Phase 4: User Story 2 - Refactor without losing workflows

Goal: approved MVC refactors preserve successful flows and reject unsafe inputs. Independent test: boot and exercise every original route with temporary synthetic data.

- [X] T007 [US2] Write tests/test_shop.py for all shop routes plus SQL injection, secret redaction, malformed input, order rollback and repeated-product stock checks (FR-008, FR-009); demonstrate baseline failures.
- [X] T008 [US2] Refactor code-smells-project/{app.py,config.py,database.py,models/,controllers/,views/,errors.py}; enforce name 2..200, finite nonnegative price, integer stock/quantity, combined duplicate items and atomic order writes (data-model, FR-008).
- [X] T009 [US2] Write ecommerce-api-legacy/test/api.test.js for checkout/report/deletion, invalid input, transaction failure, concurrency and no credential logging (FR-009); demonstrate baseline failures.
- [X] T010 [US2] Refactor ecommerce-api-legacy/src/{app.js,config.js,models/,controllers/,views/,services/,errors.js}; require nonempty usr/eml/pwd/card and positive integer c_id, transaction consistency and cleanup (FR-008).
- [X] T011 [US2] Write tests/test_tasks.py for task/user/category/login/search/stats/report routes, type validation, hash redaction, duplicate email, query counts and atomic update (FR-009); demonstrate baseline failures.
- [X] T012 [US2] Refactor task-manager-api/{app.py,config.py,database.py,models/,repositories/,controllers/,views/,routes/,utils/,services/,seed.py}; enforce title 3..200, integer priority 1..5, documented status/role values, password minimum 4, YYYY-MM-DD dates, valid references and #RRGGBB colors (FR-008).
- [X] T013 [US2] Run isolated test/boot matrix and record actual evidence in reports/after-validation.json and reports/compatibility.md; cover every original method/path (FR-009, SC-002).

## Phase 5: User Story 3 - Reuse and evaluate

Goal: identical skill copies and a reproducible assessment. Independent test: verify copy hashes and eval assertions.

- [X] T014 [US3] Copy the final refactor-arch folder to ecommerce-api-legacy/.agents/skills/ and task-manager-api/.agents/skills/ and validate identical hashes (FR-010).
- [X] T015 [US3] Create three realistic eval prompts/assertions in refactor-arch/evals/evals.json, execute sequential in-session evaluations, save grading and official skill-creator static viewer under reports/skill-evals/ (FR-002, FR-005, SC-003).
- [X] T016 [US3] Complete README.md sections Análise Manual, Construção da Skill, Resultados and Como Executar with counts, structures, checklists, logs, invocation and limitations (FR-011).

## Phase 6: Polish and convergence

- [X] T017 Check audit line references, public content, skill validator, route coverage, all tests and staged diff; record evidence in reports/validation.md (FR-012, SC-004).
- [X] T018 Execute speckit-converge against spec/plan/tasks, resolve appended tasks if necessary, and record requirements evidence in reports/convergence.md (SC-005).
- [X] T019 Commit the verified deliverable and push feature/sdd-fase-295 only; report commit and test results (Constitution workflow). Delivery evidence: reports/delivery.md.

## Dependencies and execution order

T001/T002 precede T003. T004 precedes skill construction T005; T006 is the explicit approval gate for T008/T010/T012. Baseline and skill evaluation preparation may proceed while confirmation is pending. Within each refactor, tests precede implementation. T013 depends on the three refactors; T014/T015 precede T016. T017 and convergence precede commit/push. No subagents are used.

## Parallel opportunities

US1 audit inspections are independent per project; US2 test processes can run concurrently against isolated data after implementation; US3 hash comparison and documentation-link checks are independent. Mutations and approval steps remain sequential.

## Implementation strategy

Deliver the audit and skill first (US1 MVP), review the concrete changes, then refactor and validate one app at a time. Finish with copy consistency, portable invocation docs and convergence. Do not replace evidence with a claim that all anti-patterns are universally eliminated.

## Phase 7: Convergence

- [X] T020 CRITICAL Disable implicit ancestor dotenv loading in code-smells-project/app.py, task-manager-api/app.py and scripts/validate.py; rerun smoke with explicit configuration per Constitution IV and FR-009 (contradicts).
- [X] T021 Move checkout orchestration/password/payment decisions from ecommerce-api-legacy/src/models/repository.js into controllers/checkout.js while preserving serialized transaction ownership and rerun failure/concurrency tests per FR-008 and plan: MVC responsibilities (partial).
