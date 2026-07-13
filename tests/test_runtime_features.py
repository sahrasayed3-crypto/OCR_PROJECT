import tempfile
import time
import tomllib
import unittest
from pathlib import Path
from unittest.mock import patch

from pdfword.backup import create_backup, restore_backup, validate_backup
from pdfword.checkpoints import load_checkpoint, save_checkpoint
from pdfword.database import Database, utc_now
from pdfword.job_queue import JobQueue, cancel_conversion_job
from pdfword.limits import ProcessingLimits, validate_pdf_limits
from pdfword.model_registry import ModelRegistry
from pdfword.models import PageResult


class TestRuntimeFeatures(unittest.TestCase):
    def test_cancel_routes_to_the_active_queue_backend(self) -> None:
        with patch("pdfword.job_queue.get_job_queue") as local_queue:
            local_queue.return_value.cancel.return_value = True
            self.assertTrue(
                cancel_conversion_job(
                    "local-job",
                    "alice",
                    local_processing_enabled=True,
                )
            )
            local_queue.return_value.cancel.assert_called_once_with(
                "local-job", "alice"
            )

        with patch("pdfword.job_queue.get_distributed_queue") as distributed_queue:
            distributed_queue.return_value.cancel.return_value = True
            self.assertTrue(
                cancel_conversion_job(
                    "remote-job",
                    "alice",
                    local_processing_enabled=False,
                )
            )
            distributed_queue.return_value.cancel.assert_called_once_with("remote-job")

    def test_checkpoint_preserves_page_quality(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            original = PageResult(
                page_no=2,
                model_used="local:pypdf",
                markdown="hello",
                quality_score=95.0,
                text_quality_score=92.0,
                requires_manual_review=False,
            )
            save_checkpoint(tmp, {2: original})
            restored = load_checkpoint(tmp)
            self.assertEqual(restored[2].text_quality_score, 92.0)
            self.assertFalse(restored[2].requires_manual_review)

    def test_pdf_size_is_unlimited_but_page_limit_is_enforced(self) -> None:
        limits = ProcessingLimits(max_pdf_pages=2)
        validate_pdf_limits(101 * 1024 * 1024, 2, limits=limits)
        config = tomllib.loads(
            Path(".streamlit/config.toml").read_text(encoding="utf-8")
        )
        self.assertGreater(config["server"]["maxUploadSize"], 100)
        with self.assertRaisesRegex(ValueError, "صفحات"):
            validate_pdf_limits(10, 3, limits=limits)

    def test_queue_limit_and_user_owned_cancel(self) -> None:
        queue = JobQueue(max_workers=2)

        def worker(cancelled):
            for _ in range(15):
                if cancelled():
                    return
                time.sleep(0.005)

        first = queue.submit("one", "alice", worker)
        second = queue.submit("two", "bob", worker)
        third = queue.submit("three", "alice", worker)
        time.sleep(0.01)
        self.assertEqual(queue.active_count(), 3)
        self.assertFalse(queue.cancel("two", "alice"))
        self.assertTrue(queue.cancel("one", "alice"))
        first.result(timeout=2)
        second.result(timeout=2)
        third.result(timeout=2)

    def test_database_user_filter_and_backup_restore(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            database = Database(root / "source.sqlite3")
            database.login("alice")
            database.create_conversion(
                {
                    "job_id": "job-a",
                    "username": "alice",
                    "original_pdf_name": "a.pdf",
                    "stored_pdf_path": "a.pdf",
                    "status": "completed",
                    "created_at": utc_now(),
                    "updated_at": utc_now(),
                }
            )
            self.assertEqual(len(database.list_conversions("alice")), 1)
            self.assertEqual(database.list_conversions("bob"), [])
            archive = create_backup(
                database,
                storage_root=root / "conversions",
                backup_root=root / "backups",
            )
            self.assertTrue(validate_backup(archive)["valid"])
            restored = restore_backup(archive, root / "restored")
            self.assertTrue((restored / "data" / "clouda.sqlite3").is_file())

    def test_registry_excludes_safety_and_ranks_free_vision(self) -> None:
        models = [
            {
                "id": "vendor/safety:free",
                "name": "Content Safety",
                "supports_vision": True,
                "prompt_price": "0",
                "completion_price": "0",
            },
            {
                "id": "vendor/ocr-vision:free",
                "name": "OCR Vision",
                "supports_vision": True,
                "prompt_price": "0",
                "completion_price": "0",
            },
        ]
        with tempfile.TemporaryDirectory() as tmp:
            registry = ModelRegistry(Database(Path(tmp) / "db.sqlite3"))
            with patch(
                "pdfword.model_registry.discover_openrouter_models", return_value=models
            ):
                ranked = registry.ranked()
        self.assertEqual(ranked["free_vision"][0].id, "vendor/ocr-vision:free")
        self.assertEqual(ranked["excluded"][0].id, "vendor/safety:free")


if __name__ == "__main__":
    unittest.main()
