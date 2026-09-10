# Sixth Milestone Prompt — Resolve the Same B.15 Tuple Before Any Parameter Change

Read, in this order:

1. `README.md`
2. `RESEARCH_CONTEXT.md`
3. `PROJECT.md`
4. `FIFTH_PROMPT.md`
5. `notes/equation-map.md`
6. `notes/numerical-method.md`
7. the complete fifth-milestone section of `notes/experiment-log.md`
8. `src/nsblowup/core_not_theorem_admissible.py`
9. the relevant source-paper pages directly:
   - (4.8)–(4.13), PDF pp. 26–27
   - Appendix B.1–B.4, especially (B.1)–(B.21), PDF pp. 144–149

Do not change any physical/model parameter until this milestone is complete.

---

# Decision for this milestone

Improve the **local numerical representation only**.

Use exactly the same first tuple that failed milestone 5:

```text
datum       = aggressive compressed datum
Lambda      = 512
g_peak      = 0.1
sigma_star  = 0.2
h           = 0.005
j0          = 0.025
Y domain    = [0, 4.1]
eta domain  = [-1, 1]
```

Do not run:

- another Lambda;
- another g_peak;
- another sigma_star;
- the relaxed-datum nonlinear control;
- global moments/stress;
- outer matching;
- time integration.

The only scientific question in this milestone is:

> **Can the same finite B.15 tuple be represented and differentiated accurately
> enough that the independent original-equation residuals converge under refinement?**

The previous failure is a failure of the present numerical representation,
not evidence of nonexistence.

---

# Confirmed starting points

Treat these fifth-milestone conclusions as established unless a new calculation
finds a concrete contradiction:

1. The B.15 equation mapping and radial-inverse fixed-point map are source-faithful.
2. No outer boundary condition is required at `Y=4.1`.
3. The iteration increment becoming small is not a solution-acceptance test.
4. The independent residual implementation uses the original (4.9)/(4.13)
   sources rather than merely reusing `R1`/`R2`.
5. The current global eta representation underresolves the narrow `g^2` source.
6. At the failed finest grid, the `g^2` interpolant has a roughly 17% peak-scale
   error and negative lobes.
7. Several eta derivatives of the failed iterate worsen under refinement.
8. `sigma_star=0.2` does not reproduce the quantitative B.2 partition.
9. Changing sigma is **not authorized** in this milestone.

Do not spend the milestone merely tightening the fixed-point increment tolerance.

---

# Important scale estimate

Near the negative root `eta0` of `H_star`,

```text
log(g/g_peak)
  ~= -Lambda * L(eta0) * H_star'(eta0)
      * (eta-eta0)^2 / (2 sigma_star^2)
```

For the present tuple the approximate standard deviation is:

```text
g   : ~0.00417
g^2 : ~0.00295
```

The 513-point Chebyshev-Lobatto grid has central spacing of roughly `0.00614`.

Therefore the current global eta grid cannot be regarded as a resolved source
representation.

Verify these numbers independently in the new run record before proceeding.

---

# Task 1 — Source-only representation benchmark

Before running the nonlinear fixed point again, build an exact source benchmark.

On a dense reference eta mesh, evaluate directly from the analytic axis data:

```text
g
g^2
(g^2)_eta
(g^2)_etaeta
zeta_star
chi
Z_star
```

Do not obtain the first two `g^2` derivatives by differentiating an interpolating
polynomial.

Use the exact identities

```text
G = g^2
G_eta = 2 Lambda zeta_star G
G_etaeta = (2 Lambda zeta_star_eta + 4 Lambda^2 zeta_star^2) G
```

with `zeta_star_eta` evaluated analytically or by an independently validated
high-accuracy formula.

Test the current global Chebyshev representation at nested eta counts such as

```text
513
1025
2049
4097
```

or stop earlier if clear convergence is reached.

For every count report:

- peak-value error in `g^2`;
- Linf and L2 errors in `g^2`;
- Linf errors in first and second derivatives;
- minimum of the interpolated `g^2`;
- location error of the peak;
- number of effective grid points across one and six `g^2` standard deviations;
- decay of Chebyshev modal coefficients.

Do not proceed to a nonlinear solve until the source representation has a
documented convergence regime.

A useful engineering source gate is:

```text
relative Linf(g^2) < 1e-4
relative Linf((g^2)_eta) < 1e-3
```

but report the measured convergence even if this gate is missed.

The gate is numerical, not a theorem condition.

---

# Task 2 — Avoid representing the known narrow source as a generic polynomial where possible

The pressure correction has the exact factorization

```text
p(Y,eta) = g(eta)^2 * Pbar(Y,eta)

Pbar(Y,eta) = integral_0^Y Phi(s,eta)^2 ds
```

because `g` is independent of `Y`.

Exploit this structure.

Do not store/differentiate `p` as a generic two-dimensional interpolant if that
needlessly aliases the known narrow factor `g^2`.

