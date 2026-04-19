# Reconstruction Workflow (Minimal: Cat 1-case)

This step adds a minimal reconstruction path:

`analysis.v0.1 JSON -> render.yaml + meta.yaml + comparison.md`

## Fixed scope in this phase

- One input only (cat / neko first pass)
- Fixed comparison reference:
  - `songs/neko_funjatta_test_piano_120`
- Output is trial artifact only:
  - `intake/reconstructed/<temporary_id>/`
- No finalize promotion

## Run

```bash
python scripts/reconstruct_from_analysis.py [analysis_json_path]
```

- If `analysis_json_path` is omitted, latest `intake/analysis/*.analysis.json` is used.

## Produced files

- `render.yaml`: execution-oriented reconstructed draft.
- `meta.yaml`: support metadata and review notes.
- `comparison.md`: short memo against fixed canonical reference.

## Notes

- `render.yaml` uses observed notes as source of truth.
- Missing/non-observed facts are written as provisional or unresolved in `meta.yaml` / `comparison.md`.
- This phase intentionally uses a simple fixed mapping (single piano track).
