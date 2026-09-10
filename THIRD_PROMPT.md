# Third Milestone Prompt — Relaxed-Hierarchy Finite Schedule Experiment

Read, in this order:

1. `README.md`
2. `RESEARCH_CONTEXT.md`
3. `PROJECT.md`
4. `SECOND_PROMPT.md`
5. `notes/equation-map.md`
6. `notes/numerical-method.md`
7. the complete second-milestone section of `notes/experiment-log.md`
8. the relevant source-paper pages/equations directly

Do not rely on project summaries for an exact paper formula.

## Decision for this milestone

We are **explicitly authorizing a relaxed-hierarchy finite experiment**.

Do **not** attempt to certify a theorem-admissible Appendix A parameter hierarchy in this milestone.

The exact proof hierarchy is intentionally much more extreme than the finite scales we want to study physically. In particular, the source audit correctly found

\[
T_d=e^{M_d}+10,\qquad P_*>e^{T_d},\qquad h<e^{-T_d},
\]

so necessarily

\[
h<e^{-10}\approx4.54\times10^{-5},\qquad P_*>e^{10}\approx2.20\times10^4,
\]

with the actual proof choices potentially far more extreme.

That exact hierarchy remains an important reference, but reproducing every proof scale is not the present scientific objective.

The objective is:

> **Preserve the paper's schedule architecture and pressure formula as faithfully as practical, while deliberately compressing the proof hierarchy, and measure what finite pressure and first inner correction result.**

Every result from this milestone must be clearly labeled as **not theorem-admissible unless separately proved otherwise**.

Do not blur this distinction in filenames, plots, summaries, or prose.

---

# Independent checks already made

The following source-audit conclusions have been independently checked against the paper and may be treated as confirmed starting points:

1. Lemma 4.8 and (A.6) impose the hierarchy stated above.
2. The existing comparison values `h=0.005`, `0.0025`, etc. are not admissible under that hierarchy.
3. Equation (A.21) gives the scheduled axis pressure datum.
4. The pressure-preserving angular bumps can be omitted when evaluating that total datum.
5. The compensated heat replacement preserves the same axis datum.
6. At the negative root `eta0` of `H_star`, (A.22) and (B.1) imply the lower bound documented in the repo.
7. The reported illustrative value near `1.3475963e7` for the conservative exact-hierarchy-derived `Z_star` bound, and the associated `Lambda=16..128` derivative table, are arithmetically correct.
8. Those bounds are **not** nonlinear field errors and do **not** prove numerical impossibility.
9. Equation (B.13) shows why the proof is allowed to take `Lambda` extremely large after the earlier parameters have been fixed.

Do not spend the milestone re-litigating those checks unless implementation reveals a genuine contradiction.

---

# Scope

This milestone is intentionally narrower than the previous prompt.

Implement and validate:

1. a finite Appendix-A-style scheduled swirl amplitude in logarithmic radius;
2. the corresponding full scheduled pressure datum from (A.21);
3. its first two `eta` derivatives;
4. `Z_star`;
5. the **first explicit axial correction diagnostic** from (B.13).

Then stop.

Do **not** solve the full nonlinear system (B.15) in this milestone.

Do **not** time-integrate Navier–Stokes.

Do **not** implement oscillatory pulses, annular stress realization, 3-D DNS, or GPU code.

---

# Task 1 — Implement the scheduled pressure evaluator

Use the source-paper schedule structure in Appendix A, especially (A.5)–(A.13) and (A.21).

Work in the logarithmic radial coordinate

\[
y=\log(X/X_R).
\]

Do not construct astronomical physical radii directly.

The implementation should represent the schedule stage-by-stage and integrate

\[
\Pi_0(\eta)
=
-\frac12\int_{-\infty}^{\infty}
E_{\mathrm{id,sched}}(y,\eta)^2\,dy.
\]

Use analytic integrals for simple exponential/power-law pieces where convenient, and numerical quadrature for transition pieces.

The angular pressure-preserving bumps should remain omitted from the pressure evaluator, consistent with Lemma A.5.

The later compensated heat replacement is not needed for this calculation.

## Important

Preserve the **functional schedule architecture** of the paper.

The relaxed experiment is permission to relax the proof's ordering/size inequalities; it is **not** permission to replace `Pi0` by:

- zero,
- the inner contribution alone,
- a fitted polynomial,
- an arbitrary Gaussian,
- or any other unrelated pressure surrogate.

---

# Task 2 — Define a small relaxed parameter family

Keep the first-milestone inner reference values initially:

```text
h = 0.005
j0 = 0.025
```

These are deliberately outside the exact proof hierarchy and must be marked as such.

Choose a **small** finite family of outer schedule parameters intended to compress the scale separation while retaining internally meaningful schedule stages.

Start with one documented baseline relaxed schedule.

Then vary only the most informative parameters one at a time.

A reasonable exploratory neighborhood is:

```text
M_d:     order 1 to a few
lambda:  roughly 0.05 to 0.2
P_star:  order 1 to 10
```

but do not use these numbers blindly if the exact schedule formulas make a choice inconsistent or nonsensical.

Choose `T_f` and `c_o` from the actual schedule requirements where possible rather than arbitrary aesthetics.

For every tuple report exactly which requirements are:

- algebraically satisfied;
- geometrically satisfied;
- intentionally relaxed;
- not checked.

Do not call a tuple "admissible" merely because the code can evaluate it.

---

# Task 3 — Validate the schedule before interpreting pressure

For each evaluated schedule verify at least:

