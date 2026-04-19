# Repository Structure

This document defines the current directory responsibilities for `midi-renderer`.

## Canonical vs Local Roles

- **GitHub repository (canonical):** source of truth for code, docs, specs, and tests.
- **Codex local environment:** execution workspace for local intake handling, MIDI processing, and analysis JSON generation.

## Top-Level Directories

- `docs/`
  - Project documentation, flow definitions, and provisional specs.
- `scripts/`
  - Thin CLI/entrypoint wrappers only (operational glue).
- `src/midi_renderer/`
  - Reusable implementation logic.
  - Subpackages are split by pipeline concern:
    - `common/`
    - `intake/`
    - `analysis/`
    - `finalize/`
    - `cleanup/`
- `intake/`
  - Local working area for in-progress reverse-analysis inputs/state.
  - `intake/midi/`: source MIDI drops.
  - `intake/analysis/`: provisional analysis outputs.
  - `intake/state/`: temporary state and tracking data.
- `songs/`
  - Song-level artifacts and finalized design outputs when promoted.

## Generated Artifact Policy

Generated outputs such as `songs/*/outputs/` are local-generated artifacts and are normally **not committed**.

The intended ignore policy for this path is local-only via `.git/info/exclude`, not shared `.gitignore`.
