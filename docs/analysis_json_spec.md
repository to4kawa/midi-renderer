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
