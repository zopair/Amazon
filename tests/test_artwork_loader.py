import tempfile
import unittest
from pathlib import Path

from scripts.artwork_loader import load_artwork

class ArtworkLoaderTests(unittest.TestCase):
    def test_refuses_to_repeat_generated_motifs_for_long_books(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError,"requires 13 unique approved artwork files"):
                load_artwork("fruit",13,Path(tmp)/"assets",Path(tmp)/"generated",300,2.4)

    def test_generates_the_12_design_review_sample(self):
        with tempfile.TemporaryDirectory() as tmp:
            images=load_artwork("fruit",12,Path(tmp)/"assets",Path(tmp)/"generated",300,2.4)
            self.assertEqual(len(images),12)
            self.assertEqual(len({p.read_bytes() for p in images}),12)

if __name__=="__main__":
    unittest.main()
