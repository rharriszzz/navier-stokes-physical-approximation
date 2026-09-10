# Fifth Milestone Prompt — Core-Only Nonlinear B.15 Diagnostic

Read, in this order:

1. `README.md`
2. `RESEARCH_CONTEXT.md`
3. `PROJECT.md`
4. `SECOND_PROMPT.md`
5. `THIRD_PROMPT.md`
6. `FOURTH_PROMPT.md`
7. `notes/equation-map.md`
8. `notes/numerical-method.md`
9. `notes/compression-audit.md`
10. all milestone sections of `notes/experiment-log.md`
11. the relevant source-paper material directly, especially Appendix B.1–B.4,
    equations (B.1)–(B.21), and the profile equations (4.13)

Do not rely on project summaries when an exact equation is required.

---

# Decision for this milestone

Proceed with a **core-only nonlinear diagnostic of (B.15)**.

Do **not** first attempt to restore the compressed exterior's missing global
moments, pulse realization, or stress cone.

This is intentional.

Appendix B takes an already fixed analytic axis pressure datum `Pi0` and solves
the local nonlinear inner profile near the axis before continuing it toward the
outer profile. The present question is therefore:

> **For the finite, non-theorem-admissible axis data already constructed, does
> the actual nonlinear B.15 core exist numerically, converge under refinement,
> and agree with the explicit first-order comparison at accessible Lambda?**

This milestone is a local-core experiment only.

It does **not** establish that the compressed outer schedule can realize the
required moments or stress.

All current models remain **NOT theorem-admissible**.

---

# Two pressure data to use

Use exactly two already validated pressure data:

## A. Aggressive compressed datum

The fourth-milestone `aggressive` schedule:

- radius span about 8.777770 decades;
- principal pulse/angular supports sacrificed;
- A.10 interpolation-slope bound sacrificed;
- conditional scalar Q endpoint retained;
- local `Pi0`, derivatives, and `Z_star` validated.

## B. Original relaxed datum

The uncompressed third-milestone relaxed schedule:

- radius span about 70.444541 decades;
- original relaxed stage lengths retained;
- still not theorem-admissible;
- global moments and stress remain unverified.

The two data agree in the tested local quantities at approximately `1e-11`
relative scale.

Use the original relaxed datum as a **control**, not as a claim of correctness.

Do not recompute or refit either datum by a new pressure surrogate.

---

# Why this comparison is important

Because the aggressive and original relaxed axis data are almost identical,
their local B.15 solutions should also be almost identical if:

- the local nonlinear problem is well conditioned;
- the numerical formulation is correct;
- and the solution depends continuously on the datum in this finite regime.

A material difference between the two solutions would therefore be a warning
about conditioning, implementation, or multiple numerical branches.

Quantify this explicitly.

---

# Task 1 — Source-ground the exact nonlinear system

Before implementation, update `notes/equation-map.md`.

Record the exact finite equations to be solved, including:

- the axis data (B.1)–(B.3);
- the rescaling `Y = Lambda X`;
- the representation (B.12);
- the approximation/expected correction (B.13);
- definitions in (B.14);
- all three equations in (B.15);
- the explicit remainders `R1`, `R2`;
- radial averaging and radial inverse operators used by the proof;
- regularity conditions at `Y=0`;
- any identities from (4.13) needed to verify the implementation.

Also record which statements in Proposition B.2 are theorem-asymptotic and are
**not** being assumed numerically.

Do not introduce an outer boundary condition at `Y=4.1` unless the paper or the
chosen mathematical formulation actually requires one.

The problem is regular-singular at the axis and is constructed outward from
axis data; do not silently turn it into an unrelated boundary-value problem.

---

# Task 2 — Choose a source-faithful numerical formulation

Before coding the solver, write the formulation in `notes/numerical-method.md`.

Prefer one of these, in order:

1. a numerical version of the Appendix-B fixed-point/radial-inverse formulation;
2. coefficient recursion / power series in `Y` with controlled continuation;
3. another method demonstrably equivalent to (B.15).

A generic black-box 2-D nonlinear PDE solver is not preferred unless the
equivalence and boundary treatment are made explicit.

The formulation must explain:

