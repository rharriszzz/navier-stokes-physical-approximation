# First-pass findings: 2026-09-09

## Outcome and scope

Stopped at the Task 6 reporting milestone. A source-grounded Appendix B
COMPARISON is implemented and validated for coordinates and incompressibility.
The exact nonlinear concentrating core and finite-truncation momentum residual
are NOT reconstructed. This is a preliminary geometry/operator milestone,
not completion of the later residual stage or a simulated blowup.

## 1. Implemented equations

- (3.2)/(4.1): implicit similarity geometry, with A=1/2+h and D=1/2-h.
- (B.1): U_star and H_star; (B.2): chi; (B.3): normalized phi_star.
- (B.11): f0; (B.12)-(B.13): explicit angular comparison and zeroth-order U.
- (4.3): physical velocity reconstruction; (4.6)-(4.7): radial average and
  incompressibility reconstruction for this chosen U.
- Section 3.1/(3.11): physical axisymmetric divergence.

The precise code mapping, paper URL, page numbers, and PDF SHA-256 are in
[equation-map.md](equation-map.md).

## 2. Omissions and finite choices

Used h=0.005, Lambda=32, sigma=0.2, j0=0.025, real-axis peak g=1.
These are reproducible exploratory choices, not certified proof parameters.
Omitted Pi0 from (4.31), Z_star and the axial correction in (B.13), nonlinear
profile corrections in (B.15), inner/exterior matching, annular stress,
heat exterior, all cutoffs, oscillations, and higher-order background terms.
No field is multiplied by a finite-window cutoff. Pressure is NOT assigned an
arbitrary zero value. No residual, vorticity, time integration, or 3-D DNS.

## 3. Grids and snapshots

Profile grid: 129x257 in (X,eta), X in [0,0.125], eta in [-0.12,0.12].
Physical divergence grids: 33x65, 65x129, 129x257, including r=0 and all edges.
Snapshots: tau=1, 1e-2, 1e-4, 1e-6. Physical rectangles and complete parameters
are recorded per snapshot in the JSON summary.

## 4. Measured divergence

Analytical divergence of the implemented comparison is zero. Numerical values
below are global maxima INCLUDING one-sided boundaries and the axis.

| Grid | Absolute Linf, tau=1 | Relative Linf | Observed order |
| --- | ---: | ---: | ---: |
| 33x65 | 9.92360e-5 | 2.48090e-5 | - |
| 65x129 | 2.47234e-5 | 6.18084e-6 | 2.00499 |
| 129x257 | 6.17005e-6 | 1.54251e-6 | 2.00253 |

The relative norm divides by the exact radial-divergence scale Linf(v0/q).
It stays approximately 1.54251e-6 on the finest grid at every tau. At tau=1e-6,
absolute Linf is 6.17005 against a gradient scale of 4.000013e6; absolute
cylindrical-volume RMS is 3.41913. Absolute error alone is misleading here.

Independent nonpolynomial manufactured-field absolute errors are
4.21842e-3, 1.05711e-3, 2.64433e-4 on the three grids, approximately second order.

## 5. Concentration and scaling

The prescribed window radius shrinks from 0.5 to 0.0005 (factor 1000).
U_max increases from 1.117992 to 1134.435511 (factor 1014.707933).
Tangential maximum increases from 0.501314 to 537.168127.

Measured log-velocity versus log-radius slopes:

| Quantity | Measured slope | Expected for this comparison |
| --- | ---: | ---: |
| Tangential maximum | -1.010000 | -1-2h = -1.01 |
| Swirl maximum | -1.010000 | -1.01 |
| Axial maximum | -1.010000 | -1.01 |
| Radial maximum | -1.000000 | -1 |
| Total speed maximum | -1.002114 | Mixed finite-tau powers |

Rescaled components collapse in the plots and tests. This verifies the
prescribed formula evaluation, not dynamical sustainability or numerical proof
of a singularity. The radius is a configured window boundary, not an observed
peak. Finite-window energy decreases from 0.0553513 to 6.07064e-5; this
exploratory quadrature is not a global energy budget or a converged energy claim.

## 6. Saved plots and run record

All artifacts are in [results/core-comparison](../results/core-comparison).

- [Physical radial profiles](../results/core-comparison/physical_profiles.png)
- [Rescaled radial profiles](../results/core-comparison/similarity_profiles.png)
- [Physical meridional speed](../results/core-comparison/physical_fields.png)
- [Rescaled meridional tangential speed](../results/core-comparison/similarity_fields.png)
- [Scaling](../results/core-comparison/scaling.png)
- [Divergence convergence](../results/core-comparison/divergence_convergence.png)
- [Finest-grid divergence field](../results/core-comparison/divergence_field.png)
- [Machine-readable summary](../results/core-comparison/summary.json)

The earlier plotting smoke run remains separately in `results/profile-check`.
The seven baseline PNG plots and JSON summary in `results/core-comparison`
are published in Git so these links also work on GitHub and fresh clones.
Other generated runs remain ignored. The summary retains the original run's
commit, dirty status, and source hashes; publishing does not rewrite provenance.

## 7. Test and environment results

`python -m pytest -q`: **45 passed** in 2.36 s.
One environment test, 22 coordinate cases, 10 profile cases, 11 operator cases,
and one end-to-end plotting/summary test. VS Code reported no errors.

Executed on daisy, WSL2 Ubuntu, Python 3.12.14, NumPy 2.5.3, SciPy 1.18.1,
Matplotlib 3.11.1, PyYAML 6.0.3, pytest 9.1.1. CPU-only float64 computation.
The configured Python 3.10 environment was replaced with a project-local 3.12
environment to meet the >=3.11 requirement. An RTX 4060 Ti was detected but
not used. WSL exposed about 7.6 GiB RAM, not the host's full 16 GB.
Base Git commit: `29e462cc98409431011c4caa9f50e19cf31041df`; source changes
were uncommitted. Exact code hashes and all installed versions are in the summary.

