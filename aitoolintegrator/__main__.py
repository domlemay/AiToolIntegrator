"""Entrypoint for python -m aitoolintegrator."""

import sys

# Force UTF-8 on Windows to handle emoji/Unicode in Rich output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]

from aitoolintegrator.cli.main import app

app()
