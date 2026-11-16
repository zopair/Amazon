# Amazon KDP Production Engine

Repository for an automated Amazon KDP children's coloring-book production pipeline.

## Current components

- [Self-Healing Inspector](docs/SELF_HEALING_INSPECTOR.md): event-driven workflow diagnostics, redacted error reports, bounded transient retries, and guarded automatic repairs.
- `scripts/kdp_inspector.py`: classify GitHub Actions logs and generate JSON/Markdown reports.
- `scripts/repair_engine.py`: apply only registered exact-match repairs with SHA-256 preconditions.
- `config/auto_fix_rules.json`: allowlisted repair registry (empty until a repair has been reproduced and tested).
- `tests/`: regression tests for diagnostics and repair safety.

## Important

The inspector monitors a workflow whose display name is exactly **KDP Production Pipeline** on `main`. It becomes active when that production workflow is added and GitHub Actions is enabled.

The inspector is not an always-on daemon and does not solve arbitrary code defects by guessing. Unknown failures are documented for review. Registered repairs are applied only after exact-match and hash checks, and a pull request is created only if the test suite passes.

## Tests

```bash
python -m unittest discover -s tests -t . -v
```
