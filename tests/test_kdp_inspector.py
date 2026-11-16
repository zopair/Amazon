import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.kdp_inspector import classify_log, redact
from scripts.repair_engine import apply_rules


class InspectorTests(unittest.TestCase):
    def test_classifies_missing_dependency(self):
        result = classify_log("ModuleNotFoundError: No module named 'pypdf'")
        self.assertEqual(result["primary_category"], "dependency")
        self.assertEqual(result["finding_count"], 1)

    def test_specific_dependency_error_wins_over_traceback_header(self):
        result = classify_log("Traceback (most recent call last):\nModuleNotFoundError: No module named 'pypdf'")
        self.assertEqual(result["primary_category"], "dependency")

    def test_detects_transient_network_failure_as_retry_candidate(self):
        result = classify_log("Connection timed out while downloading artifact")
        self.assertTrue(result["retryable_candidate"])

    def test_unknown_log_does_not_invent_root_cause(self):
        result = classify_log("some opaque runner output")
        self.assertEqual(result["status"], "no_recognized_error")
        self.assertEqual(result["primary_category"], "none")

    def test_redacts_github_token(self):
        secret = "ghp_abcdefghijklmnopqrstuvwxyz123456"
        self.assertNotIn(secret, redact("token=" + secret))


class RepairEngineTests(unittest.TestCase):
    def test_applies_only_exact_hash_guarded_repair(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "scripts" / "sample.py"
            target.parent.mkdir()
            target.write_text("VALUE = 1\n", encoding="utf-8")
            digest = hashlib.sha256(target.read_bytes()).hexdigest()
            rules = root / "rules.json"
            rules.write_text(json.dumps({
                "version": 1,
                "rules": [{
                    "id": "sample-fix",
                    "path": "scripts/sample.py",
                    "expected_sha256": digest,
                    "before": "VALUE = 1",
                    "after": "VALUE = 2"
                }]
            }), encoding="utf-8")
            result = apply_rules(root, rules)
            self.assertEqual(result["applied_count"], 1)
            self.assertEqual(target.read_text(encoding="utf-8"), "VALUE = 2\n")

    def test_refuses_symlinked_parent_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outside = root / "outside"
            outside.mkdir()
            target = outside / "sample.py"
            target.write_text("VALUE = 1\n", encoding="utf-8")
            (root / "scripts").mkdir()
            (root / "scripts" / "linked").symlink_to(outside, target_is_directory=True)
            digest = hashlib.sha256(target.read_bytes()).hexdigest()
            rules = root / "rules.json"
            rules.write_text(json.dumps({
                "version": 1,
                "rules": [{
                    "id": "symlink-escape",
                    "path": "scripts/linked/sample.py",
                    "expected_sha256": digest,
                    "before": "VALUE = 1",
                    "after": "VALUE = 2"
                }]
            }), encoding="utf-8")
            result = apply_rules(root, rules)
            self.assertEqual(result["applied_count"], 0)
            self.assertEqual(result["skipped_count"], 1)
            self.assertEqual(target.read_text(encoding="utf-8"), "VALUE = 1\n")

    def test_refuses_path_traversal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rules = root / "rules.json"
            rules.write_text(json.dumps({
                "version": 1,
                "rules": [{
                    "id": "unsafe",
                    "path": "../README.md",
                    "expected_sha256": "0" * 64,
                    "before": "a",
                    "after": "b"
                }]
            }), encoding="utf-8")
            result = apply_rules(root, rules)
            self.assertEqual(result["applied_count"], 0)
            self.assertEqual(result["skipped_count"], 1)


if __name__ == "__main__":
    unittest.main()
