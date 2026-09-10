# Navier–Stokes Physical Approximation

Numerical and physical investigation of finite, realizable approximations to the September 2026 smooth-forcing finite-time blowup construction for the three-dimensional incompressible Navier–Stokes equations.

## Research goal

The project does **not** attempt to re-prove the mathematical theorem.

Its central question is:

> **How much of the mathematical concentrating mechanism survives when the infinite, exact construction is replaced by finite resolution, finite scale separation, finite forcing precision, and a real fluid?**

In particular, the project will investigate:

- finite truncations of the concentrating vortex;
- the Navier–Stokes residual of those truncations;
- the averaged Reynolds stress required in the transition region;
- whether resolved oscillatory disturbances can generate that stress;
- sensitivity to amplitude, phase, timing, noise, viscosity, and truncation;
- how many decades of spatial concentration and velocity amplification can be achieved;
- where water, air, or other fluids depart from the incompressible-continuum model;
- whether a laboratory forcing mechanism could reproduce the essential dynamics.

## Source paper

**Finite Time Blowup for Navier–Stokes**  
OpenAI preprint, September 2026

Paper:

https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf

Overview:

https://openai.com/index/navier-stokes-solution/

The paper itself is the mathematical source of truth. Exact formulas implemented in code should be mapped to paper equation numbers in `notes/equation-map.md`.

## Project documents

The repository begins with three important guidance files:

- `README.md` — overview of the project;
- `RESEARCH_CONTEXT.md` — scientific context, rationale, fluid choices, hardware, and longer-term questions;
- `PROJECT.md` — implementation plan, numerical stages, testing requirements, and coding-agent instructions;
- `INITIAL_PROMPT.md` — suggested first instruction for Codex Local.

New contributors or coding agents should read them in that order:

1. `README.md`
2. `RESEARCH_CONTEXT.md`
3. `PROJECT.md`
4. `INITIAL_PROMPT.md`

## Initial computational strategy

The project starts deliberately small.

### Phase 1

Reconstruct the published concentrating core and similarity-coordinate geometry.

### Phase 2

Implement and validate cylindrical-axisymmetric differential operators.

### Phase 3

Compute the finite-truncation Navier–Stokes residual,

\[
R =
\partial_t u
+
(u\cdot\nabla)u
-
\nu\Delta u
+
\nabla p.
\]

### Phase 4

Determine the averaged Reynolds-stress contribution required to cancel the transition-region residual.

### Phase 5

Replace the prescribed stress with one or more resolved oscillatory disturbances.

### Phase 6

Perform robustness experiments with controlled errors and noise.

Only after these stages are understood should the project move to substantial 3-D DNS.

## Primary hardware

Initial development and simulation are intended to run locally on:

- Intel Core i7-14700F
- 16 GB system RAM
- NVIDIA GeForce RTX 4060 Ti, 8 GB VRAM
- Windows 11
- WSL2 Ubuntu

The early code should be CPU-first, double-precision, and easy to validate.

GPU acceleration may be added later.

Large 3-D DNS and broad parameter sweeps may eventually move to native-Linux cloud GPU resources.

## Default physical reference

The first dimensional reference fluid is **water**.

Water is favored initially because it is inexpensive, transparent, approximately Newtonian, has relatively low kinematic viscosity, and is compatible with optical diagnostics.

Air and liquid gallium are retained as comparison fluids.

The PDE implementation should remain nondimensional for as long as practical; dimensional fluid properties should be handled separately.

## Core metrics

Useful outcomes are quantitative rather than binary.

Important measurements include:

\[
r_{\rm core}(t),
\qquad
U_{\max}(t),
\qquad
\omega_{\max}(t),
\qquad
E(t).
\]

Derived measures include spatial concentration,

\[
C_r =
\frac{r_{\rm initial}}{r_{\min}},
\]

velocity amplification,

\[
C_u =
\frac{U_{\max}}{U_{\rm initial}},
\]

and the fitted scaling relationship between velocity and core size.

Resolved nonlinear stresses should also be compared quantitatively with the target stress required by the finite model.

## Reproducibility

Every substantive numerical run should record:

- Git commit;
- configuration;
- date;
- machine and GPU;
- numerical precision;
- grid;
- time-step strategy where applicable;
- important solver tolerances;
- final metrics;
- stopping reason.

Large field output should not be committed to Git.

## Philosophy

This is a research code, not a general-purpose CFD package.

Prefer:

- explicit equations;
- small understandable modules;
- independent tests;
- convergence studies;
- dimensional checks;
- negative results preserved rather than hidden;
- quantitative diagnostics before attractive animations.

Avoid premature optimization and premature 3-D complexity.

A finite approximation that ultimately fails can still be scientifically valuable if we can measure **how** and **where** it fails.

## First-pass implementation

The first-pass code implements the paper's **explicit Appendix B comparison**,
similarity geometry, and tested cylindrical divergence. It does **not** yet
implement the nonlinear core or its momentum
residual. See [first-pass findings](notes/experiment-log.md),
[equation map](notes/equation-map.md), and
[numerical method](notes/numerical-method.md) for the exact scope and limitations.