Compute, where needed,

```text
p_eta
  = G_eta * Pbar
    + G * Pbar_eta

Pbar_eta
  = integral_0^Y 2 Phi Phi_eta ds
```

and, if second eta derivatives are required for diagnostics,

```text
Pbar_etaeta
  = integral_0^Y 2(Phi_eta^2 + Phi Phi_etaeta) ds
```

with

```text
p_etaeta
  = G_etaeta Pbar
    + 2 G_eta Pbar_eta
    + G Pbar_etaeta.
```

This is an exact algebraic refactorization of the same B.15 pressure equation.

It is **not** a pressure surrogate and does not change the mathematical tuple.

Update the independent pressure-balance validation accordingly:

- verify `Pbar_Y = Phi^2` independently;
- verify reconstructed `p_Y = G Phi^2`;
- compare differentiated numerical `Pbar` against the integral identity;
- do not call an identity exact merely because the same routine produced both sides.

---

# Task 3 — Improve eta differentiation without changing the model

The current dense global Chebyshev differentiation may be retained only if the
source-only benchmark shows it is practical at a sufficiently resolved order.

Otherwise implement one of these source-equivalent numerical representations:

1. **multi-domain Chebyshev in eta**, with a small subdomain centered on `eta0`;
2. a smooth coordinate mapping that clusters eta nodes around `eta0`;
3. another spectrally accurate representation with demonstrably convergent
   first and second derivatives.

Prefer local refinement/multi-domain treatment over simply creating an
enormous dense differentiation matrix.

Any domain interfaces must enforce or verify continuity of:

```text
field
first eta derivative
```

and must permit a stable second derivative.

Do not introduce artificial filtering that changes the solution unless the
filter error is independently quantified and driven to zero under refinement.

---

# Task 4 — Separate source resolution from nonlinear-solution resolution

Use a staged refinement strategy.

## Stage A: eta/source refinement

Hold a reasonable radial representation fixed, for example:

```text
Y count = 65
```

and refine only eta until:

- exact-source interpolation/factorization errors decrease;
- Phi and U first/second eta derivatives stabilize;
- angular and axial residuals decrease.

Do not simultaneously change Y and eta in this stage.

## Stage B: radial refinement

Once eta is demonstrably resolved, hold the chosen eta representation fixed
and refine Y, for example:

```text
33
65
129
```

or an equivalent nested sequence.

This isolates radial error from eta-source error.

## Stage C: one combined confirmation

Only after A and B show convergence, perform one combined refinement pair to
confirm that the accepted result is not an artifact of the staged procedure.

---

# Task 5 — Diagnose endpoint versus central-source errors separately

The fifth-milestone finest angular and axial Linf residuals occurred at
`Y=4.1`, while the narrow source is centered near `eta0`.

Therefore report residual norms split into at least:

```text
all eta
|eta| <= 0.98
small neighborhood of eta0
eta endpoint slices
Y = 0
Y = 4.1
interior Y
```

This is diagnosis only; do not discard endpoint residuals from final acceptance.

Likewise report derivative differences:

- globally;
- on `|eta| <= 0.98`;
- near `eta0`;
- at eta endpoints.

If huge second-eta derivative changes are only endpoint differentiation noise,
that should become visible.

If they persist near the source, that should also become visible.

---

# Task 6 — Modal-resolution diagnostics

For `Phi`, `u`, and the smooth factored pressure variable `Pbar`, record the
Chebyshev or equivalent modal tail in eta.

For each refinement report something like:

```text
max coefficient in highest 10% of modes
/
max coefficient overall
```

and preferably a plot of coefficient magnitude versus mode for selected Y
slices:

```text
Y = 0.5
Y = 2
Y = 4.1
```

Include a slice near the eta location where the failed residual is largest.

A small fixed-point increment with a non-decaying modal tail is not acceptable.

---

# Task 7 — Re-run only the same nonlinear tuple

After the representation passes the source-only checks, rerun:

```text
aggressive datum
Lambda = 512
g_peak = 0.1
sigma_star = 0.2
```

Use both initial guesses already tested if inexpensive:

```text
comparison
flat
```

Do not open any new parameter case.

The original fixed-point map should remain mathematically unchanged apart from
source-equivalent numerical refactorizations.

---

# Task 8 — Acceptance residuals

Continue to evaluate the original equations independently.

For an accepted numerical core require all three residual families to decrease
under the relevant staged refinements:

```text
angular
axial
pressure / Pbar radial identity
```

Report:

- Linf;
- L2;
- sampled RMS;
- axis Linf;
- outer-Y Linf;
- central-source-neighborhood Linf;
- eta-endpoint Linf.

Do not require the old absolute `1e-7` engineering threshold if the convergence
study shows a clear but higher discretization floor; instead document the floor
and observed order/rate.

However, **monotone convergence under refinement remains mandatory**.

