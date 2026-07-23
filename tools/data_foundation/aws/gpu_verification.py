from __future__ import annotations

import shutil
import subprocess


def main() -> int:
    if not shutil.which("nvidia-smi"):
        print("nvidia-smi not available.")
        return 1
    return subprocess.call(["nvidia-smi"])


if __name__ == "__main__":
    raise SystemExit(main())
