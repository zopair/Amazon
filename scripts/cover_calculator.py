"""KDP paperback cover geometry based on official paper-specific spine coefficients."""
from __future__ import annotations

SPINE_COEFFICIENTS = {
    "white": 0.002252,
    "cream": 0.0025,
    "groundwood": 0.00235,
    "standard_color": 0.002252,
    "premium_color": 0.002347,
}


def calculate_spine_width(page_count: int, paper: str = "white") -> float:
    if not isinstance(page_count, int) or page_count < 24 or page_count % 2:
        raise ValueError("page_count must be an even integer of at least 24")
    try:
        coefficient = SPINE_COEFFICIENTS[paper]
    except KeyError as exc:
        raise ValueError(f"Unsupported paper type: {paper}") from exc
    return page_count * coefficient


def calculate_cover_dimensions(
    page_count: int,
    trim_width_in: float,
    trim_height_in: float,
    paper: str = "white",
    bleed_in: float = 0.125,
) -> dict[str, float]:
    if trim_width_in <= 0 or trim_height_in <= 0:
        raise ValueError("trim dimensions must be positive")
    if bleed_in != 0.125:
        raise ValueError("KDP paperback cover bleed must be 0.125 inches per outside edge")
    spine = calculate_spine_width(page_count, paper)
    width = (2 * trim_width_in) + spine + (2 * bleed_in)
    height = trim_height_in + (2 * bleed_in)
    return {
        "spine_width_in": spine,
        "cover_width_in": width,
        "cover_height_in": height,
        "back_panel_start_in": bleed_in,
        "spine_start_in": bleed_in + trim_width_in,
        "front_panel_start_in": bleed_in + trim_width_in + spine,
        "bleed_in": bleed_in,
    }
