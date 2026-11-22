"""Resolve which artwork theme and motif count the audit workflow should inspect."""
from __future__ import annotations

import os

from scripts.art_generator import THEME_DESIGNS


def resolve_audit_theme(
    requested_theme: str = "",
    event_name: str = "",
    base_ref: str = "",
    head_ref: str = "",
) -> str:
    """Prefer an explicit dispatch choice; detect the Christmas PR automatically."""
    if requested_theme:
        theme = requested_theme
    elif event_name == "pull_request" and (
        base_ref == "christmas-theme" or head_ref == "christmas-theme"
    ):
        theme = "christmas"
    else:
        theme = "fruit"

    supported = {"fruit", *THEME_DESIGNS}
    if theme not in supported:
        raise ValueError(f"unsupported artwork audit theme: {theme}")
    return theme


def review_count(theme: str) -> int:
    """Keep the 12-design fruit pilot; inspect every motif for other themes."""
    if theme == "fruit":
        return 12
    try:
        return len(THEME_DESIGNS[theme])
    except KeyError as exc:
        raise ValueError(f"unsupported artwork audit theme: {theme}") from exc


def main() -> int:
    theme = resolve_audit_theme(
        requested_theme=os.environ.get("REQUESTED_THEME", ""),
        event_name=os.environ.get("EVENT_NAME", ""),
        base_ref=os.environ.get("BASE_REF", ""),
        head_ref=os.environ.get("HEAD_REF", ""),
    )
    print(f"theme={theme}")
    print(f"count={review_count(theme)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
