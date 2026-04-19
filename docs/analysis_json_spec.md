# Analysis JSON Spec (Provisional Draft)

> Status: **Provisional**. This is a minimal draft for first reverse-analysis iterations.

Purpose: capture structured analysis output between intake and reconstruction.

## Conceptual Sections

- `schema_version`
  - Version marker for this analysis JSON schema draft.
- `analysis_id`
  - Unique identifier for one analysis result.
- `temporary_id`
  - Intake-time temporary identifier (not final `song_id`).
- `source`
  - Input source information (e.g., MIDI file path, file hash, ingest timestamp).
- `observed`
  - Direct observations from MIDI parsing/inspection (tempo-centered first).
- `inferred`
  - Derived assumptions computed from observed facts.
- `unknown`
  - Known unknowns and deferred fields requiring later resolution.
- `quality`
  - Confidence/quality indicators and notable caveats.
- `provenance`
  - Traceability metadata (tool version, run context, timestamps, operator notes).

## Practical Notes

- Early outputs are expected to be unstable.
- Retention policy should favor append/preserve rather than overwrite/delete.
- Actual field shape and constraints will be refined after first real outputs are produced from real MIDI inputs.

## Current Provisional Schema Shape (`analysis.v0.1`)

- `schema_version`: `analysis.v0.1`
- `observed.note_events[]`
  - `track_index` (renamed from `track`)
  - `pitch` (renamed from `note`)
  - `channel`, `start_tick`, `end_tick`, `duration_ticks`, `velocity`
- `unknown`
  - `fields: string[]` (simplified from `deferred_fields`)
- `quality`
  - `status`
  - `warnings`
  - `lossy_points` (MIDI-only reverse analysis limitations)
- `provenance`
  - `generated_at_utc`
  - `generator`
  - `generator_version`
  - `mode`

## Compatibility Notes

- `0.1.0-provisional` から `analysis.v0.1` へ識別子を更新。
- `observed.note_events[]` は `track` / `note` を廃止し、`track_index` / `pitch` を使用。
- `unknown.deferred_fields` は `unknown.fields` へ統一。
- `quality.lossy_points` と `provenance.generator_version` を追加。
- `observed` / `inferred` / `unknown` / `quality` / `provenance` の責務分離は継続。
