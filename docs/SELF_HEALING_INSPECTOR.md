# KDP Self-Healing Inspector

## Purpose

Inspect failed GitHub Actions runs for the KDP production pipeline, classify actionable errors, produce a redacted diagnostic report, and apply only deterministic repairs explicitly registered in config/auto_fix_rules.json.

The inspector is dependency-free and uses the Python standard library. It does not call paid AI APIs, transmit logs to third parties, or send Telegram messages.

## Operating model

1. The production workflow completes on main.
2. The inspector workflow receives the triggering run's completion event.
3. It downloads the triggering run's logs with GitHub CLI.
4. scripts/kdp_inspector.py classifies recognized failures and writes JSON/Markdown reports.
5. scripts/repair_engine.py checks the exact repair registry.
6. Every repair requires an allowed path, exact one-time match, and matching SHA-256 precondition.
7. The repository test suite runs after any applied repair.
8. A pull request is created only when a registered repair changed files and all tests pass.
9. Reports are uploaded as a GitHub Actions artifact and added to the workflow summary.

## Repair safety

Automatic repairs are deliberately constrained:
- Allowed file roots: config/, scripts/, and tests/.
- Workflow files, permissions, secrets, and release settings cannot be modified by the repair engine.
- Path traversal and symbolic links are rejected.
- Each rule must specify the target file's expected SHA-256.
- The before text must occur exactly once.
- No arbitrary shell commands or dynamically generated code are executed.
- Unknown or ambiguous failures are reported for engineering review, not guessed at.

A new repair rule should be added only after the failure has been reproduced and covered by a regression test. Compute the file hash after the intended baseline content is committed, and use an exact before/after replacement.

## Monitoring scope and limitations

The workflow listens for the named KDP Production Pipeline and Inspector Tests workflows on main. It is event-driven, not an always-on daemon. GitHub Actions must be enabled. The inspector test workflow is included in this change; production monitoring begins when the KDP Production Pipeline workflow with that exact display name is added to main.

The first version inspects failed workflow logs and can apply registered deterministic repairs. It does not claim to autonomously solve arbitrary programming defects. A future model-assisted repair stage would require an explicitly approved model provider, credential, cost limit, and review policy.

## Local tests

Run:

    python -m unittest discover -s tests -t . -v

No third-party Python packages are required.