## 8. Conditioning and cancellation

- Implicit q inversion was scaled before root finding; no fixed absolute root
  tolerance is applied to a vanishing q.
- Normalized log-swirl avoids computing an enormous phi_star and C separately.
- At the finest late snapshot, divergence subtracts terms of order 4e6.
  Refinement remains second order; roundoff is not yet the observed error floor.
- For h=0.005, q^(2h) at the midplane tau=1e-6 is about 0.871. The formal
  higher-order background parameter is NOT small on these finite scales.
  Omitting the associated terms cannot establish a small momentum residual.
- Small sigma or much larger Lambda can create narrow axial structure. No
  parameter sweep or high-precision conditioning study was performed.

## 9. Implementation ambiguity

The issue is under-specified numerical choices, not a claimed contradiction
in the paper: Pi0 depends on the constructed exterior, and the thresholds
Lambda0, C0, and the coupled parameter hierarchy are not ready-made numerical
values. Sigma's condition depends on Z_star and thus Pi0. A generic pressure
function or zero pressure would silently change the construction.
The published comparison is explicit but has not been shown close to the
nonlinear core for the moderate parameters used here.

## 10. Recommended next experiment

Construct a reproducible exterior pressure datum from (4.31)/Appendix A,
then solve the inner equations (B.15) with those data and compare against the
existing Appendix B comparison under radial/axial refinement. Quantify the
leading tangential residual before and after the correction. Only then attempt
annular matching and a full finite-truncation residual. Do not proceed to time
integration, pulse simulation, or 3-D DNS yet.

---

# Second milestone: source-audit stop, 2026-09-09

## Outcome

Read and committed `SECOND_PROMPT.md` as `0b72ac8` before the audit. Re-read
the project guidance, inspected the existing code/tests/configuration and
published baseline, and read the pressure dependencies directly in the PDF.
The PDF SHA-256 still matches the first-milestone source.

**Stopped after source grounding, before constructing Pi0 or attempting a
nonlinear solve. Tasks 2-4 are not complete.** The requested stop for a
materially under-specified finite construction applies at the proposed
baseline: its h is incompatible with the prescribed exterior hierarchy,
and no alternative admissible finite schedule and normalization have been
established. A conservative axial-correction bound gives an additional reason
not to treat the suggested Lambda sweep as a small-correction regime.

This is not a claim that the paper is inconsistent or that no finite schedule
can be constructed. Section A.2 specifies a family with selectable constants;
Lemma A.5 even removes several otherwise expensive dependencies from Pi0.
What remains unresolved is a concrete admissible, useful finite member of that
family. No arbitrary pressure replacement or silent hierarchy relaxation was made.

## 1. Newly implemented equations

