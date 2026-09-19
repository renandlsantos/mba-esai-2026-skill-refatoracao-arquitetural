# Quickstart validation

Prerequisites: Python3.12+, uv, Node, bun and Codex for the interactive skill.

1. From repository root run `bash scripts/setup.sh`.
2. Run `python3 scripts/validate.py`: 15 tests, 44 original routes, three loopback boots and identical skill copies must pass.
3. Optionally run `python3 scripts/reproduce_baseline.py` to export/reproduce the original revision into ignored temporary storage. Never run legacy app.py/app.js directly.
4. Enter each app directory, start Codex and invoke `$refactor-arch`; review Phase2 and explicitly confirm the concrete scope before Phase3.

See [README](../../README.md) for application commands and [contracts](contracts/endpoints.md) for routes. Actual output is in [after-validation.json](../../reports/after-validation.json).
