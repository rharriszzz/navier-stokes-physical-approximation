# Second Codex / Copilot Agent Prompt

Use this prompt for the **second milestone** of the `navier-stokes-physical-approximation` project.

Before doing any work:

1. Read `README.md`.
2. Read `RESEARCH_CONTEXT.md`.
3. Read `PROJECT.md`.
4. Read `notes/equation-map.md`.
5. Read `notes/numerical-method.md`.
6. Read `notes/experiment-log.md`.
7. Inspect the current source, tests, configs, and `results/core-comparison`.
8. Read the cited source paper directly wherever exact formulas are required.

Do not rely on summaries when an exact equation from the paper is needed.

---

# Current status

The first milestone is complete.

What is already validated:

- the Appendix B explicit comparison geometry;
- the forward/inverse similarity-coordinate map;
- the physical velocity reconstruction for the explicit comparison;
- exact analytical incompressibility of that comparison;
- second-order numerical divergence convergence;
- rescaled-profile collapse;
- expected prescribed scaling of the comparison field;
- reproducible environment and run summaries;
- 45 passing tests.

Important limitation:

The current implementation is **not** the nonlinear core solution of the paper.

It is only the explicit Appendix B comparison.

The current code deliberately omits:

- the exterior pressure datum `Pi0(eta)` from (4.31);
- the associated `Z_star`;
- the first axial correction appearing in Appendix B;
- nonlinear profile corrections from (B.15);
- inner/exterior matching;
- annular stress;
- oscillatory pulse families;
- cutoffs;
- the full Navier–Stokes momentum residual;
- time integration;
- 3-D DNS.

Do not reinterpret the existing `1000x` shrinking radius and `~1000x` velocity growth as a numerical dynamical result. They are prescribed similarity scalings of the comparison field.

A particularly important observation from the first run is that for the exploratory choice

```text
h = 0.005
Lambda = 32
sigma = 0.2
j0 = 0.025
```

the nominal higher-order parameter `q^(2h)` is still about `0.871` at the midplane when `tau = 1e-6`.

Therefore the omitted higher-order terms cannot be assumed numerically small merely because `tau` is small.

---

# Scientific objective of this milestone

The next question is:

> **At computationally attainable finite parameters, how close is the explicit Appendix B comparison to the actual corrected nonlinear inner core?**

This is more important now than extending the prescribed similarity evaluation to even smaller `tau`.

The goal of this milestone is to implement only enough of the next layer of the paper to quantify that difference.

Do **not** proceed to annular pulses, time integration, or 3-D DNS.

---

# Primary tasks

## Task 1 — Source-ground the exterior pressure datum

Read the relevant portion of the paper surrounding:

- equation (4.31);
- the Appendix A construction needed to determine `Pi0(eta)`;
- every definition on which that datum depends.

Update `notes/equation-map.md` before implementing.

Document:

- paper equation numbers;
- PDF page numbers;
- dependencies among quantities;
- which constants/functions are explicitly defined;
- which are only existential/asymptotic;
- which finite parameter choices must be introduced numerically.

Do not set `Pi0 = 0`.

Do not replace it by an arbitrary pressure profile.

If the paper does not provide enough information for a unique finite numerical value without additional choices, state exactly what choices are required and make them explicit in configuration.

---

## Task 2 — Construct a reproducible finite `Pi0(eta)`

Implement a numerical representation of the exterior pressure datum required by the inner problem.

Requirements:

- double precision;
- architecture-neutral NumPy/SciPy implementation;
- no GPU dependency;
- explicit configuration of finite parameters;
- tests for smoothness, interpolation consistency, and reproducibility;
- record numerical quadrature/solver tolerances;
- save a diagnostic plot of `Pi0(eta)` and any directly related quantities.

If a boundary-value problem or ODE must be solved, include an independent residual check.

If the finite construction is numerically under-specified, do not hide that fact. Add the ambiguity to the experiment log.

---

## Task 3 — Implement `Z_star` and the first omitted axial correction

