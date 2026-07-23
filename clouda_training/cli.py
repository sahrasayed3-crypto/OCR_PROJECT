from __future__ import annotations

import argparse
import json
from pathlib import Path

from clouda_contracts.storage import StorageRoots
from clouda_data.locations import default_catalog_path
from clouda_training.config.models import load_training_config
from clouda_training.planner import plan_training


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="clouda-training")
    subparsers = parser.add_subparsers(dest="command", required=True)
    plan = subparsers.add_parser("plan", help="Create a no-training execution plan.")
    plan.add_argument("--config", required=True, type=Path)
    plan.add_argument("--catalog", type=Path)
    plan.add_argument("--output", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = load_training_config(args.config)
    result = plan_training(
        config,
        roots=StorageRoots.from_env(),
        catalog_path=args.catalog or default_catalog_path(),
    )
    payload = json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
    if args.output:
        output = args.output.expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
