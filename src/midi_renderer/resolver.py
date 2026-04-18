from __future__ import annotations


def resolve_gm_program(program_hint: str | int | None) -> int | None:
    """Placeholder GM resolver.

    Future implementation may accept named instruments and map to GM program numbers.
    """
    if program_hint is None:
        return None
    if isinstance(program_hint, int):
        return program_hint
    return None
