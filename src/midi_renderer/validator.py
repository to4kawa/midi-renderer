from __future__ import annotations

from typing import Any


class ValidationError(ValueError):
    """Raised when the render spec fails bootstrap validation."""


REQUIRED_TOP_LEVEL_FIELDS = (
    "schema_version",
    "song_ref",
    "format",
    "transport",
    "tracks",
    "notes",
)


REQUIRED_TRANSPORT_FIELDS = (
    "bpm",
    "ppq",
    "time_signature",
)


def validate_render_spec(spec: dict[str, Any]) -> None:
    missing = [key for key in REQUIRED_TOP_LEVEL_FIELDS if key not in spec]
    if missing:
        raise ValidationError(f"Missing required top-level fields: {', '.join(missing)}")

    if not isinstance(spec["transport"], dict):
        raise ValidationError("'transport' must be a mapping")

    missing_transport = [key for key in REQUIRED_TRANSPORT_FIELDS if key not in spec["transport"]]
    if missing_transport:
        raise ValidationError(
            "Missing required transport fields: " + ", ".join(missing_transport)
        )

    if not isinstance(spec["tracks"], list):
        raise ValidationError("'tracks' must be a list")

    if not isinstance(spec["notes"], list):
        raise ValidationError("'notes' must be a list")