If the residuals plateau, identify whether the floor is:

- source representation;
- eta differentiation;
- radial differentiation/integration;
- floating point;
- fixed-point iteration;
- or unknown.

---

# Task 9 — Derivative convergence

For accepted candidates compare on common evaluation grids:

```text
Phi_Y
Phi_eta
Phi_YY
Phi_etaeta

U_Y
U_eta
U_YY
U_etaeta

Pbar_Y
Pbar_eta
Pbar_YY
Pbar_etaeta
```

Reconstruct `Pi` derivatives from the factored pressure afterward.

First and second derivatives must show convergence.

Do not accept a visually stable `Phi` or `U` with unstable derivatives.

---

# Task 10 — Only after numerical acceptance, re-evaluate the first-term comparison

If and only if the same tuple passes residual and derivative convergence,
report again:

```text
max |U-U_star|
max |U-U_star + Y Z_star/(2 L Lambda)|
max |Phi-f0(Y chi)|
```

The previous values

```text
~0.10212
~0.000732
```

came from an unaccepted iterate and must remain labeled historical failed-run
diagnostics.

Do not infer an asymptotic Lambda rate from this one accepted tuple.

---

# Separate sigma_star / B.2 audit

Do not change `sigma_star=0.2` in the nonlinear calculation.

Maintain a separate note:

- B.2 first chooses `delta_star`, then chooses `sigma_star` so that
  `chi > 0.99` wherever `|Z_star| <= delta_star`.
- For sigma_star=0.2 the sampled global maximum chi is about 0.988444.
- Therefore refinement cannot make this same sigma satisfy `chi>0.99`.
- This is a finite-parameter mismatch, not a discretization error.
- Smaller sigma may eventually be needed for a B.2-like partition.
- But because the local width of g scales approximately linearly with sigma,
  reducing sigma makes the present resolution problem more severe.

As a **non-solver side calculation only**, it is acceptable to locate the
real zeros of `Z_star` accurately and compute the sigma threshold implied by

```text
H_star^2 / (H_star^2 + sigma_star^2) > 0.99
```

at those roots.

Do not use that threshold to launch another nonlinear case in this milestone.

---

# Tests

Retain all 75 existing tests.

Add tests for:

- exact `G_eta` and `G_etaeta` formulas against high-order finite differences
  away from underflow;
- source representation convergence;
- nonnegativity of direct `G`, while not requiring a low-order polynomial
  interpolant to be nonnegative;
- factored `p = G Pbar`;
- independent `Pbar_Y = Phi^2` convergence;
- `p_eta` factorization against direct differentiation on a manufactured smooth
  test where both are well resolved;
- any multi-domain interface continuity;
- first/second eta derivative convergence on manufactured analytic functions;
- preservation of the old radial inverse polynomial tests.

Do not weaken old acceptance tests simply to make the new representation pass.

---

# Stop conditions

Stop and report if any of these occurs:

- the exact source benchmark does not converge under the chosen eta method;
- a multi-domain/mapped representation cannot produce stable second derivatives;
- source representation becomes accurate but B.15 residuals still fail to
  converge;
- pressure factorization exposes a discrepancy with the previous equation map;
- endpoint derivative instability remains dominant under refinement;
- the fixed-point iteration itself ceases to converge once the source is
  actually resolved;
- two initial guesses converge to distinct resolved solutions;
- resource use becomes excessive for the local problem.

Each is scientifically useful.

---

# Do not do yet

Do not:

- lower sigma_star;
- change Lambda;
- change g_peak;
- run the relaxed-datum nonlinear control;
- restore global moments;
- construct stress;
- join to the exterior;
- time-integrate Navier–Stokes;
- use GPU optimization;
- claim theorem admissibility;
- claim physical realizability.

---

# Required report

Append a new dated section to `notes/experiment-log.md`.

Report:

1. verified local source widths;
2. source-only interpolation/factorization convergence;
3. numerical representation chosen and why;
4. pressure factorization validation;
5. eta-only refinement results;
6. radial-only refinement results;
7. combined confirmation;
8. residual localization by source/endpoint/interior regions;
9. modal-tail diagnostics;
10. first/second derivative convergence;
11. iteration behavior and initial-guess comparison;
12. whether the same tuple is finally accepted;
13. if accepted, updated B.13 first-term comparison;
14. separate sigma/B.2 note, with no parameter change;
15. runtime and memory.

Then recommend exactly one next gate:

```text
A. Same solver, now test the original relaxed pressure datum as control.
B. Same solver, perform a dedicated sigma_star/B.2 finite-feasibility study.
C. Improve the local numerical method again.
D. Stop because the finite B.15 tuple remains numerically non-credible.
```

Then stop for review.

The central question is:

> **Was the fifth-milestone failure caused by underresolution of the known narrow
> eta source and its induced derivatives, or does the same finite B.15 tuple
> remain nonconvergent after that numerical defect is removed?**
