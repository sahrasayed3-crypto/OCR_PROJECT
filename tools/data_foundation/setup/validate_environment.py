from __future__ import annotations

import importlib
import subprocess
import sys
from pathlib import Path

REQUIRED_IMPORTS = [
    "yaml",
    "jsonschema",
    "PIL",
    "src.config.models",
    "src.pipeline.cli",
]


def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(project_root))
    missing: list[str] = []
    for module in REQUIRED_IMPORTS:
        try:
            importlib.import_module(module)
        except Exception as exc:
            missing.append(f"{module}: {exc}")
    pip_check = subprocess.run(
        [sys.executable, "-m", "pip", "check"],
        text=True,
        capture_output=True,
        check=False,
    )
    if missing:
        print("Missing imports:\n" + "\n".join(missing), file=sys.stderr)
        return 1
    if pip_check.returncode != 0:
        print(pip_check.stdout + pip_check.stderr, file=sys.stderr)
        return pip_check.returncode
    print("Environment validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
