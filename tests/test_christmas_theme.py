"""Christmas theme: 50 original generic motifs, bold-outline kawaii style, KDP-safe output."""
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from scripts.art_generator import generate_artwork, THEME_DESIGNS
from scripts.theme_christmas import CHRISTMAS


class ChristmasThemeTests(unittest.TestCase):
    def test_christmas_has_50_unique_motifs(self):
        self.assertEqual(len(CHRISTMAS), 50)
        self.assertEqual(len(set(CHRISTMAS)), 50)
        self.assertEqual(THEME_DESIGNS["christmas"], CHRISTMAS)

    def test_generate_all_motifs_binary_palette(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = generate_artwork("christmas", 50, Path(tmp), dpi=300, line_width_pt=9.0)
            self.assertEqual(len(paths), 50)
            for path in paths:
                self.assertTrue(path.exists())
                with Image.open(path) as im:
                    self.assertEqual(im.size, (2550, 3300))
                    gray = im.convert("L")
                    colors = gray.getcolors(maxcolors=10)
                    self.assertIsNotNone(colors, f"{path.name}: expected binary palette")
                    self.assertLessEqual({v for _, v in colors}, {0, 255})
                    self.assertTrue(
                        any(v == 0 and count > 1000 for count, v in colors),
                        f"{path.name}: no ink",
                    )

    def test_generate_rejects_over_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                generate_artwork("christmas", 51, Path(tmp), dpi=300, line_width_pt=9.0)


if __name__ == "__main__":
    unittest.main()