Using the exact equations in Appendix B, implement:

- `Z_star`;
- the first axial correction omitted from the existing comparison;
- any immediate dependent quantities required to evaluate that correction consistently.

Do not yet solve the entire nonlinear problem unless that is genuinely necessary for the correction.

Add unit tests tied to identities or limiting cases from the paper where possible.

---

## Task 4 — Solve the finite-parameter nonlinear inner correction

Implement the finite-parameter version of the nonlinear inner equations corresponding to (B.15), or the smallest mathematically faithful subsystem sufficient to recover the corrected inner profile.

Before coding, document the numerical formulation in `notes/numerical-method.md`:

- unknowns;
- independent variables;
- domain;
- boundary conditions;
- normalization conditions;
- solver type;
- discretization;
- stopping tolerances;
- continuation strategy if used;
- failure criteria.

Prefer a method that is easy to validate over one that is maximally fast.

Do not silently accept solver convergence based only on an optimizer/status flag.

Compute and report the actual equation residual of the solved profile.

---

# Parameter study

The first milestone used one exploratory point:

```text
h = 0.005
Lambda = 32
sigma = 0.2
j0 = 0.025
```

This milestone should investigate whether the comparison improves as the relevant asymptotic parameters are pushed in the theoretically favorable direction.

Start with a **small coarse sweep**, not a huge job.

Suggested first exploration:

### `Lambda`

```text
16
32
64
128
```

if numerically stable and resolvable.

### `sigma`

Use a few values around the present value, for example:

```text
0.4
0.2
0.1
0.05
```

but only where the axial structure is adequately resolved.

### `h`

Use a small number of values, for example:

```text
0.01
0.005
0.0025
```

subject to the paper's allowed range and numerical conditioning.

Do not blindly run the full Cartesian product.

Use the baseline first, then vary one parameter at a time to identify which direction is informative.

If increasing `Lambda` or decreasing `sigma` requires more grid points, adapt resolution and record the requirement.

---

# Main quantities to measure

For every successful corrected solution, compare the corrected nonlinear inner profile with the existing Appendix B comparison.

At minimum compute normalized errors such as

\[
\epsilon_U =
\frac{\|U_{\mathrm{corrected}} - U_{\mathrm{comparison}}\|}
{\|U_{\mathrm{corrected}}\|},
\]

\[
\epsilon_E =
\frac{\|E_{\mathrm{corrected}} - E_{\mathrm{comparison}}\|}
{\|E_{\mathrm{corrected}}\|}.
\]

Use more than one norm where useful:

- `Linf`;
- weighted or ordinary `L2`;
- derivative-sensitive norms if the momentum residual depends strongly on derivatives.

Also compare:

- axial correction magnitude;
- swirl correction magnitude;
- radial velocity reconstructed from incompressibility;
- relevant first derivatives;
- relevant second derivatives;
- conditioning of the nonlinear solve;
- grid resolution required.

The key practical relationship to expose is:

> **asymptotic accuracy versus computational resolution / scale separation**

For example, if doubling `Lambda` reduces profile error by a factor of two but requires 8x more axial resolution, record that explicitly.

---

# Derivative accuracy

The later momentum-residual calculation will depend on derivatives, not only field values.

Therefore a corrected profile that looks visually close is not sufficient.

For each important profile component, assess convergence of:

- the field;
- first derivatives;
- second derivatives where the later Navier–Stokes operator will require them.

If derivative errors remain large while field errors are small, make that a prominent conclusion.

---

# Do not compute a misleading full momentum residual

Do **not** calculate the final full Navier–Stokes residual unless all quantities required for that residual are now specified consistently.

In particular:

- do not invent pressure;
- do not omit a correction known to be of comparable order;
- do not apply an arbitrary window cutoff and call the resulting residual intrinsic to the core.

A limited residual diagnostic is acceptable only if its mathematical scope is clearly stated.

A useful target, if supported by the completed corrections, is to compare the **leading tangential momentum residual** before and after the nonlinear correction.

