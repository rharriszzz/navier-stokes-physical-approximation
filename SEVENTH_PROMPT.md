# Seventh Milestone Prompt — Endpoint-Stable B.15 Solve at the Same Tuple

Read, in this order:

1. `README.md`
2. `RESEARCH_CONTEXT.md`
3. `PROJECT.md`
4. `FIFTH_PROMPT.md`
5. `SIXTH_PROMPT.md`
6. `SIXTH_RESPONSE.md`
7. `notes/equation-map.md`
8. `notes/numerical-method.md`
9. the fifth- and sixth-milestone sections of `notes/experiment-log.md`
10. `src/nsblowup/core_not_theorem_admissible.py`
11. any new sixth-milestone source files implementing factorized pressure/source resolution
12. the relevant source-paper pages directly:
   - (4.8)–(4.13), PDF pp. 26–27
   - Appendix B.1–B.4, especially (B.1)–(B.21), PDF pp. 144–149

Do not change the mathematical tuple in this milestone.

---

# Fixed tuple

Use exactly:

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

All models remain **NOT theorem-admissible**.

Do not run any different `Lambda`, `g_peak`, `sigma_star`, or exterior datum.

---

# Starting point

Milestone 6 established the following:

- the narrow source is now resolved;
- at 2049 eta nodes, relative source errors are approximately:
  - `g^2`: `9.57e-9`
  - `(g^2)_eta`: `9.57e-8`
  - `(g^2)_etaeta`: `6.36e-6`
- exact pressure factorization `p = g^2 Pbar` is implemented;
- pressure balance and `Pbar_Y = Phi^2` are accurate to about machine precision;
- the remaining nonlinear failure is localized primarily at the outer-Y / eta-endpoint corner;
- at the minimum-increment snapshot, central-source residuals are already very small;
- the fixed-point iteration later develops endpoint derivative growth and proposes negative `Phi`;
- the cause is not yet uniquely identified: endpoint spectral amplification, roundoff, loss of discrete contraction, or a combination.

Do not repeat the global-source-resolution work except as a regression check.

---

# Scientific objective

The sole question is:

> **Can the same finite B.15 tuple be solved with a numerically stable eta representation that preserves full-domain endpoint checks and produces convergent first/second derivatives and original-equation residuals?**

Do not reinterpret endpoint instability as evidence against existence.

Do not remove the endpoints from acceptance.

---

# Task 1 — Localize the instability precisely

Before changing the solver, reproduce one source-resolved failed run and record:

- iteration at minimum increment;
- iteration at onset of residual growth;
- location of maxima for angular and axial residuals;
- location of largest `Phi_etaeta`, `U_etaeta`, and `Pbar_etaeta`;
- modal spectra at representative Y slices;
- endpoint values and endpoint derivatives through the iteration history.

Separate:

```text
eta = -1
eta = +1
|eta| <= 0.98
small neighborhood of eta0
Y = 4.1
interior Y
```

Determine whether the dominant instability begins at one endpoint, both endpoints, or a corner coupled to `Y=4.1`.

---

# Task 2 — Replace the single global eta polynomial

Implement an endpoint-stable representation without changing the equations.

Preferred option:

## Multi-domain Chebyshev in eta

Use a small number of subdomains, for example conceptually:

```text
[-1, -a]
[-a, b]
[b, 1]
```

with the center domain chosen to resolve the narrow source near `eta0`, and endpoint domains chosen to improve derivative conditioning.

The exact partition is a numerical design choice and should be justified by source width and derivative behavior.

Alternative acceptable options:

- mapped Chebyshev coordinates with explicit endpoint conditioning analysis;
- another high-order representation with demonstrably convergent first and second derivatives.

Avoid simply increasing one dense global differentiation matrix to enormous size.

---

# Task 3 — Interface conditions

For any multi-domain method, enforce or verify continuity of:

```text
Phi
Phi_eta
u
u_eta
Pbar
Pbar_eta
```

at every eta interface.

Second derivatives may be discontinuous at finite resolution but must converge under refinement.

Report interface jumps explicitly.

Acceptance requires interface jumps to decrease under refinement.

Do not smooth or average interfaces in a way that changes the equations without a vanishing-error study.

---

# Task 4 — Manufactured derivative tests

Before solving B.15, validate the new eta representation on analytic functions chosen to stress:

- endpoint derivatives;
- narrow Gaussian-like features near `eta0`;
- smooth non-symmetric functions;
- first and second eta derivatives.

Include at least one function with width comparable to the present `g^2` source.

Measure convergence of:

```text
field
first derivative
second derivative
endpoint derivatives
interface continuity
```

Do not run the nonlinear solve until this representation passes a documented derivative benchmark.

---

# Task 5 — Preserve analytic source handling

Retain the milestone-6 source treatment:

```text
G = g^2
G_eta
G_etaeta
```

from analytic formulas.

Retain:

```text
p = G Pbar
Pbar_Y = Phi^2
```

and reconstruct eta derivatives through the factored formulas rather than differentiating `p` as one generic polynomial.

Do not regress to interpolating the narrow source as an unresolved global polynomial.

---

# Task 6 — Re-run the same fixed-point map

Keep the mathematical fixed-point map unchanged.

Do not add an arbitrary outer boundary condition.

Do not add artificial damping to the equations.

If numerical under-relaxation is tested, treat it only as an iteration accelerator:

```text
x_{n+1} = (1-alpha) x_n + alpha F(x_n)
```

and verify that the converged solution satisfies the original equations independently.

If under-relaxation changes which fixed point is obtained or does not converge to the original map residual, reject it.

