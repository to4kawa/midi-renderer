from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def intake_root() -> Path:
    return repo_root() / "intake"


def intake_midi_dir() -> Path:
    return intake_root() / "midi"


def intake_analysis_dir() -> Path:
    return intake_root() / "analysis"


def intake_reconstructed_dir() -> Path:
    return intake_root() / "reconstructed"


def reference_neko_song_dir() -> Path:
    return repo_root() / "songs" / "neko_funjatta_test_piano_120"
