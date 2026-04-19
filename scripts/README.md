# scripts/

`scripts/` is reserved for operational entrypoints and thin wrappers.

- Keep script files focused on CLI execution flow.
- Put reusable implementation logic in `src/`, not in `scripts/`.
- Avoid embedding core parser/analyzer business logic directly in wrapper scripts.
