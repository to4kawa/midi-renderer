# Render Spec (Bootstrap)

## Overview
The primary contract is `songs/<song_id>/render.yaml`. This document defines the minimum expected shape for bootstrap-stage development. The active bootstrap render flow writes real MIDI (`.mid`) output.

## Primary input file: render.yaml
- Stable required path pattern: `songs/<song_id>/render.yaml`
- Stable optional sibling path: `songs/<song_id>/meta.yaml` (not required in bootstrap)

## Required top-level fields
A render spec must include:
- `schema_version`
- `song_ref`
- `format`
- `transport`
- `tracks`
- `notes`

Bootstrap reconstruction currently writes `schema_version: render.v0.1` and `format: bootstrap`.
This indicates an observed-faithful trial spec for regeneration, not a normalized/final render contract.

## Transport fields
Bootstrap expects transport to be a mapping with at least:
- `bpm`
- `ppq`
- `time_signature`

## Track fields
`tracks` must be a list. Track item structure is intentionally minimal at this stage, but each item should be an object suitable for future expansion.

## Note fields
`notes` must be a list. Note-level schema is not finalized yet, but timing fields are expected to eventually use `bar:beat:tick` notation.

## bar:beat:tick notation
Timing strings follow this pattern:
- `bar:beat:tick`
- each segment is a non-negative integer
- example: `1:1:0`

## Validation expectations
Bootstrap validation focuses on structure and required keys:
- required top-level keys must exist
- `transport` must be an object
- `tracks` must be a list
- `notes` must be a list

Semantic checks (musical correctness, value ranges, channel/program constraints) are intentionally deferred.
