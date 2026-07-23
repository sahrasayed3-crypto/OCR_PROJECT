from __future__ import annotations

from pathlib import Path


def main() -> int:
    temp = Path("temp")
    temp.mkdir(exist_ok=True)
    for item in temp.iterdir():
        if item.is_file():
            item.unlink()
    print("Temporary files removed from temp/ only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
