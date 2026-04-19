# Operation Flow

## Bootstrap render execution path
1. Provide the target render spec path (`songs/<song_id>/render.yaml`).
2. Run `scripts/run_render.py` with the render spec and optional `--output` path.
3. Loader reads YAML (`load_render_spec`).
4. Validator performs bootstrap structural checks (`validate_render_spec`).
5. Renderer produces the render result (`render`).
6. Writer emits MIDI artifact (`write_midi_output`).

## Canonical command
```bash
python scripts/run_render.py songs/<song_id>/render.yaml --output out/<song_id>/render_result.mid
```

## Expected success signal
- Exit code `0`
- Console message prefix: `[bootstrap-render] wrote:`
- Output artifact exists at the supplied `--output` path
- Output artifact is non-empty
- Output artifact header starts with `MThd`