If that can be computed faithfully, do so and quantify the improvement.

---

# Two-machine portability requirement

There are now two available local machines.

## Daisy

- Intel Core i7-14700F
- 16 GB host RAM
- NVIDIA RTX 4060 Ti
- 8 GB VRAM
- Windows 11
- WSL2 Ubuntu
- current WSL memory exposure was about 7.6 GiB in the first run

## iMac

- Apple M4 processor
- 24 GB unified memory
- macOS

For this milestone:

- keep the implementation CPU-first;
- use NumPy/SciPy;
- do not require CUDA;
- do not require Apple MPS;
- avoid x86-specific assumptions;
- avoid Linux-only assumptions unless unavoidable.

At least one reference calculation should eventually be runnable on both machines from the same Git commit and configuration.

If practical during this milestone, create a documented cross-platform command such as:

```bash
python -m pytest -q
python scripts/<relevant-script>.py --config configs/<config>.yaml
```

Do not require the user to maintain separate source branches for macOS and WSL.

---

# Reproducibility

Every substantive run should record:

- Git commit hash;
- dirty/clean status;
- machine name;
- OS/platform;
- CPU architecture;
- Python version;
- NumPy/SciPy versions;
- total/available memory;
- precision;
- all mathematical parameters;
- all grid parameters;
- solver tolerances;
- iteration count;
- residual norms;
- stopping reason.

Preserve the existing source-hash convention where useful.

Do not overwrite previous result directories.

---

# Tests

Add tests appropriate to the new mathematics.

Examples include:

- reconstruction of known Appendix A identities;
- pressure-datum interpolation consistency;
- convergence of quadrature;
- convergence of nonlinear solver residual;
- finite-difference/spectral derivative convergence;
- corrected incompressibility;
- limiting comparison behavior where justified by the paper.

Do not weaken or delete the existing tests merely to make new code pass.

---

# Visualization

Produce plots that help answer the scientific question, not just pretty images.

At minimum:

1. `Pi0(eta)` and related exterior datum;
2. corrected versus comparison `U`;
3. corrected versus comparison swirl profile;
4. absolute/relative correction fields;
5. error versus `Lambda` for at least one controlled sweep;
6. required grid resolution versus parameter, if it changes materially;
7. solver residual/convergence history where useful.

Use logarithmic axes where appropriate.

---

# Stop conditions

Stop this milestone and report rather than proceeding if any of the following occurs:

- the paper's finite numerical construction is under-specified in a material way;
- the nonlinear inner problem cannot be solved robustly at the baseline parameters;
- solver residual does not converge under refinement;
- the required resolution grows beyond the available local-memory budget;
- derivative errors do not converge;
- a supposedly small asymptotic correction remains order one throughout the accessible parameter range;
- the corrected solution no longer resembles the explicit comparison.

Any of these is a scientifically valuable result.

---

# Do not do yet

Do **not** proceed to:

- time integration;
- oscillatory pulse simulation;
- annular Reynolds-stress generation;
- full inner/exterior/cutoff completion;
- 3-D DNS;
- GPU optimization;
- water/air/gallium dimensionalization;
- laboratory apparatus design.

Those are later milestones.

---

# Required final report

When this milestone is complete, update `notes/experiment-log.md` with a new dated section and stop.

Report:

1. exact paper equations newly implemented;
2. all new numerical assumptions;
3. how `Pi0` was obtained;
4. how the nonlinear inner correction was solved;
5. solver residuals and convergence;
6. corrected-versus-comparison errors;
7. derivative errors;
8. parameter-sweep results;
9. resolution requirements;
10. whether the explicit Appendix B comparison appears to approach the nonlinear inner core in an accessible parameter regime;
11. whether there is now enough information to compute a meaningful momentum residual;
12. recommended next scientific experiment.

Also report any evidence that the finite approximation is already becoming computationally impractical.

The central question for this milestone is:

> **Can the nonlinear corrected core be reached at finite, computationally realistic parameters while remaining quantitatively close to the explicit comparison profile?**
