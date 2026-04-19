# Reconstruction Workflow (Minimal: reference optional + intent-aware comparison)

This step provides a minimal reconstruction path:

`analysis.v0.1 JSON -> render.yaml + meta.yaml + comparison.md`

## Scope in this phase

- Input: one `analysis.v0.1` JSON.
- Optional inputs:
  - reference song directory (`render.yaml` + `meta.yaml`)
  - `song_intent` YAML/JSON
- Output is trial artifact only:
  - `intake/reconstructed/<temporary_id>/`
- No finalize promotion

## Run

```bash
python scripts/reconstruct_from_analysis.py [analysis_json_path] \
  [--reference-song-path <songs/...>] \
  [--song-intent-path <path/to/song_intent.yaml>]
```

- If `analysis_json_path` is omitted, latest `intake/analysis/*.analysis.json` is used.
- If `--reference-song-path` is omitted, the tool tries to infer a song ref from `temporary_id`; if no matching `songs/<song_ref>` exists, reference comparison is skipped.
- `--song-intent-path` is optional.

## Comparison input priority

1. explicit/inferred reference song path (when available)
2. song_intent path (when available)
3. unavailable mode when neither exists

`comparison_mode` values:
- `reference_song`
- `song_intent`
- `reference_song+song_intent`
- `unavailable`

## Produced files

- `render.yaml`: execution-oriented reconstructed draft.
- `meta.yaml`: support metadata and review notes.
- `comparison.md`: comparison memo with required minimum sections.

## Notes

- `render.yaml` uses observed notes as source of truth.
- Missing/non-observed facts are written as provisional or unresolved in `meta.yaml` / `comparison.md`.
- This phase intentionally keeps track inference simple (single piano-like track).
