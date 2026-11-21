import tempfile
import unittest
from pathlib import Path

from scripts.artwork_loader import load_artwork

class ArtworkLoaderTests(unittest.TestCase):
    def test_refuses_to_repeat_generated_motifs_for_long_books(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError,"requires 13 unique approved artwork files"):
                load_artwork("flowers",13,Path(tmp)/"assets",Path(tmp)/"generated",300,2.4)

    def test_rejects_duplicate_approved_artwork(self):
        from PIL import Image, ImageDraw
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/"assets"/"fruit"
            source.mkdir(parents=True)
            image=Image.new("RGB",(200,200),"white")
            ImageDraw.Draw(image).ellipse((40,40,160,160),outline="black",width=8)
            image.save(source/"one.png")
            image.save(source/"two.png")
            with self.assertRaisesRegex(ValueError,"duplicate artwork"):
                load_artwork("fruit",2,Path(tmp)/"assets",Path(tmp)/"generated",300,2.4)

    def test_rejects_colored_source_artwork(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/"assets"/"flowers"
            source.mkdir(parents=True)
            Image.new("RGB",(100,100),(255,0,0)).save(source/"red.png")
            with self.assertRaisesRegex(ValueError,"monochrome"):
                load_artwork("flowers",1,Path(tmp)/"assets",Path(tmp)/"generated",300,2.4)

    def test_generates_the_12_design_review_sample(self):
        with tempfile.TemporaryDirectory() as tmp:
            images=load_artwork("fruit",12,Path(tmp)/"assets",Path(tmp)/"generated",300,2.4)
            self.assertEqual(len(images),12)
            self.assertEqual(len({p.read_bytes() for p in images}),12)

if __name__=="__main__":
    unittest.main()