- unknowns;
- representation of `Phi`, `U`, and `Pi`;
- eta differentiation;
- radial differentiation/integration;
- radial averaging;
- treatment of `Y=0`;
- pressure reconstruction;
- nonlinear iteration;
- stopping criterion;
- residual evaluation independent of the iteration criterion.

Do not claim convergence merely because a nonlinear solver returns a success flag.

---

# Task 3 — Axis-profile parameters

The existing first-pass comparison used approximately:

```text
h = 0.005
j0 = 0.025
sigma_star = 0.2
```

Keep `h` and `j0` fixed for this milestone.

For `sigma_star`, first audit the finite B.1/B.2 consequences of the existing
value `0.2`.

Report:

- `H_star`;
- `Z_star`;
- the negative zero `eta0`;
- `chi = H_star^2/(H_star^2 + sigma_star^2)`;
- where `chi > 0.99`;
- where `|Z_star|` is small/large;
- whether the qualitative partition underlying (B.2) is visible.

Do not call `sigma_star=0.2` theorem-valid.

If `0.2` gives a numerically pathological axis profile, allow **one** smaller
source-grounded sensitivity value, for example `0.1`, and document why.

Avoid a broad sigma sweep.

---

# Task 4 — Treat the swirl normalization C explicitly

This is important.

Proposition B.2 chooses `C >= C0(Lambda)` only after Lambda is fixed. The proof
uses large C so that

```text
g = phi_star / C
```

is small on the relevant complex neighborhood.

The first milestone normalized the real-axis peak of `g` to one for plotting.
Do not silently equate that plotting normalization with a theorem-valid C.

Parameterize the finite experiment by a real-axis normalization such as

```text
g_peak = max_real |g|
```

or an exactly equivalent documented quantity.

Use a **small continuation family**, for example:

```text
g_peak = 0.1
g_peak = 0.3
g_peak = 1.0
```

provided the actual axis normalization makes these meaningful.

Start from the smallest value.

The point is to learn whether the finite nonlinear solution persists as swirl
strength is increased toward the earlier comparison normalization.

Do not perform a large C scan.

---

# Task 5 — Primary Lambda values

Use:

```text
Lambda = 512
Lambda = 128
```

as the primary finite cases.

Start with `Lambda=512`, because the first explicit correction is about `0.10`
in maximum absolute magnitude for the present datum.

Then try `Lambda=128`, where it is about `0.40`.

If a larger-Lambda asymptotic anchor is genuinely useful and inexpensive,
one `Lambda=2048` case may be added, but do not let it expand the milestone.

Do not use `Lambda=32` unless needed as a documented failure/control case.

---

# Task 6 — Solve B.15 on the local core only

Solve on the Appendix-B radial interval

```text
0 <= Y <= 4.1
```

and on the real eta interval needed by the equations, initially

```text
-1 <= eta <= 1
```

with any necessary numerical endpoint treatment documented.

Do not map this to the enormous outer radial schedule.

The B.15 solve is a local similarity-profile problem; the 8.78- or 70.44-decade
outer geometry is not a computational grid for this milestone.

Use CPU float64 initially.

No CUDA/MPS optimization.

---

# Task 7 — Independent equation residuals

For every accepted solution evaluate the actual B.15 residuals independently
of the iteration machinery.

At minimum report norms for:

1. the angular equation;
2. the axial equation;
3. radial pressure balance.

Use:

- `Linf`;
- an `L2` or weighted `L2`;
- axis-specific residuals near `Y=0`;
- endpoint residuals near `Y=4.1`.

Run at least three nested resolutions if the formulation is grid based.

If coefficient based, increase truncation order and independently evaluate the
equations on a denser set of off-grid points.

A solution is not accepted unless the equation residual decreases under
refinement/truncation.

---

# Task 8 — Compare with the explicit Appendix-B approximation

For each accepted solution compute:

```text
DeltaU_actual = U_nonlinear - U_star
DeltaU_first  = -Y Z_star / (2 L Lambda)
```

and compare them.

Report quantities such as:

```text
||DeltaU_actual - DeltaU_first||inf
||DeltaU_actual - DeltaU_first||inf / max(1, ||DeltaU_actual||inf)
```

Also compare:

- `Phi` with `f0(Y chi)`;
- pressure correction `Pi - Pi0`;
- first derivatives in Y;
- first derivatives in eta;
- second derivatives needed by B.15.

