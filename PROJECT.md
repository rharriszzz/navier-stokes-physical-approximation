# Navier–Stokes Blowup Approximation Project

## Purpose

Build a transparent numerical research code to investigate physically realizable finite approximations to the recent smooth-forcing Navier–Stokes blowup construction.

The goal is **not** to reproduce the full proof or to prove blowup numerically.

The goal is to answer experimentally useful questions:

1. Can a finite, truncated portion of the concentrating flow be reproduced numerically?
2. What forcing or Reynolds-stress structure is required to sustain that concentration?
3. Can resolved oscillatory disturbances generate enough of that stress?
4. How sensitive is the concentration mechanism to amplitude, phase, position, viscosity, truncation, and random noise?
5. How many decades of spatial concentration and velocity amplification can be achieved before:
   - numerical resolution fails,
   - the constructed mechanism loses coherence,
   - or real-fluid effects such as cavitation, compressibility, or continuum breakdown would intervene?
6. Which practical fluid is most favorable for an eventual physical experiment?

Water is the first dimensional reference fluid. Air and liquid gallium should be retained as comparison fluids.

---

## Source paper

Use the actual current paper as the mathematical source of truth:

**Finite Time Blowup for Navier–Stokes**  
OpenAI preprint, released September 2026.

Paper:
https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf

OpenAI overview:
https://openai.com/index/navier-stokes-solution/

Do not infer exact formulas from summaries in this repository if they conflict with the paper.

Before implementing any analytic profile, forcing term, similarity coordinate, pulse, stress, cutoff, or scaling law, locate the corresponding equation in the paper and record its equation number in a source-code comment or in `notes/equation-map.md`.

The project is about a **finite approximation of the published construction**, not an independently invented blowup ansatz.

---

# Hardware and execution environment

Primary computer ("daisy"):

- CPU: Intel Core i7-14700F
- System RAM: 16 GB
- GPU: NVIDIA GeForce RTX 4060 Ti, 8 GB VRAM
- OS: Windows 11
- Preferred development environment: WSL2 Ubuntu
- Available disk space: roughly 446 GB at project start

Design the first stages to run comfortably on this machine.

Do not assume that large 3-D DNS will fit into 8 GB of VRAM.

Do not require cloud computing for the initial project.

Do not use nekRS locally at first. Current nekRS documentation does not list Microsoft WSL as a supported platform. A native-Linux cloud machine can be considered later if full 3-D DNS warrants it.

---

# Development philosophy

This is a scientific exploration, not a general-purpose CFD software project.

Prefer:

- short, readable modules;
- explicit equations;
- reproducible runs;
- unit tests;
- dimensional checks;
- convergence tests;
- plots that reveal failures;
- checkpointed scientific milestones.

Avoid initially:

- complicated GUI work;
- distributed computing;
- giant frameworks;
- premature optimization;
- full 3-D simulation before the axisymmetric mechanism is understood;
- hidden "magic" constants copied without references;
- turbulence models such as RANS or LES for the central mechanism.

For the early stages, direct numerical evaluation and axisymmetric computation are more valuable than a sophisticated production CFD package.

---

# Numerical precision

Use double precision (`float64`) by default.

The mechanism involves cancellation among terms and potentially large dynamic ranges. Do not silently use GPU `float32`.

If a GPU library defaults to single precision, explicitly enable 64-bit computation where supported.

Compare selected calculations against higher precision or independent formulations when cancellation becomes severe.

---

# Repository layout

Start with approximately:

```text
navier-stokes-blowup/
├── README.md
├── PROJECT.md
├── pyproject.toml
├── .gitignore
├── configs/
│   ├── nondimensional.yaml
│   ├── water.yaml
│   ├── air.yaml
│   └── gallium.yaml
├── notes/
│   ├── equation-map.md
│   ├── derivations.md
│   ├── numerical-method.md
│   └── experiment-log.md
├── src/
│   └── nsblowup/
│       ├── __init__.py
│       ├── coordinates.py
│       ├── profiles.py
│       ├── operators_axisymmetric.py
│       ├── residual.py
│       ├── stress.py
│       ├── pulses.py
│       ├── fluids.py
│       ├── metrics.py
│       ├── plotting.py
│       └── io.py
├── scripts/
│   ├── plot_profiles.py
│   ├── compute_residual.py
│   ├── stress_experiment.py
│   ├── pulse_experiment.py
│   └── convergence_test.py
├── tests/
│   ├── test_coordinates.py
│   ├── test_operators.py
│   ├── test_divergence.py
│   ├── test_scaling.py
│   └── test_residual.py
└── results/
    └── .gitkeep
```

