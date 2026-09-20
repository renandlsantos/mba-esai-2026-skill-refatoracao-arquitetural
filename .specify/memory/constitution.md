# Refactor Arch Constitution

## Core Principles

### I. Evidence before modification
Every audit MUST name the inspected revision, actual stack, files and exact line ranges. Findings MUST distinguish observed defects from hypotheses. The skill MUST present the complete audit and pause for explicit confirmation before Phase 3 edits. Approval applies only to the reviewed scope.

### II. Preserve legitimate behavior
Refactoring MUST preserve the original route inventory and successful domain workflows. Security corrections may reject invalid inputs previously accepted; those differences MUST be documented and covered by tests. Existing user data MUST NOT be deleted or seeded over.

### III. MVC with explicit dependencies
Routes MUST perform transport handling, controllers MUST orchestrate use cases, models/repositories MUST own persistence and views/serializers MUST define public representations. Configuration and error handling MUST be centralized. Avoid speculative abstractions; preserve useful existing separation.

### IV. Executable validation
Baseline characterization MUST precede implementation. Each target MUST pass boot and HTTP endpoint checks after refactoring, plus regression tests for high-impact security and transaction defects. Tests MUST use synthetic temporary data, loopback listeners and isolated configuration. Report actual results, never infer success from file creation.

### V. Reusable, reviewable skill
The refactor-arch skill MUST use technology-neutral decision rules with framework-specific examples, not hardcoded project paths. Its three copies MUST be identical. Reference catalogs MUST cover at least eight anti-patterns and eight transformations, including deprecated API detection. Public reports MUST contain no private course transcripts or real secrets.

## Safety Constraints

Use only this repository for code changes. Bind local servers to 127.0.0.1. No deployment, main-branch push, merge or platform submission is authorized. Preserve upstream baseline in Git. Never execute untrusted project hooks without inspection. Authentication and data-model changes need explicit compatibility notes.

## Development Workflow

Execute constitution, specify, plan, tasks, implement and converge in order. Review each artifact before proceeding. Record audit confirmation before target-code refactoring. Run meaningful tests and inspect the staged diff before an atomic English imperative commit. Push only feature/sdd-fase-295. Record limitations and unexecuted steps honestly.

## Governance

This constitution governs the feature artifacts and code. Amendments require rationale and a compatibility assessment in the development record. Use semantic versioning: breaking principle changes increment major, additions minor, clarifications patch. Review all five principles during planning and convergence. Ratification below is the first concrete constitution for this repository.

**Version**: 1.0.0 | **Ratified**: 2026-09-19 | **Last Amended**: 2026-09-19
