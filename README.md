# Amazon KDP Production Engine

Automated, testable production of original children's coloring-book paperbacks for Amazon KDP.

## Production profile

- Audience: ages 4–8.
- Themes: fruits, flowers, general toys, birds, animals, and children's professions.
- Trim: 8.5 × 11 in.
- Interior: black ink on white paper, no bleed.
- One design on each odd-numbered right-hand page; every even-numbered reverse page is completely blank.
- Raster artwork: at least 300 DPI.
- Line art: 2.4 pt project target; never below KDP's 0.75 pt minimum.
- Sample: 24 pages / 12 illustrations.
- Standard production target: 100 pages / 50 illustrations. The production profile requires 50 approved, distinct original assets; the built-in generator will not repeat its 12 review motifs to pad a book.
- Full-wrap cover: calculated from selected paper, page count, trim, and 0.125 in outside bleed; CMYK vector colors, embedded fonts, and no PDF metadata.
- No automatic publishing. Owner approval and KDP Print Previewer review are mandatory.

## Main components

- config/book_meta.json: exact sample book configuration.
- config/series_defaults.json: standard 100-page series target.
- config/themes.json and config/series_templates/: six theme definitions and ready-to-edit 24-page templates.
- config/production_policy.json: machine-readable production constitution.
- docs/BOOK_PRODUCTION_CONSTITUTION.md: mandatory originality, design, and release rules.
- docs/KDP_TECHNICAL_SPECIFICATION.md: official requirements vs market observations.
- docs/DEPENDENCY_AUDIT.md: pinned GitHub-sourced libraries, licenses, and security review.
- scripts/art_generator.py and scripts/theme_art.py: create original, deterministic line art for all six requested themes.
- scripts/artwork_loader.py: loads rights-cleared assets, flattens them to pure black/white, and rejects exact duplicates.
- scripts/interior_builder.py: builds the single-sided interior PDF.
- scripts/cover_calculator.py: computes paper-specific spine and full-wrap dimensions.
- scripts/cover_builder.py: builds a full-wrap PDF with embedded fonts.
- scripts/validator.py: checks page count, geometry, blank reverse pages, effective DPI, transparency, and embedded fonts.
- scripts/pipeline.py: one-command build and preflight.
- scripts/kdp_inspector.py: diagnoses GitHub Actions failures.
- scripts/repair_engine.py: applies only exact, hash-guarded allowlisted repairs.
- scripts/intervention_controller.py: resumes failed jobs only after explicit owner approval.

## Run locally

Install pinned dependencies:

    python -m pip install -r requirements.txt

Build the 24-page review sample:

    python -m scripts.pipeline --config config/book_meta.json --output-dir build/output

Run tests:

    python -m unittest discover -s tests -t . -v

## GitHub Actions

- KDP Production Pipeline builds the PDFs, validates them, and uploads an artifact.
- KDP Self-Healing Inspector reads failed workflow logs, classifies errors, retries only bounded transient failures, and opens a human-intervention issue when a decision is needed.
- KDP Intervention Queue exposes a manual Run Workflow button and checks owner-approved intervention issues every six hours. The approved-to-resume label is explicit authorization; without it, the queue does not rerun failed jobs.
- Inspector Tests runs regression tests on changes.

## Important limits

A successful preflight is not an Amazon approval. The sample must be visually inspected and passed through KDP Print Previewer. Confirm actual AI-generated content disclosure, metadata, rights, categories, keywords, and publishing rights in KDP. Never publish without explicit owner approval.
