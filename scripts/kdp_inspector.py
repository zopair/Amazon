#!/usr/bin/env python3
"""Dependency-free GitHub Actions log inspector for the KDP production repository."""
from __future__ import annotations
import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

MAX_LOG_BYTES = 8 * 1024 * 1024
PATTERNS = [
    ("missing_dependency", re.compile(r"ModuleNotFoundError|ImportError:", re.I), "dependency"),
    ("missing_file", re.compile(r"FileNotFoundError|No such file or directory", re.I), "filesystem"),
    ("permission", re.compile(r"PermissionError|Permission denied|EACCES", re.I), "permissions"),
    ("assertion", re.compile(r"AssertionError|assert .* failed", re.I), "validation"),
    ("pdf_failure", re.compile(r"\b(PDF|pypdf|reportlab|fitz)\b.*\b(error|failed|invalid|exception)\b", re.I), "pdf"),
    ("network_transient", re.compile(r"timed? ?out|connection reset|temporary failure|502 Bad Gateway|503 Service Unavailable|429 Too Many Requests", re.I), "transient"),
    ("resource_exhaustion", re.compile(r"No space left on device|out of memory|OOMKilled|memory limit", re.I), "resources"),
    ("python_traceback", re.compile(r"Traceback \(most recent call last\):|^\s*[A-Za-z_][\w.]*Error:", re.I), "python"),
    ("workflow_failure", re.compile(r"Process completed with exit code [1-9]\d*|Error: Process completed", re.I), "workflow"),
    ("generic_error", re.compile(r"(^|\s)(ERROR|FATAL|Error:)(\s|:)", re.I), "unknown"),
]
SECRET_PATTERNS = [
    re.compile(r"(?i)(gh[pousr]_[A-Za-z0-9_]{20,})"),
    re.compile(r"(?i)(github_pat_[A-Za-z0-9_]{20,})"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"(?i)(xox[baprs]-[A-Za-z0-9-]{10,})"),
    re.compile(r"(?i)(sk-[A-Za-z0-9]{24,})"),
    re.compile(r"(?i)(Bearer\s+)[A-Za-z0-9._~+/-]{12,}"),
    re.compile(r"(?i)((?:token|password|secret|api[_-]?key)\s*[=:]\s*)[^\s,;]+"),
]
LOCATION_RE = re.compile(r"(?P<path>(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+\.(?:py|json|ya?ml|toml|txt)):(?P<line>\d+)(?::(?P<column>\d+))?")
STEP_RE = re.compile(r"##\[group\](?:Run )?(?P<step>.+?)\s*$", re.I)

def redact(text: str) -> str:
    for pattern in SECRET_PATTERNS:
        if pattern.groups >= 2:
            text = pattern.sub(r"\1[REDACTED]", text)
        else:
            text = pattern.sub("[REDACTED]", text)
    return text

def classify_log(log_text: str) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    current_step = "unknown"
    for index, raw in enumerate(log_text.splitlines(), start=1):
        line = raw.strip()
        step_match = STEP_RE.search(line)
        if step_match:
            current_step = step_match.group("step").strip()
        for code, pattern, category in PATTERNS:
            if pattern.search(line):
                location = LOCATION_RE.search(line)
                findings.append({
                    "code": code, "category": category, "line": index,
                    "step": current_step, "message": redact(line[:1200]),
                    "file": location.group("path") if location else None,
                    "source_line": int(location.group("line")) if location else None,
                })
                break
    unique: list[dict[str, Any]] = []
    seen: set[tuple[Any, ...]] = set()
    for item in findings:
        key = (item["code"], item["message"], item["file"], item["source_line"])
        if key not in seen:
            seen.add(key)
            unique.append(item)
    categories = Counter(item["category"] for item in unique)
    primary = "none" if not unique else unique[0]["category"]
    priority = {"dependency", "filesystem", "permissions", "resources", "pdf", "validation"}
    if any(item["category"] in priority for item in unique):
        primary = next(item["category"] for item in unique if item["category"] in priority)
    retry_categories = {"transient", "workflow"}
    retryable = any(item["category"] == "transient" for item in unique) and all(item["category"] in retry_categories for item in unique)
    return {
        "status": "failure_detected" if unique else "no_recognized_error",
        "primary_category": primary, "retryable_candidate": retryable,
        "finding_count": len(unique), "category_counts": dict(categories),
        "findings": unique[:100],
    }

def build_report(log_text: str, metadata: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": 1, "generated_at": datetime.now(timezone.utc).isoformat(),
        "repository": metadata.get("repository"), "run_id": metadata.get("run_id"),
        "run_attempt": metadata.get("run_attempt"), "workflow": metadata.get("workflow"),
        "head_branch": metadata.get("head_branch"), "conclusion": metadata.get("conclusion"),
        **classify_log(log_text),
        "note": "Log classification is diagnostic evidence, not proof of root cause. Unknown errors require review.",
    }

def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# KDP Workflow Diagnostic Report", "",
        f"- Repository: `{report.get('repository') or 'unknown'}`",
        f"- Workflow: `{report.get('workflow') or 'unknown'}`",
        f"- Run ID: `{report.get('run_id') or 'unknown'}` (attempt {report.get('run_attempt') or 'unknown'})",
        f"- Branch: `{report.get('head_branch') or 'unknown'}`",
        f"- Conclusion: `{report.get('conclusion') or 'unknown'}`",
        f"- Classification: **{report['status']}** / `{report['primary_category']}`",
        f"- Retryable candidate: `{str(report['retryable_candidate']).lower()}`", "",
        "## Findings", "",
    ]
    if not report["findings"]:
        lines.append("No recognized error pattern was found. Inspect the original workflow logs.")
    for item in report["findings"]:
        location = f" — `{item['file']}:{item['source_line']}`" if item.get("file") else ""
        safe_message = item["message"].replace("`", "'")
        lines.extend([
            f"### {item['code']} ({item['category']})",
            f"- Workflow log line: {item['line']}",
            f"- Step: {item['step']}",
            f"- Source location: {location or 'not identified'}",
            f"- Message: `{safe_message}`", "",
        ])
    lines.extend([
        "## Safety", "",
        "No source files were changed by the log reader. Automatic changes, if any, are restricted to exact, hash-guarded rules in config/auto_fix_rules.json and must pass the test suite before a pull request is created.",
        "",
    ])
    return "\n".join(lines)

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log-file", required=True)
    parser.add_argument("--output-dir", default="diagnostics/latest")
    parser.add_argument("--repository", default="")
    parser.add_argument("--run-id", default="")
    parser.add_argument("--run-attempt", default="")
    parser.add_argument("--workflow", default="")
    parser.add_argument("--head-branch", default="")
    parser.add_argument("--conclusion", default="")
    args = parser.parse_args()
    log_path = Path(args.log_file)
    if not log_path.is_file():
        print(f"ERROR: log file not found: {log_path}", file=sys.stderr)
        return 2
    if log_path.stat().st_size > MAX_LOG_BYTES:
        print(f"ERROR: log file exceeds {MAX_LOG_BYTES} bytes", file=sys.stderr)
        return 2
    log_text = log_path.read_text(encoding="utf-8", errors="replace")
    metadata = {
        "repository": args.repository, "run_id": args.run_id,
        "run_attempt": args.run_attempt, "workflow": args.workflow,
        "head_branch": args.head_branch, "conclusion": args.conclusion,
    }
    report = build_report(log_text, metadata)
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (output / "report.md").write_text(render_markdown(report), encoding="utf-8")
    print(render_markdown(report))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