Large numerical output should not be committed to Git.

Each actual run should have a machine-readable configuration and a small text/JSON summary sufficient to reproduce it.

---

# Stage 0 — Environment and reproducibility

Create a minimal Python environment that runs in WSL2.

Preferred initial dependencies:

- Python 3.11 or newer
- NumPy
- SciPy
- Matplotlib
- PyYAML
- pytest

Optional later:

- Numba for CPU acceleration
- JAX or PyTorch for GPU experiments
- h5py or zarr for larger results

Do **not** make JAX/PyTorch a requirement for the first working version.

Create a script that prints:

- Python version
- NumPy/SciPy versions
- CPU information if easily available
- detected CUDA/GPU status if applicable
- available RAM
- Git commit hash

Store these details with each substantial run.

Acceptance criterion:

```bash
pytest
```

passes from the repository root in WSL2.

---

# Stage 1 — Reconstruct the published concentrating core

## Objective

Implement the paper's leading concentrating/core velocity field and its similarity-coordinate transformation.

Do not integrate Navier–Stokes yet.

Extract the exact definitions from the source paper.

At minimum, identify and document:

- time-to-singularity variable;
- radial similarity coordinate;
- axial similarity coordinate;
- exponent(s), including the small parameter commonly denoted `h` if that is the paper's notation;
- leading radial velocity;
- leading azimuthal/swirl velocity;
- leading axial velocity;
- pressure term required at the same approximation level;
- region of validity of the inner/core approximation;
- transition/annular region;
- cutoffs.

Create `notes/equation-map.md` with entries like:

```text
Quantity | Paper equation | Code function | Notes
```

## Initial validation

For several decreasing values of time-to-singularity, plot:

- radial velocity;
- swirl velocity;
- axial velocity;
- speed;
- vorticity magnitude if available analytically/numerically.

Show the shrinking core on both:

1. physical coordinates;
2. similarity/rescaled coordinates.

The similarity-coordinate profile should remain approximately stationary if implemented correctly.

## Metrics

Track:

- core radius `r_core`;
- maximum speed `U_max`;
- maximum vorticity `omega_max`;
- kinetic energy in the modeled domain;
- divergence error.

Use a clearly documented operational definition of `r_core`, not visual judgment.

Possible definitions include:

- location of a characteristic swirl maximum;
- radius containing a specified fraction of a core integral;
- half-maximum radius.

Prefer the definition most naturally associated with the paper's profile.

---

# Stage 2 — Axisymmetric Navier–Stokes differential operators

Implement cylindrical-axisymmetric differential operators explicitly.

For velocity:

\[
u = (u_r, u_\theta, u_z)
\]

with no theta dependence in the background field.

Implement and test:

- divergence;
- gradient of pressure;
- vector Laplacian including cylindrical terms;
- convective acceleration including swirl terms;
- curl/vorticity.

Handle the axis `r = 0` analytically/symmetry-correctly. Do not use divisions by an arbitrary epsilon as the final implementation.

Create manufactured-solution tests for the operators independent of the blowup construction.

Acceptance criteria:

- known divergence-free test fields converge at the expected numerical order;
- operator errors decrease under grid refinement;
- axis handling does not produce NaN/Inf;
- reported convergence plots are saved.

---

# Stage 3 — Compute the Navier–Stokes residual of a finite truncation

For the approximate published velocity and pressure field, compute

\[
R =
\partial_t u
+ (u\cdot\nabla)u
- \nu\Delta u
+ \nabla p.
\]

Use nondimensional viscosity first, matching the paper's normalization exactly.

Separate the residual into components:

\[
R_r,\qquad R_\theta,\qquad R_z.
\]

Plot the residual spatially.

Important questions:

1. Is the residual concentrated primarily in the transition annulus as expected?
2. Which components dominate?
3. How does the residual scale as the singular time is approached?
4. How much cancellation occurs among the individual Navier–Stokes terms?
5. How sensitive is the computed residual to grid resolution?

