# Guide

The flux of a star with effective temperature $T$ is $F = \sigma T^4$.

```{note}
This page is authored in MyST markdown; the API reference is reStructuredText.
Both flow through the same builder.
```

```{warning}
Prose hazards ahead: {{ mustache }} text and a 1 < 2 comparison, all of which
must survive the VitePress build.
```

## Quick start

```python
from vpdemo import Simulation

sim = Simulation({"x": 128, "y": 128})
print(sim.n_cells)
```

## Units

| Quantity | Unit |
| -------- | ---- |
| Flux     | W m^-2 |
| Flux density | Jy |
