#!/usr/bin/env python3
"""Apply only explicitly allowlisted, exact, SHA-256-guarded repository repairs."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any

ALLOWED_PREFIXES = ("config/", "scripts/", "tests/")
MAX_FILE_BYTES = 1024 * 1024

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()

def validate_rule(rule: dict[str, Any], root: Path) -> tuple[Path | None, str | None]:
    required = {"id", "path", "expected_sha256", "before", "after"}
    if not required.issubset(rule):
        return None, "missing required rule fields"
    rel = PurePosixPath(str(rule["path"]))
    if rel.is_absolute() or ".." in rel.parts or not str(rel).startswith(ALLOWED_PREFIXES):
        return None, "path is outside the repair allowlist"
    if not isinstance(rule["before"], str) or not isinstance(rule["after"], str):
        return None, "before and after values must be strings"
    if not isinstance(rule["expected_sha256"], str) or len(rule["expected_sha256"]) != 64:
        return None, "expected_sha256 must be a 64-character SHA-256 hex digest"
    try:
        int(rule["expected_sha256"], 16)
    except ValueError:
        return None, "expected_sha256 must be hexadecimal"
    root = root.resolve()
    path = root.joinpath(*rel.parts)
    cursor = path
    while cursor != root:
        if cursor.is_symlink():
            return None, "symbolic links in the target path are rejected"
        cursor = cursor.parent
    resolved = path.resolve()
    if root not in resolved.parents or not resolved.is_file():
        return None, "target must be a regular file inside the repository root"
    if path.stat().st_size > MAX_FILE_BYTES:
        return None, "target file exceeds size limit"
    if sha256_file(path) != rule["expected_sha256"]:
        return None, "file SHA-256 does not match the rule precondition"
    try:
        current = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None, "target is not UTF-8 text"
    before = str(rule["before"])
    if not before:
        return None, "empty before-pattern is forbidden"
    count = current.count(before)
    if count != 1:
        return None, f"expected exactly one match, found {count}"
    if current.replace(before, str(rule["after"]), 1) == current:
        return None, "repair would not change the file"
    return path, None

def apply_rules(root: Path, rules_file: Path, dry_run: bool = False) -> dict[str, Any]:
    data = json.loads(rules_file.read_text(encoding="utf-8"))
    if data.get("version") != 1 or not isinstance(data.get("rules"), list):
        raise ValueError("repair rules must have version=1 and a rules array")
    if len(data["rules"]) > 100:
        raise ValueError("repair registry exceeds the 100-rule safety limit")
    results: list[dict[str, Any]] = []
    planned_paths: set[Path] = set()
    for rule in data["rules"]:
        path, error = validate_rule(rule, root)
        if error:
            results.append({"id": rule.get("id", "unknown"), "status": "skipped", "reason": error})
            continue
        assert path is not None
        if path in planned_paths:
            results.append({"id": rule["id"], "status": "skipped", "reason": "multiple rules target the same file in one run"})
            continue
        planned_paths.add(path)
        current = path.read_text(encoding="utf-8")
        updated = current.replace(str(rule["before"]), str(rule["after"]), 1)
        if dry_run:
            results.append({"id": rule["id"], "status": "would_apply", "path": str(path.relative_to(root))})
            continue
        fd, temp_name = tempfile.mkstemp(prefix=".repair-", dir=str(path.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
                stream.write(updated)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp_name, path)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)
        results.append({"id": rule["id"], "status": "applied", "path": str(path.relative_to(root))})
    return {
        "schema_version": 1,
        "applied_count": sum(x["status"] == "applied" for x in results),
        "skipped_count": sum(x["status"] == "skipped" for x in results),
        "results": results,
    }

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--rules", default="config/auto_fix_rules.json")
    parser.add_argument("--output", default="diagnostics/latest/repairs.json")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    root = Path(args.repo_root).resolve()
    rules_file = root / args.rules
    if not rules_file.is_file():
        print(f"ERROR: repair rules file not found: {rules_file}")
        return 2
    result = apply_rules(root, rules_file, args.dry_run)
    output = root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