Also plot individual term magnitudes:

- time derivative;
- advection;
- viscosity;
- pressure gradient;
- final residual.

This is essential because a tiny residual obtained by subtracting huge numbers may require more precision.

Acceptance criterion:

A documented, converged residual calculation whose localization and scaling can be compared directly with statements/equations in the paper.

---

# Stage 4 — Required averaged Reynolds stress

The paper uses oscillatory structures whose nonlinear products produce momentum transport in the transition region.

Before resolving those waves, model their **averaged Reynolds stress** directly.

Determine from the paper which stress components are required, likely involving quantities analogous to:

\[
\langle u_r' u_\theta' \rangle
\]

and

\[
\langle u_r' u_z' \rangle.
\]

Do not assume these exact forms without confirming the paper.

Construct the simplest stress tensor/divergence that cancels the relevant finite-truncation residual.

Then evaluate whether the background concentrating solution can be advanced or maintained when this stress is supplied.

This may initially be a diagnostic balance rather than a full time integration.

Questions:

- How large is the required stress relative to the background kinetic energy?
- Is it localized?
- Does it change sign?
- How rapidly does it vary?
- How accurately must it be supplied to maintain concentration?
- Which stress component is most important?

---

# Stage 5 — First time-dependent axisymmetric model

Only after Stages 1–4 are validated, create a time integrator.

Do not begin with full 3-D.

Possible approach:

- finite differences or spectral/finite-difference hybrid in `(r,z)`;
- projection method for incompressibility;
- explicit or semi-implicit treatment depending on viscous stability;
- adaptive time step satisfying a documented CFL condition.

Do not choose a sophisticated scheme without first explaining why it is needed.

Start with modest grids, for example:

- 256 x 512;
- 512 x 1024;
- 1024 x 2048 if memory/runtime allow.

Run convergence comparisons.

Track numerical energy balance.

A simulation is not accepted merely because a visually narrowing vortex appears; convergence and incompressibility must be checked.

---

# Stage 6 — Resolve one oscillatory pulse family

Now implement the simplest finite portion of the oscillatory pulse construction.

Do not attempt the paper's infinite hierarchy.

Start with one pulse generation.

For the perturbation velocity `u'`, compute measured averages such as the paper's relevant nonlinear momentum fluxes.

Compare:

\[
\text{resolved pulse stress}
\]

with

\[
\text{target stress from Stage 4}.
\]

Measure:

- seed amplitude;
- amplification factor;
- wavelength evolution;
- phase;
- viscous decay;
- stress amplitude;
- stress spatial location;
- energy drawn from the background flow.

The scientific question is not whether the exact proof constants can be reproduced.

The scientific question is whether a **moderately separated, finite-scale pulse** creates the correct-sign, useful-order-of-magnitude momentum flux.

---

# Stage 7 — Robustness experiments

This stage is central to the project.

Define a baseline finite pulse configuration.

Repeat it with controlled errors:

## Amplitude

Suggested values:

```text
0.50
0.70
0.85
0.95
1.00
1.05
1.15
1.30
1.50
```

relative to baseline.

## Phase

Suggested perturbations:

```text
0°
2°
5°
10°
20°
45°
90°
```

where meaningful.

## Other perturbations

- pulse radial-position error;
- pulse axial-position error;
- wavelength error;
- timing error;
- viscosity error;
- background-profile error;
- random broadband divergence-free noise;
- truncation of high-frequency structure.

Do not test everything at high resolution initially.

Use coarse parameter sweeps to locate interesting transitions, then refine.

---

# Core scientific outcome metrics

Do not reduce the project to the binary question "blowup / no blowup."

Define quantitative metrics.

## Spatial concentration

\[
C_r = \frac{r_{\rm initial}}{r_{\min}}.
\]

## Velocity amplification

\[
C_u = \frac{U_{\max}}{U_{\rm initial}}.
\]

## Vorticity amplification

\[
C_\omega =
\frac{\omega_{\max}}
{\omega_{\max,\rm initial}}.
\]

## Scaling exponent

Fit:

\[
S = \frac{d\log U_{\max}}{d\log r_{\rm core}}.
\]

