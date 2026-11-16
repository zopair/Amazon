"""Deterministic technical audit for KDP coloring-page artwork.

This tool checks measurable file and composition constraints only. It never
claims visual originality or grants human approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageOps


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _pixel_digest(image: Image.Image) -> str:
    normalized = image.convert("RGB")
    digest = hashlib.sha256()
    digest.update(f"{normalized.width}x{normalized.height}:".encode("ascii"))
    digest.update(normalized.tobytes())
    return digest.hexdigest()


def _is_binary_black_white(image: Image.Image) -> bool:
    if image.mode == "L":
        colors = image.getcolors(maxcolors=3)
        return colors is not None and all(value in (0, 255) for _, value in colors)
    if image.mode != "RGB":
        return False
    colors = image.getcolors(maxcolors=3)
    return colors is not None and all(value in ((0, 0, 0), (255, 255, 255)) for _, value in colors)


def _foreground_bbox(image: Image.Image):
    grayscale = image.convert("L")
    foreground = grayscale.point(lambda value: 255 if value < 255 else 0)
    return foreground.getbbox()


def _load_spec(spec_path: Path) -> dict[str, Any]:
    with spec_path.open("r", encoding="utf-8") as stream:
        spec = json.load(stream)
    for section in ("canvas", "rendering", "composition"):
        if not isinstance(spec.get(section), dict):
            raise ValueError(f"invalid artwork specification: missing {section} object")
    return spec


def audit_artwork_directory(input_dir: str | Path, spec_path: str | Path) -> dict[str, Any]:
    """Audit all PNG files and return a JSON-serializable report."""
    directory = Path(input_dir)
    spec = _load_spec(Path(spec_path))
    report: dict[str, Any] = {
        "schema_version": 1,
        "spec_id": spec.get("spec_id", "unspecified"),
        "input_directory": str(directory),
        "status": "PASS",
        "human_approval": "NOT_GRANTED",
        "errors": [],
        "warnings": [],
        "assets": [],
    }

    if not directory.is_dir():
        report["status"] = "FAIL"
        report["errors"].append("input_directory_not_found")
        return report

    files = sorted(path for path in directory.iterdir() if path.is_file() and path.suffix.lower() == ".png")
    if not files:
        report["status"] = "FAIL"
        report["errors"].append("no_png_assets")
        return report

    expected_width = int(spec["canvas"]["width_px"])
    expected_height = int(spec["canvas"]["height_px"])
    minimum_dpi = float(spec["canvas"].get("minimum_dpi", 300))
    safe_fraction = float(spec["composition"].get("safe_inset_fraction", 0.08))
    occupancy_min = float(spec["composition"].get("target_subject_canvas_occupancy_min", 0.0))
    occupancy_max = float(spec["composition"].get("target_subject_canvas_occupancy_max", 1.0))

    seen_file_hashes: dict[str, str] = {}
    seen_pixel_hashes: dict[str, str] = {}

    for path in files:
        asset: dict[str, Any] = {
            "file": path.name,
            "sha256": None,
            "dimensions": None,
            "dpi": None,
            "foreground_bbox": None,
            "bbox_occupancy": None,
            "errors": [],
            "warnings": [],
            "human_review": "PENDING",
        }
        try:
            asset["sha256"] = _sha256(path)
            with Image.open(path) as source:
                source.load()
                image = source.copy()
                asset["dimensions"] = [image.width, image.height]
                dpi = source.info.get("dpi")
                asset["dpi"] = list(dpi) if isinstance(dpi, tuple) else dpi

            if image.size != (expected_width, expected_height):
                asset["errors"].append("canvas_dimensions")

            if image.mode not in ("RGB", "L") or "transparency" in image.info:
                asset["errors"].append("transparency_or_unsupported_mode")
            elif not _is_binary_black_white(image):
                asset["errors"].append("non_binary_palette")

            if not isinstance(dpi, tuple) or len(dpi) < 2 or min(float(dpi[0]), float(dpi[1])) < minimum_dpi - 0.5:
                asset["errors"].append("dpi_below_minimum_or_missing")

            bbox = _foreground_bbox(image)
            if bbox is None:
                asset["errors"].append("empty_artwork")
            else:
                left, top, right, bottom = bbox
                asset["foreground_bbox"] = [left, top, right, bottom]
                width, height = image.size
                inset_x = round(width * safe_fraction)
                inset_y = round(height * safe_fraction)
                if left < inset_x or top < inset_y or right > width - inset_x or bottom > height - inset_y:
                    asset["errors"].append("safe_inset")
                occupancy = ((right - left) * (bottom - top)) / float(width * height)
                asset["bbox_occupancy"] = round(occupancy, 5)
                if occupancy < occupancy_min or occupancy > occupancy_max:
                    asset["warnings"].append("subject_bbox_occupancy_outside_target")

            file_hash = asset["sha256"]
            pixel_hash = _pixel_digest(image)
            if file_hash in seen_file_hashes:
                asset["errors"].append(f"duplicate_file:{seen_file_hashes[file_hash]}")
            elif pixel_hash in seen_pixel_hashes:
                asset["errors"].append(f"duplicate_pixels:{seen_pixel_hashes[pixel_hash]}")
            else:
                seen_file_hashes[file_hash] = path.name
                seen_pixel_hashes[pixel_hash] = path.name

        except (OSError, ValueError) as exc:
            asset["errors"].append(f"unreadable_or_invalid_png:{type(exc).__name__}")

        report["assets"].append(asset)

    error_count = sum(len(asset["errors"]) for asset in report["assets"])
    warning_count = sum(len(asset["warnings"]) for asset in report["assets"])
    report["summary"] = {
        "asset_count": len(report["assets"]),
        "error_count": error_count,
        "warning_count": warning_count,
        "human_review_pending": len(report["assets"]),
    }
    if error_count:
        report["status"] = "FAIL"
    elif warning_count:
        report["status"] = "REVIEW"
    return report


def create_contact_sheet(input_dir: str | Path, output_path: str | Path, columns: int = 3) -> Path:
    directory = Path(input_dir)
    files = sorted(path for path in directory.iterdir() if path.is_file() and path.suffix.lower() == ".png")
    if not files:
        raise ValueError("no PNG artwork available for contact sheet")
    columns = max(1, int(columns))
    cell_width, image_height, label_height, padding = 340, 420, 44, 18
    rows = (len(files) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * cell_width, rows * (image_height + label_height) + padding), "white")
    draw = ImageDraw.Draw(sheet)
    for index, path in enumerate(files):
        x = (index % columns) * cell_width
        y = (index // columns) * (image_height + label_height) + padding
        try:
            with Image.open(path) as source:
                thumb = ImageOps.contain(source.convert("RGB"), (cell_width - 2 * padding, image_height - 2 * padding))
            sheet.paste(thumb, (x + (cell_width - thumb.width) // 2, y + (image_height - thumb.height) // 2))
            draw.rectangle((x + 2, y + 2, x + cell_width - 3, y + image_height - 3), outline="black", width=1)
            draw.text((x + padding, y + image_height + 5), path.name[:44], fill="black")
        except OSError:
            draw.text((x + padding, y + padding), f"UNREADABLE: {path.name[:32]}", fill="black")
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(destination, format="PNG", optimize=True)
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit KDP coloring-page PNG artwork against the repository specification.")
    parser.add_argument("--input-dir", required=True, help="Directory containing PNG artwork files")
    parser.add_argument("--spec", default="config/artwork_generation_spec.json", help="Artwork specification JSON")
    parser.add_argument("--report", default="build/artwork-quality-report.json", help="Output JSON report path")
    parser.add_argument("--contact-sheet", default="build/artwork-contact-sheet.png", help="Output contact sheet path")
    parser.add_argument("--strict", action="store_true", help="Return non-zero for REVIEW warnings as well as FAIL")
    args = parser.parse_args()

    report = audit_artwork_directory(args.input_dir, args.spec)
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    if Path(args.input_dir).is_dir() and any(Path(args.input_dir).glob("*.png")):
        create_contact_sheet(args.input_dir, args.contact_sheet)
    print(json.dumps(report, indent=2))
    if report["status"] == "FAIL" or (args.strict and report["status"] != "PASS"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
