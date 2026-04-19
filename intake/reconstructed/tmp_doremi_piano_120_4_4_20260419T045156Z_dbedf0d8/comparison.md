target_analysis_path: /workspace/midi-renderer/intake/analysis/tmp_doremi_piano_120_4_4_20260419T045156Z_dbedf0d8.analysis.json
generated_render_path: /workspace/midi-renderer/intake/reconstructed/tmp_doremi_piano_120_4_4_20260419T045156Z_dbedf0d8/render.yaml
generated_meta_path: /workspace/midi-renderer/intake/reconstructed/tmp_doremi_piano_120_4_4_20260419T045156Z_dbedf0d8/meta.yaml
comparison_mode: song_intent
used_song_intent_path: /workspace/midi-renderer/intake/song_intent/doremi_piano_120_4-4.song_intent.yaml

short_summary: Generated reconstruction artifacts with intent-aware comparison fallback when canonical reference is absent.

obvious_matches:
- song_intent: tempo is close to intended (120.0 vs 120)
- song_intent: meter matches intended (4/4)
- song_intent: right-hand melody intent acknowledged in comparison
- song_intent: left-hand accompaniment intent acknowledged in comparison
- song_intent: timing deviations treated as acceptable per timing_policy
- song_intent: instrument strictness relaxed per intent policy

obvious_differences:
- song_intent: phrase length likely differs (observed last-start-bar=15, intended=16)

unresolved_items:
- no finalize promotion to songs/
- no advanced semantic comparison scoring
- multi-instrument inference remains intentionally minimal
