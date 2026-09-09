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
Generated artifacts are ignored by Git. These links work locally; regenerate
plots on a fresh clone. The committed-sized record is this report.

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