# Artwork Generation Specification

**ID:** KDP-ARTWORK-SPEC-1.0  
**Status:** Active design standard; visual approval remains mandatory  
**Applies to:** Original children's coloring-book artwork, ages 4–8  
**First pilot:** Fruit Friends (12-page review sample)

## 1. Purpose and boundaries

This specification defines the visual, technical, originality, and review contract for every coloring-page illustration. It is an internal production standard, not an Amazon guarantee. It does not change the currently passing PDF geometry or publishing workflow.

The pilot is limited to improving and reviewing the 12 Fruit Friends motifs. It does **not** authorize production of the 50-artwork / 100-page commercial edition.

## 2. Immutable page-art output contract

| Attribute | Required value |
|---|---|
| Canvas | 2550 × 3300 px |
| Resolution metadata | 300 DPI minimum |
| Color mode | RGB or grayscale source; final normalized output pure black/white |
| Background | Uniform pure white (#FFFFFF) |
| Contours | Black (#000000), smooth, bold, closed wherever defining a coloring region |
| Nominal stroke | 2.4 pt at 300 DPI (10 px target); never below 0.75 pt |
| Composition | One dominant subject, or one simple coherent group |
| Audience | Ages 4–8 |
| Placement | Centered, balanced, fully inside the page safe area |
| Output | PNG, lossless, one design per file |

The page renderer remains responsible for placing the artwork within the existing 8.5 × 11 in no-bleed interior and for keeping even-numbered reverse pages completely blank.

## 3. Visual art direction

### 3.1 Shape language
- Use friendly, recognizable, age-appropriate proportions and clear silhouettes.
- Prefer broad curves and simple geometric construction over thin, intricate detail.
- Keep internal features large enough to color comfortably.
- Use a restrained number of secondary details; every detail must clarify the subject or add a useful coloring region.
- Maintain consistent contour weight across the page. Use hierarchy only where it improves legibility, not as a substitute for clean paths.

### 3.2 Coloring usability
- Enclose coloring regions with visibly connected contours.
- Avoid tiny islands, narrow channels, dense cross-hatching, stippling, and decorative micro-patterns.
- Do not use gray, gradients, shadows, hatching, halftones, textures, or filled black areas that dominate the page.
- Keep the silhouette and key features recognizable when viewed as a small thumbnail.
- Avoid accidental tangencies, self-intersections, awkward overlaps, and lines that stop just short of intended joins.

### 3.3 Composition and safe area
- Keep the complete subject inside an 8% canvas inset on all sides.
- Target a dominant subject bounding box occupying approximately 45–70% of the canvas area; this is an internal composition target, not a KDP rule.
- Preserve visible white space around the subject.
- No cropped leaves, stems, limbs, accessories, or other subject parts.
- Background accents are optional and must remain sparse, large, and subordinate.

## 4. Originality, rights, and safety
- Depict generic subject matter only; do not imitate a known character, franchise, branded toy, logo, packaging, signature illustration style, or specific artist.
- Do not trace, scrape, or adapt unlicensed web images.
- Record the creation method, source assets, tool/model (if used), generation date, and applicable commercial-use terms for every accepted asset.
- Reject artwork with watermarks, signatures, brand marks, text artifacts, or unexplained third-party elements.
- Human reviewer must assess similarity against the other pages in the same book and the existing catalog. Pixel hashes only detect exact duplicates; they do not prove visual uniqueness.
- Publisher must determine and answer KDP's AI-generated-content disclosure based on the actual creation process.

## 5. Standard generation brief

Use this as the controlled brief for any drawing or image-generation implementation:

> Create one original black-and-white coloring-book illustration for children ages 4–8. Subject: [EXACT SUBJECT]. Show one clear, friendly, instantly recognizable subject in a balanced centered composition. Use clean, smooth, bold black outlines on a pure white background; target a consistent 2.4 pt contour at 300 DPI. Close the contours that define coloring areas. Make the coloring regions large and open, with only a few large, meaningful interior details. Keep the entire subject inside an 8% safe inset and leave generous white space around it. No color, gray, shading, gradients, shadows, texture, hatching, halftones, lettering, numbers, watermark, border, logo, trademark, copyrighted character, branded product design, or background scene. Do not crop any part. Output a single flat page illustration, not a mockup, book cover, collage, or multi-panel sheet.

The exact subject must be substituted from the approved subject manifest. Do not ask a model to create several pages in one image.

## 6. Fruit Friends pilot application

The pilot contains these 12 distinct subjects. Each must have a visibly different silhouette and a composition specific to the subject; changing only a leaf, facial expression, or small accessory does not count as a distinct design.

| # | Subject | Pilot-specific composition guidance |
|---:|---|---|
| 1 | Apple | Broad rounded body, clear top cleft, short stem, one large leaf |
| 2 | Banana | Single curved banana with both ends visibly capped; one continuous, closed outer contour |
| 3 | Orange | Near-circular fruit with a small stem and leaf; avoid tiny peel dots |
| 4 | Pear | Narrow neck and wider lower body; clear stem and leaf |
| 5 | Grapes | Compact bunch of large, clearly separated grape forms; avoid tiny overlapping circles |
| 6 | Watermelon | One large wedge with a closed rind boundary and a small number of large seeds |
| 7 | Strawberry | Broad heart-like silhouette, leafy crown, sparse large seed marks |
| 8 | Pineapple | Oval body with a clearly closed outer contour; simplified broad diagonal lattice, not a dense grid; distinct crown leaves |
| 9 | Lemon | Elongated oval with two clear end points and one leaf; avoid detached contour fragments |
| 10 | Cherries | Two large cherries with closed bodies, two readable stems, and one leaf |
| 11 | Peach | Rounded body with a clear shallow cleft; minimal seam and one leaf |
| 12 | Avocado | Distinct pear-like outer silhouette and one large pit; avoid tiny internal details |

### Pilot acceptance rule
The pilot is accepted only when all 12 files pass the technical checks and a human reviewer approves every page at full page size and thumbnail size. Any failed page is revised individually; it is not silently replaced with a duplicate or padded with extra motifs.

## 7. Quality gates

### Gate A — automated technical checks
- Exact expected dimensions and resolution metadata.
- Monochrome source; final normalized image contains only black and white pixels.
- No alpha/transparency after normalization.
- Non-empty artwork and no content outside the safe inset.
- Minimum effective line width target is met by the generation method; image-level DPI alone cannot prove stroke width.
- File opens cleanly and can be embedded in the existing PDF pipeline.
- Exact duplicate detection passes.

### Gate B — human visual review (required)
Score each criterion Pass / Revise / Reject:
1. Recognizable subject at thumbnail size.
2. Clean, closed outer silhouette and intended internal contours.
3. Consistent bold line weight with no broken or doubled strokes.
4. Large, useful coloring regions suitable for ages 4–8.
5. Balanced scale, centering, and white space.
6. No clipping, tangencies, accidental intersections, or confusing overlaps.
7. Originality and rights provenance acceptable.
8. Distinct from all other pages in the volume and the catalog.

A page with any Reject fails. A page with any Revise cannot enter an approved asset set until revised and re-reviewed. Human review is not replaced by a similarity score.

## 8. Asset record

Every approved file must have a record containing:
- `asset_id`, `theme`, `subject`, `file_path`, `sha256`
- `canvas_px`, `dpi`, `line_width_target_pt`
- `creation_method`, `tool_or_model` (if applicable), `created_at`
- `rights_basis`, `source_references`
- `review_status`, `reviewer`, `reviewed_at`, `review_notes`
- `ai_generated` (true / false / unknown)

Unknown rights or creation provenance blocks approval. Do not infer AI disclosure from file metadata.

## 9. Release and rollback
- Existing production scripts, PDF dimensions, margins, blank reverse pages, and validation gates remain unchanged during the visual pilot.
- Store pilot outputs separately from approved production assets until all 12 pass human review.
- Never overwrite an approved asset in place; create a new version and retain its provenance.
- The 50-artwork / 100-page pipeline remains blocked until it receives exactly 50 approved, distinct assets and all release gates pass.
- A passing technical validator does not mean visual approval or KDP acceptance.

## 10. Change control
Any change to canvas size, DPI, line-width target, safe inset, normalization, or acceptance criteria must update this document and the machine-readable profile together. Changes to KDP requirements must be checked against current official KDP documentation and clearly labeled as official requirements, observed market patterns, or internal design choices.