- continuity/smoothness at stage joins to the expected order;
- positivity of the swirl amplitude where required by the schedule;
- finite convergence of the tail contribution;
- correct ordering and nonnegative lengths of intervals;
- the `Q` stopping event where that stage is retained;
- absence of overflow/underflow caused solely by representation;
- quadrature convergence under tighter tolerances/refinement.

Store amplitudes logarithmically where needed.

Report total logarithmic radial span of the finite transition schedule.

Also report the corresponding scale separation as

\[
\log_{10}(X_{\rm outer}/X_R)
=
\Delta y/\log 10,
\]

rather than forming the ratio itself when enormous.

This scale-separation metric is scientifically important.

---

# Task 4 — Compute Pi0 and its derivatives

For each valid relaxed schedule compute on a suitable `eta` grid:

- `Pi0(eta)`;
- `dPi0/deta`;
- `d2Pi0/deta2`.

Check derivative accuracy independently.

Prefer differentiation under the integral / analytic differentiation of the scheduled integrand where practical, with a finite-difference or other independent check.

Verify the qualitative properties that survive in the relaxed run:

- evenness of `Pi0`;
- sign of `eta * Pi0_eta`;
- smoothness;
- quadrature convergence.

If one of these fails, report it prominently rather than forcing it.

Plot:

1. `Pi0`;
2. `Pi0_eta`;
3. `Pi0_etaeta`.

---

# Task 5 — Compute Z_star and the first explicit correction diagnostic

Using the exact Appendix B definition,

\[
Z_*=
-A(1-2\eta U_*)U_*
-H_*U_{*\eta}
-d\Pi_{0\eta}
+4A\eta\Pi_0,
\]

compute `Z_star(eta)` for each relaxed schedule.

Locate the unique negative root `eta0` of `H_star`.

Record:

- `Pi0(eta0)`;
- `Pi0_eta(eta0)`;
- `Z_star(eta0)`;
- `max_eta |Z_star|`.

Then evaluate the first explicit correction suggested by (B.13),

\[
\delta U_1(Y,\eta)
=
-\frac{Y Z_*(\eta)}{2L(\eta)\Lambda}.
\]

Use a **small** set of `Lambda`, for example

```text
32
128
512
2048
```

if numerically harmless.

This is a diagnostic only.

Do not claim it equals the nonlinear corrected profile at finite `Lambda`.

For `Y=4`, report:

- `max |delta U_1|`;
- `|delta U_1(eta0)|`;
- a relative measure such as
  `max|delta U_1| / max(1, max|U_star|)`.

Plot correction magnitude versus `Lambda`.

---

# Task 6 — Compare hierarchy compression against physical usefulness

The central output should be a compact table for each relaxed schedule containing:

- `M_d`;
- `T_d`;
- `P_star`;
- `lambda`;
- `h`;
- intentional hierarchy violations;
- total logarithmic radial span;
- equivalent `log10` radial scale separation;
- `max|Pi0|`;
- `max|Pi0_eta|`;
- `max|Z_star|`;
- first-correction metric at each tested `Lambda`.

Include the existing exact-hierarchy **necessary lower-bound diagnostic** as a reference row or separate reference figure, clearly labeled as a bound rather than a solved schedule.

The scientific question is:

> How much hierarchy compression is required before the first inner correction becomes order-one or smaller at computationally plausible `Lambda`, and what radial scale separation does that compressed schedule still demand?

---

# Stop conditions

Stop and report rather than moving to a nonlinear solve if:

- the full relaxed schedule cannot be constructed consistently even after explicitly relaxing the proof inequalities;
- the `Q` stopping event fails for the baseline relaxed tuple;
- the pressure integral is numerically unstable under refinement;
- `Pi0` derivatives do not converge;
- the sign/symmetry structure fails in a way that undermines the intended inner construction;
- the first explicit correction remains enormous for every reasonable compressed schedule;
- or the radial scale separation remains physically absurd even after substantial hierarchy compression.

These are useful results.

---

# Do not do in this milestone

Do not:

- certify the Millennium proof;
- claim theorem admissibility for relaxed runs;
- solve (B.15);
- compute a full Navier–Stokes momentum residual;
- build the annular stress;
- implement pulses;
- run 3-D CFD;
- optimize for CUDA/MPS;
- dimensionalize to water/air/gallium yet.

---

# Portability

Keep all new code CPU-first, float64, NumPy/SciPy, and portable to:

## Daisy
- i7-14700F
- Windows 11 / WSL2 Ubuntu
- 16 GB host RAM
- RTX 4060 Ti 8 GB

## iMac
- Apple M4
- 24 GB unified memory
- macOS

Run on Daisy first.

If easy, run one reference pressure calculation on the iMac from the same Git commit and config as a cross-platform check. Do not block the milestone on that.

Improve the environment metadata helper so macOS records architecture and memory cleanly if this can be done without distracting from the scientific task.

---

# Required report

Append a new dated section to `notes/experiment-log.md`.

Report:

1. exact paper equations used;
2. explicit statement that this milestone is a relaxed-hierarchy experiment;
3. baseline relaxed schedule and every intentional hierarchy violation;
4. schedule-stage validation;
5. pressure quadrature convergence;
6. derivative validation;
7. `Pi0` results;
8. `Z_star` results;
9. first-correction diagnostics versus `Lambda`;
10. logarithmic radial scale separation;
11. comparison with the exact-hierarchy necessary bound;
12. whether any compressed regime appears worth taking to a nonlinear (B.15) solve.

Then stop and ask for review before implementing the nonlinear correction.

The desired outcome is not to make the proof constants look reasonable.

The desired outcome is to learn whether the **mechanism has a useful finite analogue once proof-scale separations are deliberately compressed and honestly labeled**.