Try only a small, documented set of `alpha` values if necessary.

---

# Task 7 — Higher precision diagnostic if needed

If the multi-domain representation improves derivative convergence but endpoint growth remains suspiciously tied to roundoff, perform one narrowly scoped higher-precision diagnostic.

Acceptable choices include:

- `longdouble` where meaningful;
- mpmath for small endpoint/local operator tests;
- another controlled higher-precision path.

Do not rewrite the whole solver in arbitrary precision unless evidence justifies it.

The purpose is to distinguish roundoff amplification from loss of fixed-point contraction.

---

# Task 8 — Residual convergence

Evaluate independent original-equation residuals exactly as before.

Report:

```text
angular
axial
pressure / Pbar identity
```

with:

- Linf;
- L2;
- RMS;
- axis slice;
- outer-Y slice;
- eta endpoints;
- eta interior;
- central-source neighborhood.

Use at least three nested eta refinements with radial resolution held fixed first.

Only after eta convergence is demonstrated should radial refinement be revisited.

Acceptance requires decreasing residuals under refinement.

---

# Task 9 — Derivative convergence

On common evaluation grids compare:

```text
Phi_eta
Phi_etaeta
U_eta
U_etaeta
Pbar_eta
Pbar_etaeta
```

and relevant Y derivatives.

Track both global and endpoint-localized differences.

The previously observed explosive second-eta derivative differences must be removed or clearly shown to be converging.

A small field difference with unstable derivatives is still rejection.

---

# Task 10 — Fixed-point stability diagnosis

Estimate whether the iteration is losing contraction.

Without building an enormous full Jacobian unless inexpensive, use practical diagnostics such as:

- ratio of successive iteration increments;
- perturbation-response tests around the best iterate;
- a small Arnoldi/Jacobian-vector estimate if practical;
- comparison of endpoint and interior amplification.

Classify the failure, if it persists, as primarily:

```text
A. representation/differentiation instability
B. floating-point amplification
C. fixed-point map not contractive at this finite tuple
D. unresolved/mixture
```

Do not claim the theorem's contraction estimate applies at these finite parameters.

---

# Task 11 — Initial guesses

Use both:

```text
comparison initialization
flat initialization
```

after the new representation is validated.

If both converge to the same accepted solution, report their final difference.

If they diverge or settle to distinct resolved states, stop and report.

Do not interpret failed starts as multiple continuum branches.

---

# Task 12 — Acceptance and B.13 comparison

Only if the same tuple passes:

- residual convergence;
- derivative convergence;
- interface convergence;
- positivity;
- initialization consistency;

then call it an **accepted finite numerical B.15 core**.

Only then report:

```text
max |U-U_star|
max |U-U_star + Y Z_star/(2 L Lambda)|
max |Phi-f0(Y chi)|
max |Pi-Pi0|
```

and compare with the historical failed-iterate values.

Do not infer a Lambda asymptotic rate from one tuple.

---

# Separate sigma note

Do not change `sigma_star=0.2`.

Carry forward explicitly:

- `sigma_star=0.2` does not satisfy the quantitative B.2 `chi > 0.99` partition;
- a rootwise necessary estimate suggested `sigma_star < ~0.00200285` near one relevant zero;
- that is not sufficient for the theorem condition;
- reducing sigma would narrow the source drastically and is a later numerical challenge.

This issue is separate from whether the current tuple can be solved numerically.

---

# Tests

Retain all existing tests.

Add tests for:

- multi-domain or mapped differentiation accuracy;
- endpoint first/second derivative convergence;
- interface continuity;
- narrow analytic feature resolution;
- source factorization regression;
- fixed-point residual independence;
- any under-relaxation preserving the same fixed-point equation;
- higher-precision endpoint checks if used.

Do not weaken existing failure gates.

---

# Stop conditions

Stop and report if:

- endpoint derivative benchmarks fail;
- interface jumps do not converge;
- source-resolved B.15 residuals still grow under eta refinement;
- fixed-point iteration is demonstrably non-contractive at this tuple;
- higher precision materially changes the endpoint behavior without a stable convergence path;
- two initial guesses approach distinct resolved solutions;
- or resource use becomes unreasonable for this local problem.

Any of these is a valid milestone result.

---

# Do not do yet

Do not:

- change sigma;
- change Lambda;
- change g_peak;
- run the relaxed exterior datum control;
- restore global moments;
- construct stress;
- join the exterior;
- time-integrate Navier–Stokes;
- run 3-D CFD;
- claim theorem admissibility;
- claim physical realizability.

---

# Required report

Append a new dated section to `notes/experiment-log.md`.

Report:

1. instability localization;
2. derivative benchmark results;
3. new eta representation;
4. interface checks;
5. source-factorization regression;
6. iteration history;
7. endpoint/interior residual behavior;
8. derivative convergence;
9. fixed-point stability diagnosis;
10. higher-precision diagnostic if used;
11. initial-guess comparison;
12. whether the same tuple is accepted;
13. if accepted, updated B.13 comparison;
14. separate sigma/B.2 status;
15. runtime and memory.

Then recommend exactly one next gate:

```text
A. Run the original relaxed pressure datum as a nonlinear control.
B. Perform a dedicated sigma_star/B.2 feasibility study.
C. Improve/replace the local nonlinear iteration.
D. Stop because this finite B.15 tuple remains numerically non-credible.
```

Then stop for review.

The central question is:

> **After replacing the unstable global eta representation, does the same
> source-resolved B.15 fixed point converge as a full-domain numerical solution,
> or is the finite fixed-point map itself the next obstacle?**
