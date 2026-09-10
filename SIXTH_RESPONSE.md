# Sixth Milestone Response: Source Resolved, Endpoint Iteration Fails

## Outcome

The sixth milestone reached its required stop. **No nonlinear B.15 core is
accepted.** The known narrow source passes its representation gate, but the
source-resolved fixed-point iteration develops endpoint instability.
This is a numerical-method failure, not evidence of mathematical nonexistence.
All models remain **NOT theorem-admissible**.

Please review the [15-part report](notes/experiment-log.md#sixth-milestone-same-tuple-source-resolution-2026-09-10-utc),
[equation map](notes/equation-map.md#sixth-milestone-same-tuple-representation-identities),
[numerical method](notes/numerical-method.md#sixth-milestone-source-resolved-factored-same-tuple-experiment),
and [reference summary](results/core_representation_not_theorem_admissible_reference/summary.json).
The report links the source/iteration and residual/modal plots.

## Unchanged Model and Numerical Changes

Only the authorized aggressive tuple was used: Lambda=512, g_peak=0.1,
sigma_star=0.2, h=0.005, j0=0.025, Y in [0,4.1], eta in [-1,1].
The pressure datum and previous solver/reference artifacts remain unchanged.
There is no pressure surrogate, parameter change or arbitrary outer boundary.

Implemented matrix-free Chebyshev coefficient transforms and exact pressure
factorization p=G Pbar, G=g^2, Pbar=integral(Phi^2). The iteration uses analytic
G derivatives and integral product identities. Independent residuals instead
differentiate numerical Pbar and reconstruct the original profile sources.
No filtering or mode truncation was introduced.

## Source Benchmark

The independently verified local standard deviations are 0.0041690272 for g
and 0.0029479474 for G, versus 0.0061358846 central spacing at 513 nodes.
Analytic G derivatives pass fourth-order finite-difference tests.

| Eta nodes | Relative Linf G | Relative Linf G_eta | Relative Linf G_etaeta |
| --- | ---: | ---: | ---: |
| 513 | 0.171283 | 0.432436 | 2.24373 |
| 1025 | 0.00426361 | 0.0211153 | 0.534575 |
| 2049 | 9.57439e-9 | 9.56631e-8 | 6.36477e-6 |

The source gate passes at 2049 nodes. Its highest-10% modal-tail ratio is
5.43537e-7, down from 0.596389 at 513. This establishes measured source
convergence, not convergence of the nonlinear solution or its derivatives.

## Resolved Nonlinear Failure

Stage A fixes 65 radial points and starts at 2049 eta points. Comparison
initialization reaches its smallest increment, 3.30747e-7, at iteration 4,
then grows and proposes negative Phi at iteration 10. Flat initialization
reaches 1.08758e-7 at iteration 5 and proposes negative Phi at iteration 13.
Neither reaches the unchanged 1e-11 increment threshold, much less numerical
acceptance. Rejected proposals are not retained as solutions.

At the comparison-start minimum-increment snapshot:

| Independent residual | Global Linf | Central-source Linf |
| --- | ---: | ---: |
| Angular | 0.230462 | 1.58013e-6 |
| Axial | 0.00126511 | 6.69731e-9 |
| Pressure | 2.18645e-14 | 2.18645e-14 |
| Pbar_Y - Phi^2 | 3.45102e-12 | 3.45102e-12 |

Angular and axial maxima occur at Y=4.1, eta=-1. By the last retained
comparison iterate, their global norms reach 31358.6 and 174.287, while
central-source norms remain about 1.85e-6 and 8.55e-9. Endpoint second-eta
derivatives grow enormously. Modal tails also grow; a small tail ratio alone
does not control endpoint differentiation. The report includes L2, RMS,
axis, outer-Y, interior-Y, eta-interior and endpoint diagnostics.

The observed localization supports endpoint amplification as the failure
pattern. Its cause is not uniquely established: roundoff amplification,
loss of discrete contraction, or both remain possible. No higher-precision
or alternative endpoint formulation was tested. Differences between the two
failed starts are not evidence of distinct resolved solution branches.

## Stop, Separate Sigma Audit and Next Gate

The explicit resolved-iteration stop condition prevented further nonlinear
eta refinement, radial refinement and combined confirmation. Derivative
convergence is therefore unestablished. B.13 comparisons were not recomputed;
the earlier correction/error numbers remain historical failed-iterate metrics.

Sigma=0.2 still fails the quantitative B.2 partition. A separate non-solver
root audit finds a near-axis Z_star zero at -0.0011283324342, imposing the
necessary strict rootwise bound sigma<0.00200285138 for chi>0.99 there.
This is not sufficient for a neighborhood or theorem condition. No smaller
sigma was tried; reducing it would make source resolution more demanding.

**Recommendation: C. Improve the local numerical method again.** Please
independently review the factorized residual implementation and propose a
narrow next prompt targeting endpoint-stable differentiation and iteration
at the same tuple. Preserve full-domain acceptance checks; do not discard
endpoints or treat an early minimum increment as convergence. A local or
mapped spectral representation may be worth assessing, but must demonstrate
stable first/second derivatives and interface consistency where applicable.

All **81 tests pass**, retaining the original 75. The final workflow took
11.17 seconds with 547.1 MiB process peak RSS on Daisy, CPU float64.
Passing tests does not override failed equation convergence. No relaxed
nonlinear control, global moment/stress construction, outer matching, time
integration, theorem-admissibility or physical-realizability claim follows.