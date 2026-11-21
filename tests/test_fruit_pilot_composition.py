import tempfile
import unittest
from pathlib import Path

from PIL import Image

from scripts.art_generator import generate_artwork


class FruitPilotCompositionTests(unittest.TestCase):

    def test_complete_fruit_pilot_passes_the_declared_composition_gate(self):
        from scripts.artwork_quality import audit_artwork_directory

        with tempfile.TemporaryDirectory() as tmp:
            generate_artwork("fruit", 12, tmp, dpi=300, line_width_pt=9.0)
            report = audit_artwork_directory(
                tmp, Path("config/artwork_generation_spec.json")
            )
            self.assertEqual(report["status"], "PASS", report)
            self.assertEqual(report["summary"]["asset_count"], 12)
            self.assertEqual(report["summary"]["error_count"], 0)
            self.assertEqual(report["summary"]["warning_count"], 0)

    def test_banana_and_watermelon_use_larger_readable_compositions(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = generate_artwork("fruit", 12, tmp, dpi=300, line_width_pt=9.0)
            by_name = {path.name: path for path in paths}
            for filename in ("fruit_02_banana.png", "fruit_06_watermelon.png"):
                with Image.open(by_name[filename]) as image:
                    self.assertEqual(image.size, (2550, 3300))
                    self.assertGreaterEqual(image.info["dpi"][0], 299.5)
                    bbox = image.convert("L").point(lambda p: 255 if p < 255 else 0).getbbox()
                    self.assertIsNotNone(bbox)
                    left, top, right, bottom = bbox
                    occupancy = ((right - left) * (bottom - top)) / (2550 * 3300)
                    self.assertGreaterEqual(occupancy, 0.24)
                    self.assertGreaterEqual(left, 204)
                    self.assertGreaterEqual(top, 264)
                    self.assertLessEqual(right, 2346)
                    self.assertLessEqual(bottom, 3036)


if __name__ == "__main__":
    unittest.main()
