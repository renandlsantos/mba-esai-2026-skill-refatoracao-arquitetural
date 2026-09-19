#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -x .work/venv-shop/bin/python ]; then uv venv --python 3.12 .work/venv-shop; fi
if [ ! -x .work/venv-tasks/bin/python ]; then uv venv --python 3.12 .work/venv-tasks; fi
uv pip install --python .work/venv-shop/bin/python -r code-smells-project/requirements-lock.txt
uv pip install --python .work/venv-tasks/bin/python -r task-manager-api/requirements-lock.txt
(cd ecommerce-api-legacy && bun install --frozen-lockfile)
