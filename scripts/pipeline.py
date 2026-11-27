"""Build a clearly classified KDP sample or owner-approved production candidate."""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ImageOps
from scripts.artwork_loader import load_artwork
from scripts.interior_builder import build_interior
from scripts.cover_builder import build_cover
from scripts.validator import validate_book
from scripts.pdf_sanitizer import strip_pdf_metadata

def _sha256(path: Path) -> str:
    digest=hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b""):
            digest.update(chunk)
    return digest.hexdigest()

def _make_preview(images: list[Path], output: Path) -> None:
    thumb_w,thumb_h=300,388
    columns=4
    rows=(len(images)+columns-1)//columns
    sheet=Image.new("RGB",(columns*thumb_w,rows*thumb_h),(238,238,238))
    for index,path in enumerate(images):
        with Image.open(path) as source:
            thumb=ImageOps.contain(source.convert("RGB"),(thumb_w-20,thumb_h-20))
        x=(index%columns)*thumb_w+(thumb_w-thumb.width)//2
        y=(index//columns)*thumb_h+(thumb_h-thumb.height)//2
        sheet.paste(thumb,(x,y))
    output.parent.mkdir(parents=True,exist_ok=True)
    sheet.save(output,format="PNG",optimize=True)

def resolve_build_mode(meta: dict, artwork_spec: dict | None = None) -> str:
    """Resolve an explicit build mode and fail closed for an unapproved production candidate."""
    if not isinstance(meta, dict):
        raise ValueError("book configuration must be a JSON object")

    build_mode = meta.get("build_mode")
    if build_mode not in {"sample", "production_candidate"}:
        raise ValueError("build_mode must be explicitly set to 'sample' or 'production_candidate'")

    if build_mode == "production_candidate":
        pilot = artwork_spec.get("pilot") if isinstance(artwork_spec, dict) else None
        approved = (
            isinstance(artwork_spec, dict)
            and artwork_spec.get("status") == "approved"
            and isinstance(pilot, dict)
            and pilot.get("commercial_50_artwork_release_authorized") is True
        )
        if not approved:
            raise PermissionError(
                "production_release_not_authorized: artwork_generation_spec.json must have "
                "status='approved' and pilot.commercial_50_artwork_release_authorized=true "
                "after the required owner review"
            )

    return build_mode


def output_file_names(build_mode: str) -> dict[str, str]:
    """Return filenames that visibly distinguish samples from production candidates."""
    if build_mode == "sample":
        return {
            "interior": "interior-SAMPLE.pdf",
            "cover": "cover-SAMPLE.pdf",
            "preview": "sample-preview.png",
            "report": "sample-validation-report.json",
            "manifest": "sample-manifest.json",
        }
    if build_mode == "production_candidate":
        return {
            "interior": "interior-PRODUCTION-CANDIDATE.pdf",
            "cover": "cover-PRODUCTION-CANDIDATE.pdf",
            "preview": "production-candidate-preview.png",
            "report": "production-candidate-validation-report.json",
            "manifest": "production-candidate-manifest.json",
        }
    raise ValueError(f"unsupported build_mode: {build_mode}")


def release_metadata(build_mode: str) -> dict[str, object]:
    """Describe build status without ever granting publication authorization."""
    if build_mode == "sample":
        classification = "SAMPLE_NOT_APPROVED"
    elif build_mode == "production_candidate":
        classification = "PRODUCTION_CANDIDATE_NOT_FOR_PUBLICATION"
    else:
        raise ValueError(f"unsupported build_mode: {build_mode}")
    return {
        "build_mode": build_mode,
        "release_classification": classification,
        "publication_authorized": False,
    }


def run(
    config_path: Path,
    output_dir: Path,
    _artwork_spec_path: Path | None = None,
) -> dict:
    config_root = Path("config").resolve()
    config_path = config_path.resolve()
    if config_root not in config_path.parents or not config_path.is_file():
        raise ValueError("book configuration must be an existing JSON file inside the repository config/ directory")

    meta = json.loads(config_path.read_text(encoding="utf-8"))
    requested_mode = meta.get("build_mode") if isinstance(meta, dict) else None
    artwork_spec = None
    if requested_mode == "production_candidate":
        spec_path = _artwork_spec_path or (config_root / "artwork_generation_spec.json")
        try:
            artwork_spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise PermissionError(
                "production_release_not_authorized: artwork approval specification is missing or invalid"
            ) from exc

    build_mode = resolve_build_mode(meta, artwork_spec)
    names = output_file_names(build_mode)
    release = release_metadata(build_mode)

    count = int(meta["interior"]["page_count"]) // 2
    images = load_artwork(
        meta["content"]["theme"],
        count,
        meta["content"].get("image_directory", "assets/images"),
        meta["content"].get("generated_image_directory", "build/images"),
        int(meta["interior"]["min_dpi"]),
        float(meta["interior"]["line_width_pt"]),
    )
    interior = output_dir / names["interior"]
    cover = output_dir / names["cover"]
    preview = output_dir / names["preview"]
    report_path = output_dir / names["report"]
    manifest_path = output_dir / names["manifest"]
    output_dir.mkdir(parents=True, exist_ok=True)

    build_interior(meta, images, interior)
    build_cover(meta, cover)
    strip_pdf_metadata(interior)
    strip_pdf_metadata(cover)
    report = validate_book(interior, cover, meta)
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    _make_preview(images, preview)
    manifest = {
        "schema_version": 1,
        **release,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "book_id": meta["book_id"],
        "title": meta["title"],
        "page_count": int(meta["interior"]["page_count"]),
        "illustration_count": count,
        "trim_in": [float(meta["trim"]["width_in"]), float(meta["trim"]["height_in"])],
        "paper": meta["interior"]["paper"],
        "ink": meta["interior"]["ink"],
        "line_width_pt": float(meta["interior"]["line_width_pt"]),
        "artwork_dpi": int(meta["interior"]["min_dpi"]),
        "ai_generated_content_assessment": (
            "Publisher must answer KDP's disclosure question from the actual content creation process; "
            "this manifest does not infer the answer."
        ),
        "validation_status": report["status"],
        "files": {
            path.name: {"sha256": _sha256(path), "bytes": path.stat().st_size}
            for path in (interior, cover, preview, report_path)
        },
        "source_artwork": [{"name": path.name, "sha256": _sha256(path)} for path in images],
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return {"report": report, "manifest": manifest, "output_dir": str(output_dir)}


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config",default="config/book_meta.json")
    parser.add_argument("--output-dir",default="build/output")
    args=parser.parse_args()
    try:
        result=run(Path(args.config),Path(args.output_dir))
    except Exception as exc:
        print(json.dumps({"status":"ERROR","error_type":type(exc).__name__,"error":str(exc)},indent=2),file=sys.stderr)
        return 1
    report=result["report"]
    print(json.dumps({
        "status":report["status"],
        "output_dir":result["output_dir"],
        "errors":report["errors"],
        "manifest":result["manifest"]
    },indent=2,ensure_ascii=False))
    return 0 if report["status"]=="PASS" else 1

if __name__=="__main__":
    raise SystemExit(main())