The theoretical construction should suggest an approximately `-1` relationship up to the small correction associated with the paper's exponent(s). Use the exact paper exponent rather than assuming `-1`.

## Fidelity to target stress

Define a normalized error between the resolved nonlinear stress and the target averaged stress, including both:

- amplitude error;
- spatial-profile error.

## Energy budget

Track:

- total kinetic energy;
- externally injected power;
- viscous dissipation;
- transfer into perturbations if separable;
- numerical energy error.

---

# Stage 8 — Dimensionalization and fluids

Keep the PDE implementation nondimensional as long as possible.

Separately provide dimensional mappings for real fluids.

Create `src/nsblowup/fluids.py` with fluid properties including provenance and temperature.

Initial comparison set:

1. water;
2. air;
3. liquid gallium.

Do not hard-code casual approximate values without recording source, temperature, and pressure.

Properties of interest:

- density `rho`;
- dynamic viscosity `mu`;
- kinematic viscosity `nu = mu/rho`;
- speed of sound;
- vapor pressure for liquids;
- surface tension if cavitation/free surfaces become relevant;
- thermal properties if heating is estimated;
- electrical conductivity for gallium if electromagnetic forcing is investigated.

For air, include mean-free-path/Knudsen-number considerations when small scales are discussed.

For water, include cavitation margin.

---

# First physical reference: water

Water is the default dimensional reference because it is:

- inexpensive;
- transparent;
- experimentally familiar;
- approximately Newtonian in the relevant regime;
- low in kinematic viscosity compared with air;
- compatible with optical velocimetry;
- easy to seed with tracer particles.

Investigate the dimensional relation implied by the paper's scaling rather than assuming it.

A useful approximate relation discussed during project planning is:

\[
U r_{\rm core} \sim \nu
\]

for the dominant scaling when the paper's small correction exponent is neglected.

Verify this carefully from the actual paper's nondimensional scaling.

Do not treat it as exact until derived.

For water, calculate the approximate velocity associated with core scales:

```text
1 mm
100 um
10 um
1 um
100 nm
10 nm
```

and quantify where:

- cavitation may occur;
- compressibility becomes relevant;
- optical diagnostics become difficult;
- tracer particles cease to follow faithfully;
- continuum assumptions become questionable.

Investigate whether moderate static pressurization substantially extends the water regime before cavitation.

---

# Air comparison

Air is cheap but likely less favorable.

Quantify:

- larger kinematic viscosity;
- Mach number as the core shrinks;
- molecular mean free path;
- Knudsen number;
- compressibility onset.

Determine quantitatively how many decades of concentration remain within both:

```text
Mach << 1
Kn << 1
```

for plausible dimensional scalings.

---

# Gallium comparison

Liquid gallium is a secondary candidate.

Potential advantage:

- low kinematic viscosity;
- high electrical conductivity, permitting Lorentz body forcing `J x B`.

Potential complications:

- melting temperature;
- oxide skin;
- compatibility/embrittlement issues;
- opacity;
- cost;
- thermal management;
- diagnostic difficulty.

Do not recommend gallium experimentally until the simulation shows that distributed body forcing would materially improve realizability.

---

# Experimental forcing question

One of the most important outputs is to classify the mathematical forcing into experimentally meaningful pieces.

For every significant forcing contribution, ask whether it could plausibly be represented by:

- boundary rotation;
- distributed jets;
- suction/injection;
- pressure gradients;
- acoustic forcing;
- electromagnetic Lorentz forcing;
- another mechanism.

Separate:

1. force components that can be absorbed into pressure;
2. divergence-free body forcing that changes the velocity field;
3. forcing needed only as a tiny pulse seed;
4. momentum transport actually produced internally by nonlinear Reynolds stress.

The eventual experiment should reproduce the **mechanism**, not necessarily the literal mathematical forcing field.

---

# GPU strategy

Do not optimize for the RTX 4060 Ti until the CPU reference implementation is correct.

When GPU acceleration is useful:

- prefer a code path that preserves double precision;
- measure GPU memory explicitly;
- do not exceed safe VRAM margins;
- keep a CPU implementation for validation.

Because the RTX 4060 Ti has 8 GB VRAM, begin 3-D experiments conservatively.

Potential initial 3-D grids:

