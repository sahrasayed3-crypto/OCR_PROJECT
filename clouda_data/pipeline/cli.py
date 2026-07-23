from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path

from clouda_contracts.storage import StorageRoots
from clouda_data.config.loader import load_config
from clouda_data.datasets.downloader import (
    download_dataset_sample,
    result_to_dict,
    verify_download,
)
from clouda_data.datasets.rasam_batch import (
    download_rasam_first_batch,
    plan_rasam_first_batch,
    plan_to_dict as rasam_plan_to_dict,
    result_to_dict as rasam_result_to_dict,
    verify_rasam_first_batch,
)
from clouda_data.datasets.registry import (
    estimate_source_download,
    get_source,
    list_sources,
    verify_license,
)
from clouda_data.datasets.reports import generate_download_report
from clouda_data.ingestion.file_inspection import inspect_file
from clouda_data.ingestion.registry import read_registry
from clouda_data.ingestion.workflow import (
    ingest_source_manifest,
    plan_to_dict,
    validate_source_manifest_file,
)
from clouda_data.locations import (
    default_data_config_path,
    default_foundation_registry_path,
    default_profile_dir,
    repository_root,
)
from clouda_data.pipeline.profiles import list_profile_paths, load_profile


def _project_root() -> Path:
    return repository_root() or Path.cwd().resolve()


def _dataset_workspace() -> Path:
    return StorageRoots.from_env().dataset_root


def _artifact_workspace() -> Path:
    return StorageRoots.from_env().artifact_root


def _cache_workspace() -> Path:
    return StorageRoots.from_env().cache_root


def _catalog_path(value: str | None) -> Path:
    return (
        Path(value).expanduser().resolve()
        if value
        else default_foundation_registry_path()
    )


def _profile_root(value: str | None) -> Path:
    return Path(value).expanduser().resolve() if value else default_profile_dir()


def inspect_config(args: argparse.Namespace) -> int:
    config = load_config(args.config or default_data_config_path(), _dataset_workspace())
    print(
        json.dumps(
            {
                "render_dpi": config.runtime.render_dpi,
                "workers": config.runtime.workers,
                "aws_enabled": config.aws.enabled,
            },
            indent=2,
        )
    )
    return 0


def validate_project(args: argparse.Namespace) -> int:
    root = _project_root()
    required = ["clouda_data", "tests", "docs"]
    missing = [path for path in required if not (root / path).exists()]
    if missing:
        print("Missing required paths: " + ", ".join(missing), file=sys.stderr)
        return 1
    for profile_path in list_profile_paths():
        load_profile(profile_path)
    print("Project foundation validation passed.")
    return 0


def validate_input(args: argparse.Namespace) -> int:
    from clouda_data.ingestion.manifest import read_page_manifest

    records = read_page_manifest(args.manifest)
    print(f"Input manifest contains {len(records)} page record(s).")
    return 0


def inspect_source(args: argparse.Namespace) -> int:
    payload = [inspect_file(path, args.source_type).__dict__ for path in args.paths]
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if all(item["ok"] for item in payload) else 1


def validate_source(args: argparse.Namespace) -> int:
    plan = validate_source_manifest_file(args.manifest, _dataset_workspace())
    print(json.dumps(plan_to_dict(plan), ensure_ascii=False, indent=2))
    return 0 if plan.ok else 1


def ingest(args: argparse.Namespace) -> int:
    plan = ingest_source_manifest(
        args.manifest, _dataset_workspace(), dry_run=args.dry_run
    )
    print(json.dumps(plan_to_dict(plan), ensure_ascii=False, indent=2))
    return 0 if plan.ok else 1


