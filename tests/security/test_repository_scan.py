from __future__ import annotations

import subprocess
from pathlib import Path

from tools.validation.repository_scan import scan_repository


def _repository(tmp_path: Path, content: str) -> Path:
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / "file.txt").write_text(content, encoding="utf-8")
    subprocess.run(["git", "add", "file.txt"], cwd=tmp_path, check=True)
    return tmp_path


def test_scan_accepts_explicit_test_placeholder(tmp_path: Path) -> None:
    report = scan_repository(_repository(tmp_path, 'api_key = "test-placeholder-key"'))
    assert report["passed"] is True


def test_scan_detects_private_key_without_exposing_value(tmp_path: Path) -> None:
    marker = "-----BEGIN " + "PRIVATE KEY-----"
    report = scan_repository(_repository(tmp_path, f"{marker}\nnot-printed"))
    assert report["passed"] is False
    assert report["secret_findings"] == [
        {"path": "file.txt", "rule": "private_key", "line": 1}
    ]
    assert "not-printed" not in str(report)
