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

The current code implements the paper's **explicit Appendix B comparison**,
similarity geometry, and tested cylindrical divergence. It does **not** yet
implement the nonlinear core, its exterior pressure datum, or its momentum
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
The optional `paper` dependency group adds `pypdf` for reading the source PDF;
it is not needed for numerical runs. No GPU software is required.
