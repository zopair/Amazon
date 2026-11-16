"""Load approved original art or generate a bounded sample without repeating motifs."""
from __future__ import annotations
import hashlib
from pathlib import Path
from PIL import Image, ImageChops
from scripts.art_generator import generate_artwork

def _flatten_to_rgb(source: Path, destination: Path, dpi: int) -> bytes:
    with Image.open(source) as opened:
        opened.load()
        rgba=opened.convert("RGBA")
        background=Image.new("RGBA",rgba.size,(255,255,255,255))
        background.alpha_composite(rgba)
        flattened=background.convert("RGB")
        gray=flattened.convert("L")
        neutral=Image.merge("RGB",(gray,gray,gray))
        if ImageChops.difference(flattened,neutral).getbbox():
            raise ValueError(f"source artwork must be monochrome black line art: {source.name}")
        # Convert anti-aliased grayscale edges to pure black/white; no gray fills or shading survive.
        binary=gray.point(lambda value: 0 if value<128 else 255).convert("RGB")
        pixels=binary.tobytes()
        destination.parent.mkdir(parents=True,exist_ok=True)
        binary.save(destination,format="PNG",dpi=(dpi,dpi),optimize=True)
        return hashlib.sha256(pixels).digest()

def load_artwork(
    theme: str,
    count: int,
    assets_root: str|Path,
    generated_root: str|Path,
    dpi: int=300,
    line_width_pt: float=2.4
) -> list[Path]:
    if count<1 or count>50:
        raise ValueError("book artwork count must be between 1 and 50")
    source_dir=Path(assets_root)/theme
    candidates=sorted(
        path for path in source_dir.iterdir()
        if path.is_file() and path.suffix.lower() in {".png",".jpg",".jpeg"}
    ) if source_dir.is_dir() else []
    if not candidates:
        if count>12:
            raise ValueError(
                f"{theme} book requires {count} unique approved artwork files in {source_dir}; "
                "the built-in generator has only 12 distinct motifs and will not repeat them."
            )
        return generate_artwork(theme,count,generated_root,dpi,line_width_pt)
    if len(candidates)!=count:
        raise ValueError(
            f"{theme} book requires exactly {count} approved artwork files in {source_dir}; "
            f"found {len(candidates)}. Partial asset sets are not silently padded."
        )
    output=Path(generated_root)
    output.mkdir(parents=True,exist_ok=True)
    paths=[]
    hashes=set()
    for index,source in enumerate(candidates,1):
        destination=output/f"approved_{theme}_{index:02d}.png"
        digest=_flatten_to_rgb(source,destination,dpi)
        if digest in hashes:
            raise ValueError(f"duplicate artwork detected after flattening: {source.name}")
        hashes.add(digest)
        paths.append(destination)
    return paths