def list_ingested(args: argparse.Namespace) -> int:
    root = _dataset_workspace()
    page_manifest = root / "data/manifests/page_manifest.json"
    registry = root / "data/manifests/file_registry.json"
    payload = {
        "pages": (
            json.loads(page_manifest.read_text(encoding="utf-8"))
            if page_manifest.exists()
            else []
        ),
        "files": read_registry(registry),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def find_duplicates(args: argparse.Namespace) -> int:
    registry = read_registry(
        _dataset_workspace() / "data/manifests/file_registry.json"
    )
    by_checksum: dict[str, list[dict]] = {}
    for item in registry:
        by_checksum.setdefault(item["checksum"], []).append(item)
    duplicates = {
        checksum: items
        for checksum, items in by_checksum.items()
        if len(items) > 1 or any(item.get("duplicate_of") for item in items)
    }
    print(json.dumps(duplicates, ensure_ascii=False, indent=2))
    return 0


def generate_ingestion_report(args: argparse.Namespace) -> int:
    root = _dataset_workspace()
    if args.manifest:
        plan = validate_source_manifest_file(args.manifest, root)
        payload = plan_to_dict(plan)
    else:
        payload = {
            "pages": (
                json.loads(
                    (root / "data/manifests/page_manifest.json").read_text(
                        encoding="utf-8"
                    )
                )
                if (root / "data/manifests/page_manifest.json").exists()
                else []
            ),
            "files": read_registry(root / "data/manifests/file_registry.json"),
        }
    out = (
        Path(args.output).expanduser().resolve()
        if args.output
        else _artifact_workspace() / "reports" / "ingestion_report.json"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(str(out))
    return 0


def list_dataset_sources(args: argparse.Namespace) -> int:
    sources = list_sources(_catalog_path(args.registry))
    if args.classification:
        sources = [
            source
            for source in sources
            if source["classification"] == args.classification
        ]
    payload = [
        {
            "source_id": source["source_id"],
            "name": source["name"],
            "classification": source["classification"],
            "license": source["license"],
            "commercial_use_status": source["commercial_use_status"],
            "risk_level": source["risk_level"],
        }
        for source in sources
    ]
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def describe_dataset_source(args: argparse.Namespace) -> int:
    print(
        json.dumps(
            get_source(args.source_id, _catalog_path(args.registry)),
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def verify_dataset_license(args: argparse.Namespace) -> int:
    result = verify_license(get_source(args.source_id, _catalog_path(args.registry)))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["sample_download_allowed"] else 1


def estimate_download(args: argparse.Namespace) -> int:
    source = get_source(args.source_id, _catalog_path(args.registry))
    print(
        json.dumps(
            estimate_source_download(source, sample_only=not args.full_dataset),
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def download_dataset_sample_cli(args: argparse.Namespace) -> int:
    result = download_dataset_sample(
        args.source_id,
        project_root=_dataset_workspace(),
        registry_path=_catalog_path(args.registry),
        max_bytes=args.max_bytes,
        dry_run=args.dry_run,
    )
    print(json.dumps(result_to_dict(result), ensure_ascii=False, indent=2))
    return 0 if result.ok else 1


def resume_download(args: argparse.Namespace) -> int:
    return download_dataset_sample_cli(args)


def verify_download_cli(args: argparse.Namespace) -> int:
    result = verify_download(args.source_id, project_root=_dataset_workspace())
    print(json.dumps(result_to_dict(result), ensure_ascii=False, indent=2))
    return 0 if result.ok else 1


def generate_download_report_cli(args: argparse.Namespace) -> int:
    output = (
        Path(args.output).expanduser().resolve()
        if args.output
        else _artifact_workspace() / "reports" / "dataset_download_report.json"
    )
    out = generate_download_report(_dataset_workspace(), output)
    print(str(out))
    return 0


def plan_rasam_first_batch_cli(args: argparse.Namespace) -> int:
    plan = plan_rasam_first_batch(
        _dataset_workspace(), batch_size=args.pages, max_bytes=args.max_bytes
    )
    print(json.dumps(rasam_plan_to_dict(plan), ensure_ascii=False, indent=2))
    return 0 if plan.ok else 1


def download_rasam_first_batch_cli(args: argparse.Namespace) -> int:
    result = download_rasam_first_batch(
        _dataset_workspace(), batch_size=args.pages, max_bytes=args.max_bytes
    )
    print(json.dumps(rasam_result_to_dict(result), ensure_ascii=False, indent=2))
    return 0 if result.ok else 1


def verify_rasam_first_batch_cli(args: argparse.Namespace) -> int:
    result = verify_rasam_first_batch(_dataset_workspace())
    print(json.dumps(rasam_result_to_dict(result), ensure_ascii=False, indent=2))
    return 0 if result.ok else 1


def list_profiles(args: argparse.Namespace) -> int:
    for path in list_profile_paths(_profile_root(args.config_dir)):
        profile = load_profile(path)
        print(profile["name"])
    return 0


def describe_profile(args: argparse.Namespace) -> int:
    path = _profile_root(args.config_dir) / f"{args.name}.json"
    profile = load_profile(path)
    print(json.dumps(profile, ensure_ascii=False, indent=2))
    return 0


def preview(args: argparse.Namespace) -> int:
    if not args.synthetic_test:
        print(
            "Only --synthetic-test previews are enabled during foundation preparation.",
            file=sys.stderr,
        )
        return 2
    out = _artifact_workspace() / "previews" / "synthetic_preview.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        "Synthetic preview placeholder only. No real distorted page was generated.\n",
        encoding="utf-8",
    )
    print(str(out))
    return 0


def dry_run(args: argparse.Namespace) -> int:
    validate_project(args)
    print(
        "Dry run completed. No ingestion, distortion, training, or AWS action was executed."
    )
    return 0


def status(args: argparse.Namespace) -> int:
    status_path = _project_root() / "PROJECT_STATUS.md"
    print(
        status_path.read_text(encoding="utf-8")
        if status_path.exists()
        else "PROJECT_STATUS.md is missing."
    )
    return 0


def cleanup(args: argparse.Namespace) -> int:
    targets = [_cache_workspace() / "temporary"]
    for target in targets:
        if target.exists():
            for child in target.iterdir():
                if child.is_file():
                    child.unlink()
    print("Cleaned temporary files only.")
    return 0


def run_tests(args: argparse.Namespace) -> int:
    return subprocess.call(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", "."]
    )


def system_inspection(args: argparse.Namespace) -> int:
    payload = {
        "platform": platform.platform(),
        "python": sys.version,
        "git": shutil.which("git"),
        "docker": shutil.which("docker"),
        "wsl": shutil.which("wsl"),
        "tesseract": shutil.which("tesseract"),
    }
    print(json.dumps(payload, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m clouda_data.pipeline.cli")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("inspect-config")
    p.add_argument("--config")
    p.set_defaults(func=inspect_config)

    p = sub.add_parser("validate-project")
    p.set_defaults(func=validate_project)

    p = sub.add_parser("validate-input")
    p.add_argument("manifest")
    p.set_defaults(func=validate_input)

    p = sub.add_parser("inspect-source")
    p.add_argument("paths", nargs="+")
    p.add_argument(
        "--source-type",
        choices=[
            "pdf",
            "docx",
            "image",
            "text",
            "json_layout",
            "page_xml",
            "alto_xml",
            "ground_truth_json",
        ],
    )
    p.set_defaults(func=inspect_source)

    p = sub.add_parser("validate-source")
    p.add_argument("manifest")
    p.set_defaults(func=validate_source)

    p = sub.add_parser("ingest")
    p.add_argument("manifest")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=ingest)

    p = sub.add_parser("list-ingested")
    p.set_defaults(func=list_ingested)

    p = sub.add_parser("find-duplicates")
    p.set_defaults(func=find_duplicates)

    p = sub.add_parser("generate-ingestion-report")
    p.add_argument("--manifest")
    p.add_argument("--output")
    p.set_defaults(func=generate_ingestion_report)

    p = sub.add_parser("list-dataset-sources")
    p.add_argument("--registry")
    p.add_argument("--classification")
    p.set_defaults(func=list_dataset_sources)

    p = sub.add_parser("describe-dataset-source")
    p.add_argument("source_id")
    p.add_argument("--registry")
    p.set_defaults(func=describe_dataset_source)

    p = sub.add_parser("verify-dataset-license")
    p.add_argument("source_id")
    p.add_argument("--registry")
    p.set_defaults(func=verify_dataset_license)

    p = sub.add_parser("estimate-download")
    p.add_argument("source_id")
    p.add_argument("--registry")
    p.add_argument("--full-dataset", action="store_true")
    p.set_defaults(func=estimate_download)

    p = sub.add_parser("download-dataset-sample")
    p.add_argument("source_id")
    p.add_argument("--registry")
    p.add_argument("--max-bytes", type=int, default=100 * 1024 * 1024)
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=download_dataset_sample_cli)

    p = sub.add_parser("resume-download")
    p.add_argument("source_id")
    p.add_argument("--registry")
    p.add_argument("--max-bytes", type=int, default=100 * 1024 * 1024)
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=resume_download)

    p = sub.add_parser("verify-download")
    p.add_argument("source_id")
    p.set_defaults(func=verify_download_cli)

    p = sub.add_parser("generate-download-report")
    p.add_argument("--output")
    p.set_defaults(func=generate_download_report_cli)

    p = sub.add_parser("plan-rasam-first-batch")
    p.add_argument("--pages", type=int, default=100)
    p.add_argument("--max-bytes", type=int, default=1024 * 1024 * 1024)
    p.set_defaults(func=plan_rasam_first_batch_cli)

    p = sub.add_parser("download-rasam-first-batch")
    p.add_argument("--pages", type=int, default=100)
    p.add_argument("--max-bytes", type=int, default=1024 * 1024 * 1024)
    p.set_defaults(func=download_rasam_first_batch_cli)

    p = sub.add_parser("verify-rasam-first-batch")
    p.set_defaults(func=verify_rasam_first_batch_cli)

    p = sub.add_parser("list-profiles")
    p.add_argument("--config-dir")
    p.set_defaults(func=list_profiles)

    p = sub.add_parser("describe-profile")
    p.add_argument("name")
    p.add_argument("--config-dir")
    p.set_defaults(func=describe_profile)

    p = sub.add_parser("preview")
    p.add_argument("--synthetic-test", action="store_true")
    p.set_defaults(func=preview)

    p = sub.add_parser("dry-run")
    p.set_defaults(func=dry_run)

    p = sub.add_parser("status")
    p.set_defaults(func=status)

    p = sub.add_parser("cleanup")
    p.set_defaults(func=cleanup)

    p = sub.add_parser("test")
    p.set_defaults(func=run_tests)

    p = sub.add_parser("inspect-system")
    p.set_defaults(func=system_inspection)

    for future in ["render", "distort", "validate", "evaluate", "resume"]:
        p = sub.add_parser(future)
        p.set_defaults(
            func=lambda args, name=future: (
                print(f"{name} is reserved for a later phase."),
                2,
            )[1]
        )

    return parser


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
