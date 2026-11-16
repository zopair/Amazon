# Artwork Quality Gate

## Purpose

The repository-owned `scripts.artwork_quality` tool performs deterministic checks on PNG artwork using the already-pinned Pillow dependency. It is deliberately separate from the production PDF pipeline while the visual pilot is being evaluated.

## Run locally

Generate a 12-design pilot using the existing generator:

```bash
python -c "from scripts.art_generator import generate_artwork; generate_artwork('fruit', 12, 'build/artwork-pilot', 300, 2.4)"
python -m scripts.artwork_quality --input-dir build/artwork-pilot
```

The CLI accepts `--spec`, `--report`, `--contact-sheet`, and `--strict`. The default specification is `config/artwork_generation_spec.json`.

## Checks

- Exact canvas dimensions and minimum DPI metadata.
- RGB/grayscale mode without transparency.
- Strict binary black-and-white pixels; gray and antialiasing are reported as errors.
- Non-empty foreground and the configured safe inset.
- Foreground bounding-box occupancy target (warning, not automatic rejection).
- Exact file and normalized-pixel duplicate detection.
- JSON report and a contact sheet for human inspection.

## Approval boundary

A technical `PASS` is not a visual or commercial approval. The report explicitly lists effective stroke width, contour closure, thumbnail recognition, originality, rights provenance, and near-duplicate detection as unverified checks. Every asset remains `human_review: PENDING`; the tool never grants approval, judges originality, proves legal rights, or determines the publisher's KDP AI disclosure. Pixel-level duplicate checks do not detect near-duplicates. The 50-artwork / 100-page release remains blocked until the required distinct assets receive human approval.

## Workflow

Run **Actions → Artwork Quality Audit → Run workflow** and select a theme. The workflow is manual-only, generates 12 pilot files on the ephemeral runner, and uploads the report/contact sheet for 14 days. It does not call external APIs, use AI credits, or modify production assets.
