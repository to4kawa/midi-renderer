# Reconstruction Workflow (Bootstrap render.v0.1)

This step provides a minimal reconstruction path:

`analysis.v0.1 JSON -> render.yaml + meta.yaml` (default)

## Scope in this phase

- Input: one `analysis.v0.1` JSON.
- Optional inputs:
  - reference song directory (`render.yaml` + `meta.yaml`)
  - `song_intent` YAML/JSON
- Output is trial artifact only (bootstrap render, not normalized/final):
  - `intake/reconstructed/<temporary_id>/`
- No finalize promotion

## Run

```bash
python scripts/reconstruct_from_analysis.py [analysis_json_path] \
  [--reference-song-path <songs/...>] \
  [--song-intent-path <path/to/song_intent.yaml>] \
  [--with-comparison]
```

- If `analysis_json_path` is omitted, latest `intake/analysis/*.analysis.json` is used.
- If `--reference-song-path` is omitted, the tool tries to infer a song ref from `temporary_id`; if no matching `songs/<song_ref>` exists, reference comparison is skipped.
- `--song-intent-path` is optional.
- `--with-comparison` is optional. Without this flag, `comparison.md` is not generated.

## Comparison mode (optional artifact)

When `--with-comparison` is enabled, input priority is:
1. explicit/inferred reference song path (when available)
2. song_intent path (when available)
3. unavailable mode when neither exists

`comparison_mode` values:
- `reference_song`
- `song_intent`
- `reference_song+song_intent`
- `unavailable`
- `disabled` (default, when comparison output is skipped)

## Produced files

- `render.yaml`: execution-oriented reconstructed draft.
- `meta.yaml`: support metadata and review notes.
- `comparison.md`: optional comparison memo, generated only with `--with-comparison`.

## Notes

- `render.yaml` is a bootstrap execution spec (`schema_version: render.v0.1`) and uses observed notes as source of truth.
- Missing/non-observed facts are written as provisional or unresolved in `meta.yaml` and (optionally) `comparison.md`.
- This phase intentionally avoids advanced semantic understanding (e.g., section/chord interpretation); those are future tasks.