None in production code. The source map now traces (4.31) through (A.5)-(A.23)
and the pressure-preserving heat replacement in (A.39)-(A.43). It also records
(B.1), (B.12)-(B.15) and a derived necessary lower bound. A scalar diagnostic
evaluated that bound; it did not implement Pi0, Z_star for a particular datum,
or a corrected profile. The diagnostic is reproducible from the snippet in
[numerical-method.md](numerical-method.md#independent-necessary-check-before-a-nonlinear-solve).

## 2. Numerical assumptions and unresolved choices

The scheduled-pressure calculation needs `(M_d, P_star, lambda, h, T_f, c_o)`;
the constant-slope Q hold ends at the stopping value Q_p in (A.13), rather
than after an arbitrary chosen length. T_d and T_w are derived. The full
dependency inventory and explicit/existential distinctions are in
[equation-map.md](equation-map.md#schedule-dependency-inventory).

Lemma 4.8 / (A.6) require T_d=exp(M_d)+10, P_star>exp(T_d), and
h<exp(-T_d). Therefore even the weaker necessary conditions are

```text
h < 4.5399929762484854e-5
P_star > 22026.465794806718
```

Every suggested h (0.01, 0.005, 0.0025) fails this necessary schedule test.
Also, h=0.01 is the excluded upper endpoint in the existing comparison API.
This does not invalidate the first milestone's comparison-only calculations;
it prevents treating their config as an admissible exterior/core construction.
Ordinary choices of smoothing functions can be made explicitly, but cannot
repair this particular hierarchy mismatch. No new mathematical configuration
was installed, and the existing comparison configuration was not changed.

## 3. How Pi0 would be obtained

Use the complete scheduled integral (A.21). The angular bumps in (A.11)
preserve its total value and can be omitted from this calculation. Proposition
A.7 shows that the compensated heat replacement also leaves Pi0 unchanged.
There is therefore no need to implement the whole heat exterior or axial
moment closure merely to integrate a specified schedule.

The inner contribution `-(5/2) P_star^2/(1+eta^2)^2` is exact but is only
part of that integral. It must not be substituted for the full Pi0. The
interpolation duration, terminal coefficient and Q event affect the remaining
integral. Numerical Pi0, Pi0_eta, interpolation, and their errors remain
uncomputed. No pressure plot was produced.

## 4. Nonlinear inner correction

Not solved. The exact axial datum needed is
`Z_star=-A(1-2 eta U_star)U_star-H_star U_star_eta-d Pi0_eta+4A eta Pi0`.
The first explicit correction is `-Y Z_star/(2 L Lambda)`. Without Pi0,
assigning numerical values to this formula would conceal an unresolved input.
No optimizer or nonlinear solver was launched, so this is not solver failure.

## 5. Residuals and convergence

No nonlinear residual or convergence result is available. The one scalar
H_star root solve used `brentq`, bracket [-0.01,0], absolute tolerance 1e-15
and default relative tolerance; it converged in 5 iterations and
|H_star(eta0)| was 8.67e-19. This checks
the location used for the analytical bound, not the nonlinear equations.

## 6. Corrected-versus-comparison errors

No epsilon_U, epsilon_E, radial-velocity error, or corrected-field norms
were measured. At eta0<0 with H_star=0, the sign of Pi0_eta and (A.22) give

$$
Z_*(\eta_0)\ge 10A|\eta_0|e^{20}f(\eta_0)^2
-A(1-2\eta_0 U_*)U_*.
$$

For the illustrative h=1e-6, j0=0.025, eta0=-0.005555537737779095,
the lower bound is 1.3475962855866544e7. This h passes only the weakest
necessary test; it is NOT a certified admissible schedule. The use of exp(20)
weakens the bound; it does NOT choose P_star or replace Pi0 by its bound.
Sigma does not enter H_star or this bound.

## 7. Derivative information

Any regular solution of (B.15) must have
`U_Y(0,eta0)=-Z_star/(2 L Lambda)`; the comparison has U_Y=0.
The resulting lower bounds on absolute derivative discrepancy are in the
table below. No derivative-convergence test or second-derivative computation
was performed. A large axis derivative does not by itself prove a large
finite-domain field error, nor does the first explicit term control all
higher corrections at the proposed finite Lambda values.

## 8. Parameter diagnostic, not a solved-profile sweep

| Lambda | Lower bound on abs(U_Y at axis) | Lower bound on first explicit abs(delta U) at Y=4 |
| --- | ---: | ---: |
| 16 | 421123.839 | 1684495.36 |
| 32 | 210561.920 | 842247.679 |
| 64 | 105280.960 | 421123.839 |
| 128 | 52640.480 | 210561.920 |

These are conditional necessary bounds under the published datum constraints,
NOT computed nonlinear profile differences. They show why merely sweeping
Lambda=16..128 cannot make this explicit first correction small while retaining
those constraints and j0=0.025 at this illustrative h. No sigma sweep or
nonlinear h sweep was run. The paper fixes the pressure data before taking
Lambda large; its constants need not be modest in the earlier parameters.

## 9. Resolution and practical cost

No nonlinear grid, iteration history, runtime scaling, or memory estimate was
measured. The bound used float64 arithmetic and a single scalar root solve.
The schedule contains exp(M_d), P_star>exp(exp(M_d)+10), pulse length
13/lambda in log radius, and later radial derivative scale Lambda. These
are clear conditioning/scale-separation risks but do not prove that a
logarithmic, normalized numerical representation is computationally impossible.
No resource exhaustion occurred; an adequate grid cannot yet be specified.

## 10. Does the comparison approach the corrected core accessibly?

Unanswered for the actual nonlinear profile. The suggested baseline is not
an admissible pressure/core parameter set under the stated schedule, and
the necessary-bound diagnostic warns that the first axial correction is far
from small for modest Lambda if the pressure hierarchy is retained. There
is no evidence here of convergence of corrected profiles toward the comparison.

## 11. Is a meaningful momentum residual now possible?

No. Neither a consistent numerical pressure datum nor the nonlinear inner
solution has been produced. Full and leading tangential residuals were not
computed. Existing baseline plots and their provenance were not overwritten.
The required new pressure/correction/residual plots are unavailable because
their inputs were not constructed before this stop.

## 12. Recommended next decision and experiment

Decide explicitly between implementing an admissible Appendix A schedule
with revised h, j0, Lambda and normalization, versus studying a declared
relaxation of the hierarchy as a different finite experiment. Neither choice
should be disguised as the existing validated core. For the faithful path,
the next bounded task is a schedule-only feasibility calculation: choose and
validate the six inputs, Q stopping event, pressure integral and its first two
eta derivatives, then quantify Z_star before budgeting the nonlinear solve.
Keep the current comparison unchanged as a reference, but do not use its
four-parameter config as the missing exterior datum.

### Validation and portability

No source, tests, dependencies, configuration, or result artifacts changed in
this audit; only documentation was extended after the prompt commit. The
existing test suite passed unchanged: **45 passed in 2.65 s** with
`python -m pytest -q`. The reproduction snippet above was executed directly
from the method document and reproduced the table; `git diff --check` passed.
The scalar audit is
NumPy/SciPy-only and its reproduction snippet works without Linux-specific
APIs; actual execution was on Daisy/WSL2, Python 3.12.14. No iMac test is
claimed. Existing macOS memory metadata is incomplete and remains a follow-up
before substantive cross-machine calculations.

---

# Third milestone: relaxed scheduled pressure, 2026-09-10 UTC

## Outcome

Completed the scope of [THIRD_PROMPT.md](../THIRD_PROMPT.md) after direct user
authorization. **All five schedules are relaxed-hierarchy, NOT theorem-admissible.**
Full scheduled pressure and two eta derivatives are validated, Z_star and the
first explicit correction are evaluated, and the run stops for review. No
nonlinear (B.15) solve, momentum residual, time integration, pulse realization,
stress construction, GPU computation, or dimensionalization was attempted.

Pressure-amplitude compression makes the first correction modest at accessible
Lambda, but preserving the schedule lengths still costs **141-196 decades in X**.
This is a useful negative result about this finite schedule architecture, not a
proof that every physically meaningful analogue is impossible.

## 1. Exact equations and implementation

Directly reread PDF pp. 129-130, 133-134, 144, 147 with the recorded source
SHA-256 unchanged. Implemented (A.5)-(A.13) stage architecture and Q stopping,
(A.21) full scheduled integral, analytic differentiation under that integral,
(B.1) Z_star, and the first term `delta U1=-Y Z_star/(2 L Lambda)` from
(B.12)-(B.13). See [equation map](equation-map.md) and
[numerical method](numerical-method.md) for derivations and exact omissions.
The new evaluator is [relaxed_schedule.py](../src/nsblowup/relaxed_schedule.py).

## 2. Explicit relaxation and unchecked construction

The object evaluated is the unbumped scheduled swirl in (A.21), with every
other schedule interval and both infinite ends retained. The angular bumps
are omitted exactly where Lemma A.5 permits omitting them from the pressure
integral. Their realizability at these relaxed parameters is **not** verified.
In particular, the release initial Q is the prescribed moment-corrected value
`(lambda-h)/(1-lambda)`, not Q reconstructed from the unbumped swirl. This
does not establish a globally consistent moment-corrected exterior.

Every tuple violates the explicit `P_star>exp(T_d)` and `h<exp(-T_d)`
inequalities. The sufficiently-large M_d and subsequent sufficiently-small
lambda and h ordering is deliberately not imposed. Unspecified thresholds
are not claimed either satisfied or quantitatively violated. Stress cones,
axial moment closure, angular bump existence, core/exterior matching, complex
neighborhoods, sigma_star, C0(Lambda), and nonlinear remainders remain unchecked.

## 3. Baseline and finite family

Common values: h=0.005, j0=0.025, T_f=64, c_o=0.025. Only one parameter
changes at a time. Label `V` in the table means both explicit hierarchy
violations above, plus unverified asymptotic ordering. The complete per-tuple
satisfied/relaxed/unchecked inventory is in the reference JSON.

| Case (all relaxed, not theorem-admissible) | M_d | T_d | P_star | lambda | h | Hierarchy | Delta y | log10(X_outer/X_R) |
| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| Baseline | 1 | 12.718282 | 2 | 0.2 | 0.005 | V | 324.409099 | 140.889082 |
| P_star=1 | 1 | 12.718282 | 1 | 0.2 | 0.005 | V | 324.409099 | 140.889082 |
| P_star=5 | 1 | 12.718282 | 5 | 0.2 | 0.005 | V | 324.409099 | 140.889082 |
| M_d=2 | 2 | 17.389056 | 2 | 0.2 | 0.005 | V | 329.079874 | 142.917573 |
| lambda=0.1 | 1 | 12.718282 | 2 | 0.1 | 0.005 | V | 451.786100 | 196.208210 |

Algebra retained: all defining lengths, 0<h<0.01, h<lambda<1, positive
P_star, valid j0, positive terminal factor, interpolation and collar slope
bounds, and integrable infinite ends. Geometrically retained: ordered finite
intervals, the four T_w patches, eleven terminal units of zero axial reduction,
and a positive Q stopping hold. No physical radius ratio is formed.

## 4. Schedule validation

Baseline finite lengths, in paper order:

| Stage | Local log length |
| --- | ---: |
| Inner slope transition | 1 |
| Axial reduction | 12.718282 |
| Transition to -lambda | 1 |
| Intermediate power law | 96.566275 |
| Axial-pulse swirl interval (no pulse realization) | 65 |
| Removal of eta dependence | 64 |
| Angular-bump interval (bumps omitted) | 48.283137 |
| Release down | 1 |
| Release hold at l=-1 | 21.193269 |
| Release up | 1 |
| Q stopping hold | 9.648136 |
| Terminal collar | 3 |

Across all cases, C2 joins of log E have maximum value discrepancy
2.85e-14; first/second local-y derivative discrepancies are zero at the
tested joins. Flat ends are explicit in (A.5); this checks C2 numerically,
not infinitely many derivative orders. All stage lengths are positive and
finite log amplitudes give positive E. Baseline sampled log E ranges from
-239.1333 to 0.730767; the most negative family sample is -288.0752.
Neither amplitudes nor totals overflow in this family. A separate test at
lambda=0.05 verifies logarithmic retention of a tail integral below float64's
normal amplitude range; it is not an extra interpreted family run.

T_f=64 gives interpolation slope range [-0.2866434,-0.2] for lambda=0.2,
within [-lambda-0.1,-lambda]. The measured maximum f_o'/f_o is 0.000500004,
below h/4=0.00125; endpoint roundoff is below 5e-18. The conservative bound
used to choose c_o also passes. Reserved patches fit because T_w>25.

Baseline Q before the stopping hold is 13.5755211792, Q_p is
0.000919549105438, and the derived hold length is 9.64813604875. The collar
ends at Q=1.30e-17. Independent integrating-factor endpoint checks pass.
At lambda=0.1 the hold length is 9.64188987965; it is not reused or guessed.
Tightening tolerances changes total spans by at most 5.69e-14.

## 5. Full pressure and quadrature convergence

Analytic constant-slope integrals and both infinite ends are combined with
adaptive transition quadrature. Each positive stage contribution has its own
log scale. Tightening relative/absolute tolerances from 1e-10/1e-12 to
1e-12/1e-14 changes Pi0 and its derivatives by at most 2.68e-14 relative to
their component maximum (denominator at least one). The largest absolute
second-derivative change is 8.53e-12 in the P_star=5 case. Per-stage log
integrals change by at most 3.42e-13, so small late stages are checked as
well as the dominant total. These are observed differences, not rigorous
quadrature error bounds. Independent direct scalar integration also passes.

At eta=0 the baseline squared-swirl integral contributions are:

| Stage | Integral of E^2 dy |
| --- | ---: |
| Infinite inner branch | 20 |
| First slope transition | 3.83570165597 |
| Axial reduction | 2.68127215142 |
| Transition to -lambda | 4.90988402666e-6 |
| Intermediate power interval | 1.72814893172e-6 |
| Axial-pulse swirl interval | 3.34272618191e-65 |
| Eta interpolation | 1.00763431688e-104 |
| Infinite outer tail | 1.93694971641e-208 |

All intervening late stages are included and logged in the JSON, not discarded.
The datum is -1/2 times the complete sum. The inner contribution alone would
give Pi0(0)=-10 instead of -13.2584902, a material difference. Early dominance
is an observed consequence of the full calculation, not a substituted model.

## 6. Derivative, symmetry, and grid checks

Centered differences of pressure at eta steps 0.004, 0.002, 0.001 converge
at order approximately 2 for both derivatives in every case. At the finest
step the relative maximum errors are approximately 1.93e-6 for Pi0_eta and
1.50e-6 for Pi0_etaeta. Baseline absolute errors are 2.65e-5 and 7.95e-5.
The independent second derivative is computed from pressure values, not from
the analytic first derivative. Pi0 is even and eta Pi0_eta is strictly
positive at every nonzero grid point; Pi0_eta(0)=0 by the analytic formula.

Main grids use 513 eta points on [-1,1]; a 1025-point comparison changes the
largest sampled Z_star by at most 1.06e-4, and the Lambda=32 correction
maximum by at most 1.28e-5. Maxima below are sampled, not certified continuous
suprema. No extrapolation to a nonlinear profile is implied.

## 7. Pressure results

| Relaxed case | max abs(Pi0) | max abs(Pi0_eta) | max abs(Pi0_etaeta) |
| --- | ---: | ---: | ---: |
| Baseline | 13.2584902 | 13.7252027 | 53.0339609 |
| P_star=1 | 3.31462256 | 3.43130068 | 13.2584902 |
| P_star=5 | 82.8655639 | 85.7825171 | 331.462256 |
| M_d=2 | 13.2584909 | 13.7252035 | 53.0339637 |
| lambda=0.1 | 13.2584905 | 13.7252030 | 53.0339621 |

Changing P_star scales the entire scheduled pressure exactly as P_star^2.
Changing M_d or lambda here barely changes pressure, because their effects
occur after substantial amplitude decay, despite increasing the radial span.

## 8. Z_star and the negative transport root

All cases use eta0=-0.005561716315493002 from H_star=0, with a checked
absolute root residual below 1e-14. This is distinct from evaluating at eta=0.

| Relaxed case | Pi0(eta0) | Pi0_eta(eta0) | Z_star(eta0) | max abs(Z_star) |
| --- | ---: | ---: | ---: | ---: |
| Baseline | -13.2576700 | -0.294932476 | 0.442478484 | 25.4776976 |
| P_star=1 | -3.31441750 | -0.0737331189 | 0.109576839 | 10.9486111 |
| P_star=5 | -82.8604376 | -1.84332797 | 2.77279000 | 127.307995 |
| M_d=2 | -13.2576707 | -0.294932491 | 0.442478507 | 25.4776986 |
| lambda=0.1 | -13.2576703 | -0.294932482 | 0.442478494 | 25.4776980 |

Z_star at the root is positive for these tuples. Its root value is much
smaller than its maximum over eta; using only the root would understate the
domain-wide first correction.

## 9. First explicit correction at Y=4

These are **first-term diagnostics only**, not solved-profile differences or
controlled finite-Lambda error estimates. No C0(Lambda) or nonlinear remainder
bound has been established. Their exact 1/Lambda scaling is algebraic.

| Relaxed case | max abs(delta U1), Lambda=32 | 128 | 512 | 2048 |
| --- | ---: | ---: | ---: | ---: |
| Baseline | 1.59524812 | 0.398812030 | 0.0997030075 | 0.0249257519 |
| P_star=1 | 0.685606110 | 0.171401527 | 0.0428503818 | 0.0107125955 |
| P_star=5 | 7.97067427 | 1.99266857 | 0.498167142 | 0.124541786 |
| M_d=2 | 1.59524818 | 0.398812046 | 0.0997030115 | 0.0249257529 |
| lambda=0.1 | 1.59524815 | 0.398812037 | 0.0997030092 | 0.0249257523 |

| Relaxed case | abs(delta U1 at eta0), Lambda=32 | 128 | 512 | 2048 |
| --- | ---: | ---: | ---: | ---: |
| Baseline | 0.0276549138 | 0.00691372845 | 0.00172843211 | 0.000432108028 |
| P_star=1 | 0.00684855458 | 0.00171213864 | 0.000428034661 | 0.000107008665 |
| P_star=5 | 0.173299428 | 0.0433248571 | 0.0108312143 | 0.00270780357 |
| M_d=2 | 0.0276549153 | 0.00691372882 | 0.00172843220 | 0.000432108051 |
| lambda=0.1 | 0.0276549144 | 0.00691372861 | 0.00172843215 | 0.000432108038 |

The relative measure divides each domain maximum by
`max(1,max|U_star|)=4.025`, common to all cases. Baseline relative values are
0.396335, 0.0990837, 0.0247709, 0.00619273. For P_star=1 they are
0.170337, 0.0425842, 0.0106461, 0.00266151; for P_star=5 they are
1.98029, 0.495073, 0.123768, 0.0309421. The M_d and lambda variants agree
with baseline at these displayed relative precisions; full values for every
Lambda and tuple are saved in the JSON.

## 10. Logarithmic radial scale separation

The most compressed tested geometry still needs Delta y=324.409099, or
140.889082 decades in X. Lowering lambda to 0.1 increases this to
196.208210 decades without materially improving pressure or the correction.
The long intermediate interval, pulse interval, eta-removal interval and
angular adjustment interval dominate the span; tiny pressure contribution
does not permit deleting their geometric cost while claiming the same schedule.
At fixed q, r scales as sqrt(X), so even the shortest schedule corresponds
to about 70.44 decades in radius. This statement concerns relative geometry,
not dimensional fluid validity or dynamically achieved concentration.

## 11. Separate exact-hierarchy bound reference

The earlier necessary-bound calculation is reproduced unchanged in the run
summary. It is **not an evaluated schedule** and is not another relaxed case.
At illustrative h=1e-6, j0=0.025 it gives
`Z_star(eta0) >= 1.3475962855866544e7`, using the weaker necessary
P_star^2>exp(20). The associated first-term lower bounds at Y=4 are:

| Lambda | Conditional lower bound on abs(delta U1 at eta0) |
| --- | ---: |
| 16 | 1684495.36 |
| 32 | 842247.679 |
| 64 | 421123.839 |
| 128 | 210561.920 |

These are neither nonlinear field errors nor an admissible tuple certificate.
The h differs from the relaxed run. They establish the scale of the exact
hierarchy reference, not a controlled matched-parameter comparison.

## 12. Review decision and reproducibility

**Stop before (B.15).** For an isolated core-only numerical diagnostic,
P_star=1 or 2 and Lambda=128..512 look worth considering after review:
their explicit corrections are modest. For the stated goal of a physically
useful full schedule, no tested member is yet convincing; retained radial
separation remains physically extreme. Removing or shortening additional
schedule intervals would be a new scientific model decision, not an
implementation adjustment authorized by this milestone. Small delta U1 alone
does not establish convergence, dynamics, or realizability.

Reference run: 2026-09-10T00:33:36 UTC on Daisy/WSL2, Intel i7-14700F,
x86_64, Python 3.12.14, CPU float64. WSL reported 7,983,812 kB total and
4,875,732 kB available RAM at metadata capture. The five-case workflow took
8.46 seconds; no time steps or GPU work were performed. No iMac run is
claimed. Its metadata path has a mocked unit test only.

The run records parent commit `28655507d647dcc31aa81e30ee4c9cb15b17f3cb`
plus dirty-worktree status and source/config/test SHA-256 hashes. That commit
alone does not contain the implementation; hashes identify the actual run
sources. New implementation has not been automatically committed or pushed.
Earlier comparison artifacts are untouched.

Reproduce in the configured environment, using a new output directory:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python scripts/relaxed_pressure.py
```

Validation: **61 tests passed in 6.53 s**, including all prior 45 tests,
fourteen new schedule/pressure/correction tests, a workflow/no-overwrite test,
and the mocked macOS metadata test. Editor diagnostics report no new errors.
All three generated plots were inspected for readable labels and correct
nonblank content.

Artifacts: [summary and full validation](../results/relaxed_not_theorem_admissible_reference/relaxed_not_theorem_admissible_summary.json),
[pressure and derivatives](../results/relaxed_not_theorem_admissible_reference/relaxed_not_theorem_admissible_pressure.png),
[Z_star and first correction](../results/relaxed_not_theorem_admissible_reference/relaxed_not_theorem_admissible_correction.png),
[logarithmic schedule](../results/relaxed_not_theorem_admissible_reference/relaxed_not_theorem_admissible_log_schedule.png).
The NPZ arrays are local, reconstructible output and remain ignored. Request
scientific review of this finite-pressure versus scale-separation tradeoff
before any nonlinear correction implementation.

---

# Fourth milestone: schedule compression, 2026-09-10 UTC

## Outcome and provenance

The user supplied [FOURTH_PROMPT.md](../FOURTH_PROMPT.md) and authorized the
archive/publish/execute/review pattern. The unchanged prompt and exchange
receipt were committed and pushed as `be32c4b` before execution. Source roles,
support thresholds and forfeited estimates were audited before mathematical
code changes. This is a **modified finite model, NOT theorem-admissible**.
The original RelaxedSchedule, its config and published outputs are unchanged.

Ten one-at-a-time compressions and three combined cases were evaluated against
the baseline. The most compressed case reduces separation from **70.444541
to 8.777770 radius decades** with relative changes of order 1e-11 in local
data. This does not preserve the full Appendix A construction. No B.15 solve,
stress realization, time integration, dimensionalization or GPU work was done.

## 1. Stage-condition dependency matrix

The complete twelve-stage matrix is in [compression-audit.md](compression-audit.md).
It identifies paper equations/pages and P/M/S/R/T roles for every stage, with
the distinction between moment closure, S-pulse amplitude, conditional Q
matching, stress estimates, four reserved patches, heat compensation and
higher-order/background/phase-averaged corrections. Directly read Appendix
A.2-A.5, pp129-137, A.1-A.3 pp127-128, and B.1-B.3 pp144-147 from the
same PDF digest. No dominant length formula remains ambiguous for this
experiment; optimal finite estimates and actual moment/stress conditions
remain unchecked rather than being assumed.

## 2. Hard constraints and margins

- T_w>25 keeps the four paper-positioned patches inside the interval. The
  factor 60 also supplies amplitude/transient suppression in A.14 and A.27;
  it is not merely reserved blank space.
- The principal pulse ends at 11/lambda. The two .3-wide axial bumps fit
  strictly after it if T_p>11/lambda+3.15=58.15. Room for these bumps does
  not retain the exponential smallness or the A.19 amplitude-root argument.
- Two .3-wide angular bumps fit at the stated centers if T_a>3.15. The
  original 30 log(1/lambda) also suppresses the r_I discrepancy for the
  nonlinear pressure-preserving correction. Lemma A.2 smallness is unchecked.
- T_f>=80 log(2)=55.45177444 preserves A.10's slope bound. T_f=56 passes;
  T_f=8 deliberately fails it while retaining smooth eta removal.
- Shortening the release hold replaces h^8 and h^6 by exp(-2T) and
  exp(-1.5T). The Q stopping hold is recomputed, never overridden.

The paper's moment-weight slopes both exceeding .4 already fails at the
relaxed lambda=.2 (the slopes are .3 and .1). Thus even the baseline's
principal supports are not a certificate of the small-correction argument.
All earlier relaxed hierarchy violations continue to apply.

## 3. One-at-a-time results

All use M_d=1, P_star=2, lambda=.2, h=.005, j0=.025, c_o=.025 and
the unchanged reference unless the named length is overridden. Each entry
has full original/modified/ratio and sacrifice metadata in the summary.
For every OAT case the computed relative changes in Pi0, both derivatives
and Z_star round to zero in the tightened float64 totals. Report this as
**unresolved at the observed numerical precision**, not exactly invariant.

| Case | Modified log length | Delta y | X decades | Radius decades | Additional sacrificed structure |
| --- | ---: | ---: | ---: | ---: | --- |
| Baseline | none | 324.409099 | 140.889082 | 70.444541 | None beyond relaxed baseline's unverified guarantees |
| intermediate_26 | 26 | 253.842825 | 110.242538 | 55.121269 | Paper transient/amplitude margins; reserved supports fit |
| intermediate_1 | 1 | 228.842825 | 99.385176 | 49.692588 | Also four reserved supports |
| pulse_59 | 59 | 318.409099 | 138.283315 | 69.141657 | Original pulse integral/separation estimates; supports fit |
| pulse_1 | 1 | 260.409099 | 113.094235 | 56.547117 | Also main pulse and separated axial bump supports |
| angular_4 | 4 | 280.125962 | 121.657160 | 60.828580 | lambda^28 discrepancy estimate; bump supports fit |
| angular_1 | 1 | 277.125962 | 120.354276 | 60.177138 | Also angular bump supports |
| interpolation_56 | 56 | 316.409099 | 137.414726 | 68.707363 | Original duration; explicit slope bound retained |
| interpolation_8 | 8 | 268.409099 | 116.568591 | 58.284295 | Also A.10 slope bound |
| release_half | 10.596635 | 313.170118 | 136.008054 | 68.004027 | Original h^8/h^6 suppression estimates |
| release_2 | 2 | 303.272537 | 131.709589 | 65.854795 | Same estimates, more aggressively |

Corrections at Lambda=128 and 512 are 0.398812030180 and 0.099703007545
to displayed precision for all OAT cases. Intermediate and pulse intervals
are adjacent with identical constant slopes and eta factors: they can trade
length without changing the combined exponential segment except at its far
end. That is one reason the OAT pressure sensitivity is so small.

## 4. Combined candidates

All stages remain positive; no pulse implementation or zero-length deletion
was introduced. Length columns are in local log radius. All fixed transitions
and early axial reduction remain unchanged; Q hold is derived separately.

| Candidate | T_w | T_p | T_a | T_f | Release hold | Delta y | X decades | Radius decades |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| principal_support | 1 | 59 | 4 | 56 | 2 | 149.423125 | 64.893639 | 32.446819 |
| local_slope | 1 | 1 | 1 | 56 | 2 | 88.423125 | 38.401675 | 19.200838 |
| aggressive | 1 | 1 | 1 | 8 | 2 | 40.423125 | 17.555540 | 8.777770 |

The first label means support-aware, NOT moment-solved. The second is an
A.21-style local-data experiment, NOT an exactly pressure-preserving edit.
The last is a diagnostic aggressive analogue, NOT a physical realization.

## 5. Sacrifice matrix

| Property | Baseline | principal_support | local_slope | aggressive |
| --- | --- | --- | --- | --- |
| Positive smooth swirl, same formulas, convergent infinite ends | Retained | Retained | Retained | Retained |
| Four paper-positioned reserved patches | Fit | Lost | Lost | Lost |
| Main axial pulse and separated end-bump supports | Fit | Fit | Lost | Lost |
| Principal angular-bump supports | Fit | Fit | Lost | Lost |
| A.10 interpolation slope bound | Retained | Retained | Retained | Sacrificed |
| Original h^8/h^6 release factors | Retained | Lost | Lost | Lost |
| Published lambda-power suppression estimates | Unverified at relaxed parameters | No longer asserted | No longer asserted | No longer asserted |
| Scalar Q endpoint identities with imposed initial Q | Verified | Verified | Verified | Verified |
| Actual M,J,S,I moments and pressure-preserving bumps | Unchecked | Unchecked | No supporting construction asserted | No supporting construction asserted |
| Stress cone, heat compensation, inner matching, later corrections | Unchecked | Not asserted | Not asserted | Not asserted |
| Theorem admissibility | No | No | No | No |

The full per-case [condition table](../results/compressed_not_theorem_admissible_reference_v2/compressed_not_theorem_admissible_conditions.md)
and per-override JSON metadata preserve this distinction. A "yes" support
flag is geometry, not proof of coefficient existence or acceptable stress.

## 6. Geometry targets and constraints

- **30 radius decades:** local_slope reaches 19.20. Retaining the original
  principal pulse/bump supports AND the eta slope bound cannot reach 30
  under the fixed early stages and conditional Q construction: conservative
  lower bound 30.415393. Derivation in the source audit uses nonnegative
  Q source and at most exp(-2) damping across the two unit ramps; the
  required Q hold is at least 3.598005 log units.
- **10 radius decades:** aggressive reaches 8.78, but sacrifices the eta
  slope bound. Even with the other adjustable lengths and Q hold set to
  zero as a lower-bound argument, retaining that slope bound costs at least
  16.322970 radius decades. This is not a proposed zero-length run.
- **3 radius decades:** impossible in this length-only scope. The unchanged
  early stages, two release ramps and collar alone cost 4.281770 radius
  decades, before any adjustable interval or Q hold. No unrelated parameter
  or formula was altered to force the target.

These are bounds for the stated retained structure, not general impossibility
claims for every possible finite model. The aggressive case saves 61.666771
radius decades, about 87.54% of the reference span, yet 8.78 decades still
does not imply a laboratory-scale flow.

## 7. Local data and first corrections

Changes use baseline Linf denominators (at least one for derivatives and Z).
The original Pi0 and derivative maxima exceed one. Grid: 513 points on
[-1,1]. Maxima are sampled, not certified continuous suprema.

| Candidate | Relative Pi0 change | Relative Pi0_eta change | Relative Pi0_etaeta change | Relative Z_star change |
| --- | ---: | ---: | ---: | ---: |
| principal_support | unresolved (rounded 0) | unresolved | unresolved | unresolved |
| local_slope | 5.36e-16 | 5.18e-16 | 5.36e-16 | 5.58e-16 |
| aggressive | 1.61147e-11 | 2.23900e-11 | 2.37055e-11 | 1.45065e-11 |

Local_slope differences are below the observed numerical refinement floor
and are unresolved. Aggressive differences exceed it; their last digits are
not certified. Aggressive maxima are 13.2584902225006 for abs(Pi0),
13.7252027360771 for abs(Pi0_eta), 53.0339608895996 for abs(Pi0_etaeta),
and 25.4776976095575 for abs(Z_star). Both pressure sign structure and the
positive Z_star at the negative H_star root survive these tests.

| Model | max abs(delta U1), Lambda128 | Lambda512 | Root abs(delta U1), Lambda128 | Lambda512 |
| --- | ---: | ---: | ---: | ---: |
| Baseline | 0.398812030180 | 0.099703007545 | 0.006913728454 | 0.001728432113 |
| Aggressive | 0.398812030174 | 0.099703007544 | 0.006913728454 | 0.001728432113 |

The maximum absolute correction change over eta is 5.78e-12 at Lambda128
and 1.45e-12 at Lambda512. Relative to max abs(U_star)=4.025, aggressive
corrections are 0.0990837342 and 0.0247709336. These remain **first explicit
terms only**, not computed nonlinear errors or evidence of concentration.

## 8. Q and numerical validation

Q release initial value remains (lambda-h)/(1-lambda)=0.24375, conditional
on A.11. It is NOT the global moment of the unbumped compressed field.
Q_p=0.000919549105438 is unchanged because h and the collar are unchanged.
The release_2 and combined cases have Q_start=1.96342734277 and a derived
Q hold of 7.70484291584, compared with 13.5755211792 and 9.64813604875
for baseline. The half-release Q hold is 9.005790. All collar endpoints
are approximately 1.30e-17; independent integrating-factor checks pass.

Every case retains C2 joins with maximum log-value mismatch 2.85e-14 and
zero measured derivative mismatch at joins. Pressure and derivative relative
changes on tightening quadrature/ODE tolerances are at most 2.68e-14;
per-stage log-integral changes are at most 1.31e-12. Analytic derivatives
agree with independent pressure finite differences at second order; finest
relative errors are about 1.93e-6 and 1.50e-6. Symmetry and strict sign tests
pass. No instability, Q failure, or order-one local-data change occurred.

For T_f=8 the measured minimum l is -0.893147, below the required -0.3.
This is an explicit sacrificed check, preserved as false in the summary,
not hidden by changing the validation criterion or slope formula. T_f=56
has minimum -0.299021 and passes. All other required checks must pass.

## 9. Remaining dominant geometry

For principal_support, T_p=59 and T_f=56 dominate. For local_slope, T_f=56
dominates. In aggressive, T_d=12.718282, T_f=8 and Q hold=7.704843 together
account for about 70.3% of Delta y. Further substantial compression would
need to revisit early axial reduction, the eta-removal condition, or the
terminal construction, beyond the present five-length audit. Tiny pressure
change alone says nothing about whether the missing global moments or stress
can be restored on the remaining short supports.

## 10. Suitability for a core-only B.15 diagnostic

**Recommendation B: use the aggressive compressed datum for a later core-only
nonlinear diagnostic, with the original relaxed datum as a control.** It
reduces geometry dramatically while preserving the tested local pressure,
derivatives, sign structure and Z_star to approximately 1e-11. The retained
factorization E=c(y)f^theta and integrable ends support the same analytic
datum argument; no new pressure fit was introduced.

This recommends a numerical experiment, not invoking Proposition B.2 with
certified thresholds. Sigma_star, the analytic neighborhood, C0(Lambda),
nonlinear residual convergence and finite-Lambda accuracy still need their
own validation. Near-identical datum should not be sold as a dynamically
validated or globally realizable compressed mechanism. Any claim about an
actual exterior must first address missing moment closure and stress; scalar
conditional Q alone cannot supply those missing facts.

## 11. Next milestone and review stop

Stop here for review, as requested. A next prompt could authorize only a
core-only B.15 formulation and convergence experiment using this specific
compressed datum, with a baseline-datum control and no global matching claims.
Alternatively the scientific review may prioritize actual angular moment and
stress compatibility; that is a different next task, not performed here.

Run date 2026-09-10T00:59:13 UTC, Daisy/WSL2, Python 3.12.14, CPU float64,
x86_64 i7-14700F. Fourteen total cases took 18.98 seconds. WSL reported
7,983,812 kB total and 5,069,128 kB available RAM. No iMac run is claimed.
The summary records parent commit `be32c4b`, dirty status, full configs,
versions and source hashes; that parent alone does not contain new code.

Validation: all **70 tests pass**, including the original 61, eight new
model tests and one workflow/no-overwrite test. Unit compression reproduces
RelaxedSchedule exactly; invalid lengths and Q overrides fail explicitly.
Editor diagnostics show no errors. All three plots were inspected; the first
run's crowded labels were fixed and the final reference regenerated to a
new directory, preserving the initial output rather than overwriting it.

Reproduce with `.venv/bin/python scripts/compressed_not_theorem_admissible.py`
and `.venv/bin/python -m pytest -q`. No time step is taken. New results and
implementation are local pending review/publication; only the prompt receipt
has been published at this point. Earlier baseline artifacts are untouched.

Final artifacts: [summary and validation](../results/compressed_not_theorem_admissible_reference_v2/compressed_not_theorem_admissible_summary.json),
[cumulative stage geometry](../results/compressed_not_theorem_admissible_reference_v2/compressed_not_theorem_admissible_stages.png),
[Pi0 and Z_star comparison](../results/compressed_not_theorem_admissible_reference_v2/compressed_not_theorem_admissible_local_data.png),
[local error versus geometry saved](../results/compressed_not_theorem_admissible_reference_v2/compressed_not_theorem_admissible_tradeoff.png),
[condition table](../results/compressed_not_theorem_admissible_reference_v2/compressed_not_theorem_admissible_conditions.md).