```text
128^3
192^3
256^3
```

depending on storage per grid cell.

Before starting a 3-D run, estimate memory from the actual number of simultaneous arrays and FFT/solver workspace.

Do not assume that because one scalar `256^3` array fits, the CFD solver fits.

---

# Cloud transition criteria

Do not move to cloud merely because it is available.

Move an experiment to native-Linux cloud GPU resources when one or more is true:

- required VRAM materially exceeds 8 GB;
- required system RAM approaches Daisy's practical limit;
- a useful single run is unacceptably slow locally;
- a parameter sweep contains many independent runs;
- a production CFD/DNS solver requires native Linux;
- 3-D resolution beyond roughly the local GPU's practical range is scientifically justified.

Cloud runs must be reproducible from the same Git repository and configuration files.

Do not create a separate untracked cloud codebase.

---

# Data policy

Numerical fields can become enormous.

For every run, keep a compact summary containing:

- Git commit;
- configuration;
- date;
- machine/GPU;
- grid;
- time-step strategy;
- precision;
- final metrics;
- convergence notes;
- reason the run stopped.

Save full fields sparsely.

Prefer derived slices/profiles and checkpoints at scientifically meaningful times.

Do not commit multi-gigabyte output to Git.

---

# Visualization

Every important simulation should produce:

1. one or more field plots;
2. time histories of core metrics;
3. log-log scaling plots;
4. residual or stress error plots;
5. a concise run summary.

Eventually create animations of:

- the physical-coordinate collapse;
- the same evolution in similarity coordinates;
- perturbation/pulse amplification;
- vorticity;
- Reynolds-stress generation.

Animations are diagnostic tools, not substitutes for quantitative metrics.

---

# Stopping conditions

A run should stop cleanly if:

- CFL threshold is violated;
- NaN/Inf appears;
- divergence error exceeds a configured bound;
- solver iteration fails;
- minimum resolvable core radius is reached;
- energy-budget error becomes unacceptable;
- physical dimensionalization reaches a user-selected real-fluid limit.

Record the stopping reason explicitly.

---

# Git workflow

Make small commits corresponding to scientific milestones.

Examples:

```text
Initialize reproducible Python environment
Implement similarity coordinates
Implement leading core profile
Add cylindrical divergence operator
Validate axisymmetric operators
Compute finite-truncation residual
Add target Reynolds-stress diagnostic
```

Do not mix major mathematical changes with unrelated refactoring in one commit.

Run tests before commits that alter numerical equations.

---

# Immediate task for the coding agent

Do the following **in order**.

## Task 1

Initialize the repository structure and Python environment.

## Task 2

Read the relevant portions of the source paper necessary for the leading core/similarity construction.

Create `notes/equation-map.md`.

Do not implement uncertain formulas.

## Task 3

Implement only the coordinate transforms and leading profiles needed to reproduce the core geometry.

## Task 4

Create `scripts/plot_profiles.py`.

It should generate plots at several values of time-to-singularity in:

- physical coordinates;
- similarity coordinates.

## Task 5

Implement divergence and test that the leading velocity profile satisfies the expected incompressibility to the accuracy justified by the paper/truncation.

## Task 6

Report findings before building a time integrator.

The report should state:

- exactly which paper equations were implemented;
- what approximations/cutoffs were omitted;
- grid used;
- measured divergence error;
- whether the expected core scaling was reproduced;
- any ambiguity in the paper that matters numerically.

**Do not proceed automatically to a giant 3-D solver.**

The user wants to understand each stage and inspect intermediate results.

---

# Research attitude

A finite physical approximation is interesting even if it cannot approach the mathematical singularity closely.

Useful outcomes include:

- discovering that concentration survives only one or two generations;
- discovering that it is extremely phase-sensitive;
- discovering that generic noise substitutes for carefully seeded pulses;
- discovering that the mechanism evolves into ordinary turbulence;
- discovering that cavitation prevents a water experiment;
- identifying a simpler realizable forcing that reproduces the essential stress;
- finding a stable finite-scale concentrating regime.

Negative results should be preserved and quantified.

The central question is:

> **How much of the mathematical concentrating mechanism survives when the infinite, exact construction is replaced by finite resolution, finite scale separation, finite forcing precision, and a real fluid?**
