"""Christmas theme: 50 original generic motifs, bold-outline kawaii style, KDP-safe output."""
from pathlib import Path

import pytest
from PIL import Image

from scripts.art_generator import generate_artwork, THEME_DESIGNS
from scripts.theme_christmas import CHRISTMAS


def test_christmas_has_50_unique_motifs():
    assert len(CHRISTMAS) == 50
    assert len(set(CHRISTMAS)) == 50
    assert THEME_DESIGNS["christmas"] == CHRISTMAS


def test_generate_all_motifs_binary_palette(tmp_path):
    paths = generate_artwork("christmas", 50, tmp_path, dpi=300, line_width_pt=9.0)
    assert len(paths) == 50
    for path in paths:
        assert path.exists()
        with Image.open(path) as im:
            assert im.size == (2550, 3300)
            gray = im.convert("L")
            colors = gray.getcolors(maxcolors=10)
            assert colors is not None, f"{path.name}: expected binary palette"
            assert sorted(count for count, _ in colors) and {v for _, v in colors} <= {0, 255}
            # Page must actually contain ink.
            assert any(v == 0 and count > 1000 for count, v in colors), f"{path.name}: no ink"


def test_generate_rejects_over_count(tmp_path):
    with pytest.raises(ValueError):
        generate_artwork("christmas", 51, tmp_path, dpi=300, line_width_pt=9.0)
