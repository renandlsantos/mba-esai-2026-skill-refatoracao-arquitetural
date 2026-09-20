# Feature Specification: Reusable Architecture Refactoring Skill

**Feature Branch**: `feature/sdd-fase-295`
**Created**: 2026-09-19
**Status**: Reviewed
**Input**: Build the phase 295 reusable skill, analyze and refactor the three supplied legacy applications, document and validate the result.

## User Scenarios & Testing

### User Story 1 - Understand and approve an audit (Priority: P1)
As a maintainer, I need the tool to describe my project's stack and architecture, identify actionable defects with exact evidence and let me review the proposed changes before it modifies application files.
**Why this priority**: A refactoring without evidence or consent can destroy behavior and data.
**Independent Test**: Invoke the skill on each untouched fixture; compare the report to manual findings and check the application file hashes remain unchanged at the approval boundary.
**Acceptance Scenarios**:
1. Given each of the three supplied projects, when analysis completes, then language, framework, domain, source-file count and architecture match the files.
2. Given an audit, when findings are emitted, then at least five manual findings per project appear with severity, file, exact lines, impact and recommendation, ordered by severity.
3. Given no confirmation or a rejection, when Phase 2 ends, then no application file is modified.

### User Story 2 - Improve architecture without losing workflows (Priority: P1)
As a maintainer, after approving an audit I want clear MVC responsibilities and resolved defects while legitimate original workflows remain usable.
**Why this priority**: Reorganization is valuable only if behavior still works.
**Independent Test**: Boot each application with temporary synthetic data and exercise every original route plus the observed defect regressions.
**Acceptance Scenarios**:
1. Given approval for a specific report, when refactoring completes, then data access, transport, orchestration, representation, configuration and errors have explicit boundaries.
2. Given malformed or hostile input, when it reaches a route, then the application rejects it safely without leaked secrets or partial transaction changes.
3. Given valid catalog, purchase and task workflows, when exercised after refactoring, then expected results remain available; deliberate security-related contract changes are documented.

### User Story 3 - Reuse and evaluate the skill (Priority: P2)
As an evaluator, I want identical portable skill copies and reproducible evidence for three different projects.
**Why this priority**: This proves the approach is reusable rather than a one-project script.
**Independent Test**: Compare skill-copy hashes and run the supplied validation commands from the documented prerequisites.
**Acceptance Scenarios**:
1. Given another supplied project, when the same skill is copied and invoked, then it adapts to the stack and existing separation without relying on fixture-specific names.
2. Given the repository, when the evaluator reads its README, then manual analysis, construction decisions, before/after results and executable commands are present.

### Edge Cases
- Malformed/non-object input, missing fields, invalid identifiers, duplicates, nonexistent resources and negative or non-finite values must receive controlled responses.
- A purchase with repeated items, insufficient stock or failure midway must not corrupt inventory or leave a partial order.
- Existing databases must not be overwritten or reseeded automatically.
- Unsupported or ambiguous stacks must produce evidence and a bounded plan, not fabricated version claims.
- Deprecated APIs require version-specific evidence and an applicable replacement; absence must be recorded honestly.
- Rejected or missing approval leaves target sources unchanged; prior broad authorization does not erase the skill's review checkpoint.

## Requirements

### Functional Requirements
- **FR-001**: Document manual analysis of all three fixtures with at least five findings each: one CRITICAL/HIGH, two MEDIUM and two LOW.
- **FR-002**: Deliver a skill named refactor-arch with sequential analysis, audit/confirmation and refactoring/validation phases.
- **FR-003**: Detect stack, dependencies, domain, architecture, persistence and analyzed source counts from observed evidence.
- **FR-004**: Provide Markdown knowledge references covering project analysis, anti-pattern catalog, report template, target MVC guidelines and transformation playbook.
- **FR-005**: Include at least eight anti-patterns spanning all four severities, including deprecated API detection; include at least eight before/after transformations.
- **FR-006**: Produce reports/audit-project-1.md, audit-project-2.md and audit-project-3.md with exact baseline file/line evidence and recommendations.
- **FR-007**: Request and record confirmation for the concrete audit before editing application sources; preserve sources if confirmation is absent or denied.
- **FR-008**: Refactor the three applications to MVC with isolated configuration, persistence, routing, orchestration, serialization and centralized errors while preserving valid endpoint workflows.
- **FR-009**: Validate baseline and result with repeatable boot, full route coverage and meaningful security/transaction regressions using temporary synthetic data.
- **FR-010**: Install identical skill folders in each supplied application, following the selected agent's discovered convention.
- **FR-011**: README must contain Análise Manual, Construção da Skill, Resultados and Como Executar, before/after structure, per-project checklists and actual boot/test logs.
- **FR-012**: Document scope, baseline revision, approval provenance, behavior changes, limitations and convergence against requirements without publishing course transcripts.

### Key Entities
- **Finding**: stable ID, severity, pattern, baseline revision, file, line range, observed evidence, impact, recommendation and validation.
- **Audit**: project identity, stack inventory, source count, ordered findings, coverage and approval decision.
- **Validation evidence**: command, environment, result, route/workflow exercised, before/after status and limitations.

## Success Criteria

### Measurable Outcomes
- **SC-001**: All three projects have a correct stack/domain inventory and at least five evidenced findings with the required severity distribution.
- **SC-002**: All three applications boot and every original route is exercised after refactoring; expected workflows and documented safe rejection cases pass.
- **SC-003**: Three identical skill copies provide all five knowledge areas and at least eight patterns and transformations.
- **SC-004**: No application edits precede the recorded concrete-audit confirmation; no private course materials or real secrets enter public deliverables.
- **SC-005**: Every functional requirement has a traceable implementation task and validation evidence; convergence has no unresolved required work.

## Assumptions

The supplied apps are intentionally insecure educational fixtures. Scope is local reproducible development, not production deployment or a new product authorization system. Public route names and successful domain workflows are preserved; arbitrary administrative execution and secret exposure are security defects, not legitimate compatibility obligations. Existing data is preserved. The maintainer's delegated review is recorded explicitly. Remote push is limited to the requested feature branch; merge and course submission remain outside scope.