The central asymptotic test is whether the error after subtracting the first
explicit term decreases roughly as Lambda increases.

Do not assume the rate in advance.

Measure it.

---

# Task 9 — Aggressive versus relaxed control

At each common `(Lambda, g_peak, sigma_star)` for which both solve, compare the
nonlinear solutions generated by:

- aggressive compressed `Pi0`;
- original relaxed `Pi0`.

Report normalized differences in:

- `Phi`;
- `U`;
- `Pi`;
- relevant first derivatives;
- B.15 residuals.

Because their input local data differ by only about `1e-11`, a large solution
difference is scientifically important and must not be dismissed.

Do not tune solver tolerances independently to make the two agree.

---

# Task 10 — Local continuation diagnostics, not proof claims

If a solution is obtained, it is useful to evaluate the real-axis quantities
that Appendix B later uses:

- positivity/minimum of `Phi`;
- angular source `S_q`;
- `p1`, `p2`, `n_s` where numerically available;
- the outer-endpoint shear expression associated with (B.19).

These are **diagnostics only**.

Do not claim Proposition B.3, complex-neighborhood bounds, or theorem
continuation unless those hypotheses were actually established.

A failure of one of these real-axis diagnostics is important and should be
reported.

---

# Task 11 — Conditioning and continuation

Track:

- nonlinear iteration counts;
- residual history;
- dependence on initial guess;
- condition estimates where practical;
- whether continuation in `g_peak` or Lambda is required;
- whether the solver finds more than one branch from substantially different
  initial guesses.

Use the explicit comparison `(Phi0, u0)` from Appendix B as the primary initial
guess when appropriate.

If two reasonable initial guesses converge to different solutions, stop and
report rather than choosing one silently.

---

# Task 12 — Cross-platform control if inexpensive

The main development run may remain on Daisy.

If a clean reference case such as

```text
aggressive datum
Lambda = 512
smallest successful g_peak
```

can be reproduced easily on the M4 iMac from the same Git commit and config,
do so and compare the main norms.

This is optional and should not delay the scientific milestone.

---

# Stop conditions

Stop and report if any of these occurs:

- the exact finite B.15 formulation is materially ambiguous;
- a required axis quantity is not representable accurately;
- residuals do not decrease under refinement;
- the solver requires an arbitrary outer boundary condition not justified by
  the source formulation;
- `Phi` crosses zero where division by it is required;
- results depend strongly on grid/order without convergence;
- aggressive and relaxed controls diverge far beyond their input-data difference;
- multiple stable branches appear;
- `Lambda=512` cannot be solved even at small `g_peak`;
- or the actual nonlinear correction is much larger than the first explicit
  term throughout the accessible regime.

These are all scientifically useful outcomes.

---

# Do not do yet

Do **not**:

- restore global moments;
- implement the axial pulse;
- implement angular pressure-preserving bumps;
- verify the full outer stress cone;
- join the core to the exterior;
- compute a whole-flow momentum residual;
- time-integrate Navier–Stokes;
- run 3-D CFD;
- claim dynamical concentration;
- claim physical realizability;
- claim theorem admissibility.

Those are later gates.

---

# Required report

Append a new dated section to `notes/experiment-log.md`.

Report:

1. exact B.15 formulation implemented;
2. numerical method and axis treatment;
3. sigma_star audit;
4. swirl normalization / C treatment;
5. successful and failed `(Lambda, g_peak)` cases;
6. residual convergence;
7. nonlinear correction versus the B.13 first term;
8. Phi comparison with `f0(Y chi)`;
9. pressure correction;
10. derivative convergence;
11. aggressive-versus-relaxed control differences;
12. real-axis B.17–B.19-style diagnostics, clearly labeled non-proof;
13. conditioning / branch information;
14. runtime and memory;
15. whether the local nonlinear core now appears numerically credible.

Then recommend exactly one next gate:

```text
A. Restore/check global moments and stress compatibility.
B. Improve the local nonlinear solver first.
C. Explore one additional finite Lambda/C regime.
D. Stop because the finite local-core approximation is not numerically credible.
```

Then stop for review.

The central question is:

> **Does the actual finite nonlinear B.15 core behave as the Appendix-B
> perturbation predicts, and is that local behavior insensitive to the enormous
> outer schedule geometry that was compressed away?**
