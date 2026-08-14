# ADR 0002: Target VitePress 1.6.x, track 2.0-alpha in CI

**Status:** accepted (2026-08-14)

## Decision

Generated config and the theme template target VitePress `^1.6.4` (npm
`latest`). A non-blocking CI job builds against `vitepress@next`
(2.0.0-alpha) so breakage is visible early.

## Rationale

- 1.6.4 is what DocumenterVitepress.jl pins and what the ecosystem runs.
- 2.0 is alpha (2.0.0-alpha.19 as of 2026-08) and requires Node ≥ 22;
  config churn is expected until it stabilizes.

## Revisit

When VitePress 2.0 reaches stable, flip the default and keep 1.6 in the
compat matrix for one release cycle.
