import json
import tempfile
import unittest
from pathlib import Path

from scripts.cover_calculator import calculate_cover_dimensions, calculate_spine_width
from scripts.art_generator import generate_artwork
from scripts.interior_builder import build_interior
from scripts.cover_builder import build_cover
from scripts.validator import validate_book_config, validate_book


class CoverCalculatorTests(unittest.TestCase):
    def test_white_paper_spine_width_uses_official_coefficient(self):
        self.assertAlmostEqual(calculate_spine_width(100, "white"), 0.2252, places=6)

    def test_cover_dimensions_include_two_bleed_edges(self):
        result = calculate_cover_dimensions(24, 8.5, 11.0, "white", 0.125)
        self.assertAlmostEqual(result["spine_width_in"], 24 * 0.002252, places=8)
        self.assertAlmostEqual(result["cover_width_in"], 17.25 + 24 * 0.002252, places=8)
        self.assertAlmostEqual(result["cover_height_in"], 11.25, places=8)

    def test_rejects_invalid_page_counts(self):
        with self.assertRaises(ValueError):
            calculate_spine_width(23, "white")
        with self.assertRaises(ValueError):
            calculate_spine_width(25, "white")


class ProductionConfigTests(unittest.TestCase):
    def setUp(self):
        self.meta = json.loads(Path("config/book_meta.json").read_text(encoding="utf-8"))

    def test_sample_config_passes_policy_validation(self):
        self.assertEqual(validate_book_config(self.meta), [])

    def test_rejects_artwork_on_reverse_pages(self):
        broken = json.loads(json.dumps(self.meta))
        broken["interior"]["single_sided"] = False
        self.assertTrue(any("single_sided" in error for error in validate_book_config(broken)))

    def test_rejects_page_count_above_official_large_trim_maximum(self):
        broken = json.loads(json.dumps(self.meta))
        broken["interior"]["page_count"] = 592
        broken["content"]["illustration_count"] = 296
        self.assertTrue(any("maximum" in error for error in validate_book_config(broken)))

    def test_rejects_line_width_below_kdp_minimum(self):
        broken = json.loads(json.dumps(self.meta))
        broken["interior"]["line_width_pt"] = 0.5
        self.assertTrue(any("line_width_pt" in error for error in validate_book_config(broken)))


class ThemeSupportTests(unittest.TestCase):
    def test_all_requested_general_series_themes_generate_300_dpi_art(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as tmp:
            for theme in ["flowers","toys","birds","animals","professions"]:
                paths=generate_artwork(theme,1,Path(tmp)/theme,dpi=300,line_width_pt=2.4)
                self.assertEqual(len(paths),1)
                with Image.open(paths[0]) as image:
                    self.assertEqual(image.size,(2550,3300))
                    self.assertGreaterEqual(image.info["dpi"][0],299)

class SampleBuildTests(unittest.TestCase):
    def test_builds_24_page_single_sided_sample_and_cover(self):
        meta = json.loads(Path("config/book_meta.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            images = generate_artwork(
                theme="fruit", count=12, output_dir=root / "images",
                dpi=300, line_width_pt=2.4
            )
            self.assertEqual(len(images), 12)
            self.assertEqual(len({p.read_bytes() for p in images}), 12)

            interior = root / "interior.pdf"
            cover = root / "cover.pdf"
            build_interior(meta, images, interior)
            build_cover(meta, cover)

            from pypdf import PdfReader
            from scripts.pdf_sanitizer import strip_pdf_metadata
            strip_pdf_metadata(interior)
            strip_pdf_metadata(cover)
            self.assertFalse(any((PdfReader(interior).metadata or {}).values()))
            self.assertFalse(any((PdfReader(cover).metadata or {}).values()))

            report = validate_book(interior, cover, meta)
            self.assertEqual(report["status"], "PASS", report["errors"])
            self.assertEqual(report["interior"]["page_count"], 24)
            self.assertEqual(report["interior"]["illustration_pages"], 12)
            self.assertEqual(report["interior"]["blank_reverse_pages"], 12)
            self.assertTrue(report["cover"]["fonts_embedded"])
            self.assertTrue(report["interior"]["metadata_absent"])
            self.assertTrue(report["cover"]["metadata_absent"])
            self.assertTrue(report["cover"]["cmyk_colors"])


if __name__ == "__main__":
    unittest.main()
