"""Build a single-page-per-PDF-page, single-sided KDP coloring-book interior."""
from __future__ import annotations
from pathlib import Path
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

PT_PER_INCH = 72.0

def build_interior(meta: dict, image_paths: list[str | Path], output_path: str | Path) -> Path:
    interior = meta["interior"]
    trim = meta["trim"]
    page_count = int(interior["page_count"])
    if page_count < 24 or page_count % 2:
        raise ValueError("KDP paperback interior page_count must be even and at least 24")
    expected_images = page_count // 2
    if len(image_paths) != expected_images:
        raise ValueError(f"Expected {expected_images} artwork files for {page_count} pages, got {len(image_paths)}")
    page_w = float(trim["width_in"]) * PT_PER_INCH
    page_h = float(trim["height_in"]) * PT_PER_INCH
    margins = [
        float(interior["inside_margin_in"]) * PT_PER_INCH,
        float(interior["outside_margin_in"]) * PT_PER_INCH,
        float(interior["top_margin_in"]) * PT_PER_INCH,
        float(interior["bottom_margin_in"]) * PT_PER_INCH,
    ]
    inside, outside, top, bottom = margins
    available_w = page_w - inside - outside
    available_h = page_h - top - bottom
    if available_w <= 0 or available_h <= 0:
        raise ValueError("Interior margins leave no printable area")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(output), pagesize=(page_w, page_h), pageCompression=1, invariant=1)
    pdf.setTitle(str(meta["title"]) + " — Interior")
    pdf.setAuthor(str(meta.get("author") or ""))
    for index, image_path in enumerate(image_paths):
        path = Path(image_path)
        if not path.is_file():
            raise FileNotFoundError(path)
        reader = ImageReader(str(path))
        image_w, image_h = reader.getSize()
        scale = min(available_w / image_w, available_h / image_h)
        draw_w, draw_h = image_w * scale, image_h * scale
        x = inside + (available_w - draw_w) / 2
        y = bottom + (available_h - draw_h) / 2
        # Odd-numbered recto page: exactly one coloring illustration.
        pdf.drawImage(reader, x, y, width=draw_w, height=draw_h, preserveAspectRatio=True, mask=None)
        pdf.showPage()
        # Even-numbered verso page: intentionally empty, including no folio or watermark.
        pdf.showPage()
    pdf.save()
    return output
