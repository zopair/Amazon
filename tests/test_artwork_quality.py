import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

from scripts.artwork_quality import audit_artwork_directory


class ArtworkQualityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.art_dir = self.root / "art"
        self.art_dir.mkdir()
        self.spec_path = self.root / "spec.json"
        self.spec = {
            "canvas": {"width_px": 80, "height_px": 100, "minimum_dpi": 300},
            "rendering": {"final_palette": ["#000000", "#FFFFFF"]},
            "composition": {
                "safe_inset_fraction": 0.1,
                "target_subject_canvas_occupancy_min": 0.2,
                "target_subject_canvas_occupancy_max": 0.6,
            },
        }
        self.spec_path.write_text(json.dumps(self.spec), encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def _valid_image(self, name="valid.png"):
        image = Image.new("RGB", (80, 100), "white")
        ImageDraw.Draw(image).rectangle((20, 20, 59, 79), fill="black")
        path = self.art_dir / name
        image.save(path, dpi=(300, 300))
        return path

    def test_accepts_technically_valid_artwork_but_keeps_human_review_pending(self):
        self._valid_image()
        report = audit_artwork_directory(self.art_dir, self.spec_path)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["assets"][0]["human_review"], "PENDING")
        self.assertEqual(report["assets"][0]["errors"], [])

    def test_rejects_wrong_canvas_dimensions(self):
        Image.new("RGB", (79, 100), "white").save(self.art_dir / "wrong.png", dpi=(300, 300))
        report = audit_artwork_directory(self.art_dir, self.spec_path)
        self.assertEqual(report["status"], "FAIL")
        self.assertIn("canvas_dimensions", report["assets"][0]["errors"])

    def test_rejects_gray_pixels(self):
        image = Image.new("RGB", (80, 100), "white")
        ImageDraw.Draw(image).rectangle((20, 20, 59, 79), fill=(120, 120, 120))
        image.save(self.art_dir / "gray.png", dpi=(300, 300))
        report = audit_artwork_directory(self.art_dir, self.spec_path)
        self.assertIn("non_binary_palette", report["assets"][0]["errors"])

    def test_rejects_transparency(self):
        image = Image.new("RGBA", (80, 100), (255, 255, 255, 255))
        ImageDraw.Draw(image).rectangle((20, 20, 59, 79), fill=(0, 0, 0, 255))
        image.save(self.art_dir / "alpha.png", dpi=(300, 300))
        report = audit_artwork_directory(self.art_dir, self.spec_path)
        self.assertIn("transparency_or_unsupported_mode", report["assets"][0]["errors"])

    def test_rejects_content_outside_safe_inset(self):
        image = Image.new("RGB", (80, 100), "white")
        ImageDraw.Draw(image).rectangle((2, 20, 59, 79), fill="black")
        image.save(self.art_dir / "clipped.png", dpi=(300, 300))
        report = audit_artwork_directory(self.art_dir, self.spec_path)
        self.assertIn("safe_inset", report["assets"][0]["errors"])

    def test_detects_pixel_identical_duplicates_even_with_different_filenames(self):
        self._valid_image("one.png")
        self._valid_image("two.png")
        report = audit_artwork_directory(self.art_dir, self.spec_path)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("duplicate" in error for asset in report["assets"] for error in asset["errors"]))

    def test_empty_directory_is_a_failure(self):
        report = audit_artwork_directory(self.art_dir, self.spec_path)
        self.assertEqual(report["status"], "FAIL")
        self.assertIn("no_png_assets", report["errors"])


if __name__ == "__main__":
    unittest.main()
