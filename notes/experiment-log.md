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