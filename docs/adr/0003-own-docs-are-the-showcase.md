# ADR 0003: The project's own docs are the showcase; the demo is a test fixture

**Status:** accepted (2026-08-14)

## Decision

`docs/` is built with this package's own builder and is what gets deployed.
The small `vpdemo` package moved to `tests/demo/` and exists only as a test
fixture.

## Rationale

Both roles were originally filled by `demo/`, which made the repository read as
if the example were the product. Now:

- `docs/` proves the builder on real content: hero landing page, nav
  dropdowns, admonitions, math, and an API reference generated from this
  package's own docstrings with source badges. If the builder breaks, the
  project's own site breaks.
- `tests/demo/` can stay deliberately hostile (Vue mustaches, angle brackets,
  doctests, multi-parameter field lists) without that ugliness being the first
  thing a visitor sees.

## Consequences

- The docs workflow deploys `docs/`.
- Rendering fixes get their regression case in `tests/demo/`, not in `docs/`.
