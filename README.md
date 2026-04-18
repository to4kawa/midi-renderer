# Midi Renderer

## Project purpose
Midi Renderer is a Python-based execution foundation that accepts a YAML render specification and prepares a pipeline for future MIDI file generation.

## Bootstrap scope
This bootstrap includes only the minimal skeleton:
- repository structure
- YAML loading and basic validation
- timing parser skeleton
- renderer/writer placeholders
- tests for wiring and core contracts

This stage intentionally excludes real song data and production-quality MIDI generation.

## Repository structure
```text
.
├── docs/
│   └── render_spec.md
├── scripts/
│   └── run_render.py
├── songs/
│   └── .gitkeep
├── src/
│   └── midi_renderer/
│       ├── __init__.py
│       ├── loader.py
│       ├── renderer.py
│       ├── resolver.py
│       ├── timing.py
│       ├── validator.py
│       └── writer.py
└── tests/
    ├── integration/
    │   └── test_bootstrap_execution.py
    └── unit/
        ├── test_loader.py
        ├── test_timing.py
        └── test_validator.py
```

## Execution flow
1. `scripts/run_render.py` receives a `render.yaml` path.
2. `loader` reads `render.yaml` safely.
3. `validator` checks required shape and fields.
4. `renderer` builds a placeholder internal render result.
5. `writer` emits a placeholder output artifact.

## Current limitations
- No real MIDI byte writing yet.
- GM resolution is a placeholder.
- Validation is intentionally minimal and structural.
- `meta.yaml` support is optional and not required at bootstrap.

## Next step
Add a real song render spec under `songs/<song_id>/render.yaml`, expand validation semantics, and replace placeholder writing with real MIDI output.