Run in WSL2 Ubuntu with Python 3.11 or newer (the local environment uses 3.12):

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
pytest
python scripts/environment.py
python scripts/plot_profiles.py
```

For the already configured workspace, start with `source .venv/bin/activate`.
The plot driver reads [configs/nondimensional.yaml](configs/nondimensional.yaml)
and creates a new timestamped directory under `results/`, containing seven plots
and a JSON summary with configuration, metrics, convergence, hardware, versions,
and source hashes. Use `--config` and `--output` to specify alternatives; output
directories must not already exist. Generated results are ignored by Git.
The selected baseline plots and summary in
[results/core-comparison](results/core-comparison) are an explicit exception
and are published with the repository; temporary runs remain ignored.
The optional `paper` dependency group adds `pypdf` for reading the source PDF;
it is not needed for numerical runs. No GPU software is required.

## Relaxed scheduled-pressure experiment

The third milestone additionally implements the complete Appendix A scheduled
pressure integral (A.21), its first two eta derivatives, Z_star, and the first
explicit axial correction in (B.13). **This is a relaxed-hierarchy experiment,
NOT theorem-admissible, and not a nonlinear core solution.** The original
comparison implementation and published baseline are unchanged.

```bash
python scripts/relaxed_pressure.py
```

The [finite-family config](configs/relaxed_not_theorem_admissible.yaml) runs
five cases, recording stage joins, Q stopping, pressure quadrature refinement,
derivative convergence, scale separation and CPU provenance. Outputs require
a new directory. The selected reference
[summary](results/relaxed_not_theorem_admissible_reference/relaxed_not_theorem_admissible_summary.json),
[pressure plot](results/relaxed_not_theorem_admissible_reference/relaxed_not_theorem_admissible_pressure.png),
[first-correction plot](results/relaxed_not_theorem_admissible_reference/relaxed_not_theorem_admissible_correction.png),
and [log-schedule plot](results/relaxed_not_theorem_admissible_reference/relaxed_not_theorem_admissible_log_schedule.png)
are explicit version-control exceptions alongside the comparison baseline.

Result: modest first corrections are accessible after pressure-amplitude
compression, but retained radial schedules still span 141-196 decades in X.
See the [third-milestone report](notes/experiment-log.md#third-milestone-relaxed-scheduled-pressure-2026-09-10-utc).
Work stops for scientific review before any nonlinear (B.15) solve.

## Schedule compression and sacrifice audit

The fourth milestone preserves the relaxed reference and adds a separate
**compressed, NOT theorem-admissible** length-only model. The
[source audit](notes/compression-audit.md) distinguishes bump-support minima,
moment and stress estimates, and reserved regions for later corrections.

```bash
python scripts/compressed_not_theorem_admissible.py
```

The [config](configs/compressed_not_theorem_admissible.yaml) runs ten
one-at-a-time changes and three combined candidates. Radius separation falls
from 70.44 to 8.78 decades with about 1.5e-11 relative change in Z_star,
but substantial support and slope guarantees are sacrificed. Q matching
remains conditional on prescribed moment data, not verified global moments.
Three radius decades are blocked by the unchanged early stages alone.
See the [fourth-milestone report](notes/experiment-log.md#fourth-milestone-schedule-compression-2026-09-10-utc)
and its linked plots, condition table and reference summary. No nonlinear
solve, dynamical concentration, or physical realizability is claimed.

## Fifth milestone: failed local-core acceptance gate

The source-grounded nonlinear B.15 diagnostic is implemented, but **no
nonlinear core solution is accepted**. At Lambda512, g_peak=.1 and
sigma_star=.2, the initial aggressive-datum iteration settles while axial
and pressure residuals fail refinement. The narrow g^2 source is unresolved,
and the finite sigma choice also fails the quantitative B.2 partition audit.
No stronger-swirl or Lambda128 continuation was attempted.

```bash
OPENBLAS_NUM_THREADS=1 python scripts/core_not_theorem_admissible.py
```

See the [fifth-milestone report](notes/experiment-log.md#fifth-milestone-core-only-nonlinear-diagnostic-2026-09-10-utc)
and [bounded config](configs/core_not_theorem_admissible.yaml). The report
preserves failed residuals, derivative changes, initialization checks and
plots. All models remain NOT theorem-admissible. Recommended next gate:
improve the local solver, then reassess this same initial case.

## Sixth milestone: source resolved, endpoint iteration fails

The [same-tuple representation study](notes/experiment-log.md#sixth-milestone-same-tuple-source-resolution-2026-09-10-utc)
passes the exact-source convergence gate at 2049 eta points and uses
p=g^2 Pbar with analytic derivatives of g^2. All model parameters and
the original pressure datum are unchanged. Matrix-free Chebyshev transforms
avoid dense high-order eta matrices.

Both initial guesses then lose fixed-point convergence through endpoint
growth and propose nonpositive Phi. **No core is accepted.** Later radial
and combined refinement stages were not run after the required stop.
The report separates numerical instability from the unchanged sigma/B.2
mismatch. It recommends improving the local method again, not a claim
that the finite core cannot exist. All models remain NOT theorem-admissible.

```bash
OPENBLAS_NUM_THREADS=1 python scripts/core_representation_not_theorem_admissible.py
```
