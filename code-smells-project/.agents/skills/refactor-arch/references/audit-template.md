# Audit report template

# Architecture Audit Report: PROJECT

Baseline revision/hash: ...
Stack, version evidence, domain and architecture: ...
Source files/lines and exclusion rules: ...
Persistence and route/contract inventory: ...
Baseline commands/results and limits: ...

## Summary
CRITICAL: n | HIGH: n | MEDIUM: n | LOW: n

## Findings
Order by CRITICAL, HIGH, MEDIUM, LOW. Each entry:

### [SEVERITY] STABLE-ID: Concrete defect
File: `relative/path:start-end` (baseline revision above)
Pattern: APxx
Description: observed behavior, exact evidence and reachability; redact secret values.
Impact: practical consequence.
Recommendation: scoped correction with compatibility/data implications.
Validation: observable regression that would fail before and pass after.
Confidence/limitations: uncertainties, if any.

## Deprecated APIs
Confirmed symbols/version/source/replacement, or explicitly no confirmed applicable API.

## Proposed Phase 3 scope
Modules/behaviors to change, migration strategy, tests, rollback and known exclusions.

## Confirmation
Phase 2 complete. Proceed with the scoped refactoring (Phase 3)?
Status: pending until a real reviewer response. Record report hash, response origin and allowed scope separately. Do not edit application sources while pending.

## Phase 3 follow-up (after approval)
Finding-resolution matrix, before/after structure, executed boot and endpoint checks, regression results, compatibility changes and remaining limits. Do not rewrite baseline evidence to point at new code.
