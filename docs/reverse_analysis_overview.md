# Reverse Analysis Overview (Current Focus)

This project is currently focused on **reverse-analysis**, not on expanding render-side features.

## Goal

Current target pipeline:

`MIDI -> analysis JSON -> render.yaml + meta.yaml`

The intent is to inspect incoming MIDI files, capture analysis output in a provisional JSON form, and reconstruct final design artifacts.

## Workflow Stages

1. **intake**
   - Accept MIDI inputs and assign temporary handling IDs.
   - Intake must not determine a final `song_id`.
2. **analyze**
   - Extract observed facts first (initially tempo-centered), plus inferred/unknown fields.
3. **reconstruct**
   - Transform analysis outputs into draft render design data.
4. **finalize**
   - Promote only final `render.yaml` and optional `meta.yaml`.
5. **cleanup**
   - Close temporary working state while preserving analysis history as needed.

## Scope Note

At this stage, only repository structure and static draft documentation are being prepared. Full parser/analyzer/finalize logic is intentionally deferred.
