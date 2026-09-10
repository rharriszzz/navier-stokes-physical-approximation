# First-pass numerical method

## Scope

This code evaluates the explicit Appendix B comparison, not the nonlinear
profile of Proposition B.2 or the completed flow. The comparison is useful for
checking geometry and operators. Its error relative to the actual core is not
numerically bounded. See [equation-map.md](equation-map.md).

All PDE quantities remain nondimensional with viscosity-one reference units.
No fluid properties, time integrator, pressure, residual, or stress are supplied.

## Coordinates

Input time is positive tau rather than t to avoid cancellation in 1-t.
For fixed tau, q=tau/(1-eta^2), r=sqrt(2qX), and z=q^D eta.
The inverse uses the implicit equation q-z^2 q^(2h)=tau, not q=tau.

Set b=|z|^(1/D), reference=max(tau,b), and y=q/reference. The scaled
equation is y-(b/reference)^(1-2h)y^(2h)-tau/reference=0. Its root is
bracketed by 1 and 3 for 0<h<0.01. Fixed 56-step bisection avoids an
absolute root tolerance that would fail as tau shrinks. All arrays are float64.
Round trips and the implicit identity are tested down to tau=1e-12 and |eta|=0.99.
Machine-extreme coordinates and eta indistinguishable from +/-1 are not validated.

## Comparison and normalization

Use the paper's U_star=4 eta+j0, H_star=D eta+(1-eta^2)U_star,
chi=H_star^2/(H_star^2+sigma^2), and zeta=-L H_star/(H_star^2+sigma^2),
where L=1-2h eta^2. Let eta0 be the unique real zero of H_star in (-1,0).
Instead of forming the potentially enormous phi_star and dividing by C, evaluate

$$
g(\eta)=g_{\rm peak}\exp\left(\Lambda\int_{\eta_0}^{\eta}\zeta(w)\,dw\right).
$$

This corresponds to C=phi_star(eta0)/g_peak in (B.3), with C>1 for these
parameters. It normalizes the maximum on the REAL interval, not the complex
neighborhood in (B.16); it does not certify C>=C0(Lambda). SciPy `quad` uses
absolute/relative tolerances 1e-12 for the integral; error in the exponent is
multiplied by Lambda. Extremely small sigma or large Lambda may underresolve
the axial swirl or underflow; such regimes have not been tested here.

Use f0(s)=0F1(;2;-s/2), tested against the series in (B.11). Set
E=sqrt(2X)g(eta)f0(Lambda X chi), U=U_star. This keeps the explicit zeroth-order
comparison and omits the corrections in (B.12)-(B.15), including the first
axial correction, which depends on the unavailable exterior pressure datum.
The evaluation domain is 0<=Lambda X<=4.1; the configured window ends at 4.

## Exact incompressibility of this comparison

Since U is independent of X, its radial average equals U. Equation (4.7) gives

$$
v_0=\frac{2A\eta U-4(1-\eta^2)}{L},\qquad
u_r=\frac{r}{2q}v_0,\qquad u_z=q^{-A}U.
$$

Thus partial_r u_r+u_r/r=v0/q and, by (4.2), partial_z u_z=-v0/q.
Their sum is exactly zero analytically, independent of the chosen swirl.
No assumption about momentum balance is involved.

The numerical divergence is evaluated on uniform physical (r,z) grids using
centered second-order differences in the interior and second-order one-sided
differences at the edges. At r=0, u_r/r is replaced by partial_r u_r, justified
by smooth odd radial velocity. Inputs with nonzero u_r on the axis are rejected.
The caller must supply a regular axisymmetric field, including even u_z at the
axis. No artificial epsilon radius is used.

All errors include boundaries and the axis. The relative error is
Linf(div u)/Linf(v0/q); absolute, axis, and cylindrical-volume RMS errors are
also saved. Manufactured tests cover a smooth nonpolynomial divergence-free
field and polynomial fields with zero and nonzero divergence.

## Windows, quadrature, and metrics

Profile plots sample uniform (X,eta), 129x257 by default, on
[0,4/Lambda] x [-0.12,0.12]. The physical window is curved because q depends
on eta. For divergence, separate uniform physical rectangles use
0<=r<=sqrt(2 tau Xmax) and |z|<=q(eta_max)^D eta_max; these stay inside the
profile window. Refinement grids are 33x65, 65x129, 129x257.

`r_core` is the midplane radius of the prescribed X=Xmax boundary, NOT a
detected swirl maximum or an advected material boundary. Extents therefore
scale as tau^(1/2) radially and tau^D axially by construction. Tangential
maximum scales as tau^(-A), giving radius slope -2A. Radial maximum scales
as tau^(-1/2), so total speed need not have slope -2A at finite tau.

Window energy is 1/2 integral |u|^2 dV. Under the fixed-tau map,
r dr=q dX and dz/deta=q^D L/(1-eta^2). Hence the implemented energy is

$$
E_{\rm window}=\pi\int\!\int |u|^2
q^{1+D}\frac{L}{1-\eta^2}\,dX\,d\eta.
$$

Nested trapezoidal quadrature gives an exploratory finite-window diagnostic;
energy accuracy has not been independently converged. This is neither global
energy nor a conservation test on a material domain. Vorticity is not computed.

## Reproducibility and stopping

Each run saves the complete configuration, runtime package versions, machine,
WSL kernel, CPU, available RAM, detected GPU (unused), float precision, Git
commit/status, and hashes of source/config/test files. Uncommitted source is
identified honestly by the dirty status and hashes. New run directories cannot
overwrite earlier output. Generated files are ignored by Git except for the
selected baseline PNG plots and summary in `results/core-comparison`.
Compact findings are preserved in [experiment-log.md](experiment-log.md).

No time step is taken. Invalid input or a nonfinite field raises an error.
Successful runs record `all configured snapshots evaluated`. Failed runs raise
before a success summary is written; partial plots can remain in their directory.

## Second milestone: source-audit stop (2026-09-09)

No nonlinear numerical formulation has been adopted or implemented. The source
audit encountered a material gap between the proposed finite baseline and the
exterior schedule required for its pressure data. The existing solver-free
comparison implementation and all baseline artifacts are unchanged.

### What the pressure calculation would require

The exact shortcut is (A.21), not a generic pressure fit: integrate the full
scheduled squared swirl over logarithmic radius, omitting only the
pressure-preserving angular bumps. The schedule in Section A.2 is explicit
once its finite choices and stopping event have been fixed. For example, its
reference inner contribution integrates analytically to
`-(5/2) P_star^2/(1+eta^2)^2`; all later intervals and the infinite tail must
still be included. The scheduled tail can also be integrated analytically
once its starting amplitude is known. Log-amplitude storage and stage-local
integration would be important, since physical radii can be enormous.

Required finite choices are `(M_d, P_star, lambda, h, T_f, c_o)` with the
constraints and Q stopping rule enumerated in [equation-map.md](equation-map.md).
Selecting these choices was authorized, but installing an inconsistent tuple
would not provide the required datum. In particular, the existing h=0.005
cannot satisfy the necessary condition h<exp(-10), regardless of the other
choices. No value of Pi0 or Pi0_eta has been supplied to the code, and no
quadrature convergence, interpolation consistency, or pressure smoothness test
has been claimed.

### Independent necessary check before a nonlinear solve

At the negative zero eta0 of H_star, the term -H_star U_star_eta in (B.1)
vanishes. Because Pi0_eta<0 there, -d Pi0_eta is nonnegative. The remaining
pressure term has the rigorous lower bound given by (A.22). This yields the
Z_star bound in the equation map without specifying a pressure function.
Use P_star^2>exp(20) to obtain a deliberately weak, schedule-independent bound.

For any regular solution of (B.15), at X=0 the terms proportional to X vanish,
so S_n=Z_star and

$$
U_X(0,\eta_0)=-\frac{Z_*(\eta_0)}{2L(\eta_0)},\qquad
U_Y(0,\eta_0)=-\frac{Z_*(\eta_0)}{2L(\eta_0)\Lambda}.
$$

The existing comparison has U_X=U_Y=0. Thus the lower bound also diagnoses
a potentially very large absolute first-derivative discrepancy. It does NOT
bound the actual finite-Y nonlinear field error. Likewise
`Y Z_star/(2 L Lambda)` is the size of the first explicit term in (B.13),
not an estimate justified at Lambda=16..128 when the asymptotic hypotheses
have not been verified. Higher nonlinear terms could be comparable.

The following reproduces the scalar audit on either WSL or macOS, in an
environment installed from the same project. It uses float64 NumPy/SciPy,
no grid, GPU, pressure surrogate, or nonlinear solver. The h=1e-6 point is
illustrative and passes ONLY the weakest necessary h test; it is not a
certified finite schedule. P_star=exp(10) is used only to evaluate a lower
bound and is not selected as a valid pressure parameter.

```python
import numpy as np
from scipy.optimize import brentq

h = 1e-6
offset = 0.025
growth = 0.5 + h
axial_exponent = 0.5 - h

def transport(eta):
	return axial_exponent * eta + (1 - eta**2) * (4 * eta + offset)

root, root_info = brentq(transport, -0.01, 0.0, xtol=1e-15, full_output=True)
assert abs(transport(root)) < 1e-14
axis = 4 * root + offset
denominator = 1 - 2 * h * root**2
shape = 1 / (1 + root**2)
bound = (
	10 * growth * abs(root) * np.exp(20) * shape**2
	- growth * (1 - 2 * root * axis) * axis
)
print(root, root_info.iterations, transport(root), bound)
for radial_parameter in (16, 32, 64, 128):
	derivative_bound = bound / (2 * denominator * radial_parameter)
	print(radial_parameter, derivative_bound, 4 * derivative_bound)
```

This stopping check is arithmetic plus one scalar root solve, not a substantive
corrected-flow run. No new result directory, pressure plot, correction plot,
or grid study was generated. The required nonlinear unknowns would be phi,
U, Pi on (X,eta), with analytic axis data phi_star, U_star, Pi0. Their
discretization, domain extensions, normalization C, residual tolerances,
continuation, and acceptance tests remain unselected until the datum and
finite regime are resolved; no arbitrary boundary conditions were added.

### Portability status

Existing reference commands remain:

```bash
python -m pytest -q
python scripts/plot_profiles.py --config configs/nondimensional.yaml
```

They use NumPy/SciPy without CUDA, MPS, or x86-specific code. Tests were run
on Daisy only; no iMac execution is claimed. The current metadata helper
falls back when `/proc` or `nvidia-smi` is absent, but its memory report on
macOS is empty. A cross-platform memory/architecture metadata enhancement
remains necessary before a substantive two-machine milestone run; it was not
added after this source-audit stop.

## Third milestone formulation: relaxed hierarchy

This is a scheduled-pressure and first-correction diagnostic only, explicitly
not theorem-admissible. No nonlinear (B.15) solution or flow time integration
is performed. The old comparison model remains unchanged.

Represent each radial stage by its local coordinate, length, log amplitude
at eta=0, and exponent vartheta of f=(1+eta^2)^(-1). Integrate
`(log E)'=l-1/2` over smooth unit transitions. Constant-slope stages use exact
exponentials; the interpolation uses (A.10) directly, and the terminal collar
uses the exact ratio f_o(y)/f_o(0). Log amplitudes are propagated across joins,
not enormous physical radii. Pressure integrates each stage's amplitude
relative to its starting log amplitude and uses analytic exponential integrals
on constant-slope stages and both infinite ends. This retains small tail
contributions with their own scales, instead of asking a global quadrature to
find them against the dominant inner contribution.

Baseline choices: M_d=1, P_star=2, lambda=0.2, h=0.005; j0=0.025 for the
inner diagnostic. T_d=exp(M_d)+10, T_w=60 log(1/lambda), the 13/lambda
interval, 30 log(1/lambda) interval, and 4 log(1/h) interval are retained
literally. No resolved axial or oscillatory pulse is built; only its swirl
schedule interval is retained. T_f=64 and c_o=0.025 are finite choices to
be checked against the interpolation slope and terminal f_o'/f_o bounds.
Both infinite ends and every transition are retained. The omitted angular
bumps are those explicitly excluded by (A.21); their moment realization and
stress-cone inequalities are NOT verified at these relaxed parameters.

The linear Q equation is integrated through the release transitions with
SciPy DOP853. Its constant l=-1 interval and l=-h stopping interval have
analytic solutions. The stopping length is derived from Q_start and the
independently integrated terminal Q_p, not guessed. Invalid ordering, a
negative stopping length, nonpositive terminal factor, or an unsuccessful
ODE/quadrature call is a failure. A separate integrating-factor formulation
will check the ODE endpoints and Q=0 at the terminal endpoint.

Pressure and two eta derivatives are evaluated under the same integral.
Independent centered finite differences at decreasing eta step sizes check
the derivatives; tighter ODE/quadrature tolerances check numerical convergence.
The implementation rejects nonfinite normalized integrals; stage scales below
float64's amplitude range remain represented logarithmically. Positive moments
are combined with log-sum-exp: contributions below the rounding precision of
the total cannot change that total, but their individual logarithms are retained.
The infinite tails approach zero analytically;
their integrals are evaluated exactly, not truncated at a machine-dependent
radius. All new calculations are NumPy/SciPy float64 on CPU.

### Implemented tolerances and independent checks

The radial step primitive and unit Q transitions use DOP853 with maximum
step 0.025; the terminal Q collar uses the same maximum step. Default
relative/absolute tolerances are 1e-10/1e-12; independent tighter runs use
1e-12/1e-14. Adaptive vector quadrature integrates the normalized nonnegative
moments `K_m=integral E^2 vartheta^m dy`, m=0,1,2, stage by stage. The datum
and derivatives are `-K_0/2`, `J_eta K_1`, and
`J_etaeta K_1-2 J_eta^2 K_2`. Scalar quadrature independently checks the full
datum, the step primitive, and integrating-factor Q endpoints in tests.

The radial step derivative has maximum 8 at y=1/2 (checked against the
explicit derivative on a 10001-point grid). T_f=64 gives worst interpolation
slope decrement `8 log(2)/64=0.086644`, below 0.1. With c_o=0.025, the
bound `f_o'/f_o <= 4 c_o h/(1-c_o h)` is below h/4. The run additionally
samples these slopes and checks C2 joins over the full eta grid. The supplied
smooth-step formula is flat at the ends; a finite C2 check is not a numerical
certificate for every smoothness order.

The main eta grid has 513 points on [-1,1], including endpoints. This is a
pressure-datum domain, not a physical coordinate grid at eta=+/-1. Sampled
Z_star/correction maxima are compared against 1025 points; neither is a
continuous supremum certificate. Independent centered eta differences use
97 interior points on [-0.98,0.98] and steps 0.004, 0.002, 0.001. They
show second-order convergence for both derivatives, including the second
derivative computed directly from pressure values.

Stage summary fields `log_start_eta0`, `log_end_eta0`, and
`log_integral_eta0` refer to **eta=0**, not the negative H_star root. The
negative root is stored as `eta0`, with separately named `root_pressure`
or `root_pressure_and_derivatives` and `root_z_star` diagnostics.

Run `python scripts/relaxed_pressure.py` with
[the relaxed config](../configs/relaxed_not_theorem_admissible.yaml). Every run
requires a fresh directory and saves three labeled plots, full-grid arrays,
per-stage logarithmic contributions, Q diagnostics, tolerance/derivative/grid
checks, the exact-hierarchy bound reference, and source/hardware provenance.
No time step is used. No broad parameter product or optimization is performed.
The named reference PNGs and JSON are selected for version control; temporary
runs and the small reconstructible full-grid array archive remain ignored.

The metadata now includes `architecture` and Python address bits. On macOS
it queries `sysctl hw.memsize` for total RAM, reports available memory as
unavailable rather than inventing a value, and queries the CPU brand. A mocked
macOS branch test is not an actual iMac numerical run.

## Fourth milestone: explicitly modified lengths

[Compression audit](compression-audit.md) records the source dependency matrix
and the choices made before code changes. The independent model in
[compressed_not_theorem_admissible.py](../src/nsblowup/compressed_not_theorem_admissible.py)
inherits RelaxedSchedule, intercepting only insertion of the five authorized
stage lengths. The original class, formulas, reference config and reference
artifacts remain unchanged. No zero-length stage or Q-hold override is allowed.
Changing the release hold propagates to its actual Q endpoint and the derived
Q stopping hold, rather than reusing the baseline hold. Original, modified,
ratio, retained, sacrificed and unchecked fields accompany each override.

The workflow reuses the third-milestone validation routine and its tolerances,
513-point eta grid, independent integrating-factor checks, and 97-point
finite-difference derivative check. A failed interpolation-slope check is
accepted only in a branch whose metadata explicitly sacrifices that bound;
the raw failed check stays visible in the summary. All other validation
failures stop the run. A relative local-data change of 0.1 also stops further
compression, a conservative numerical review threshold rather than a theorem.

Normalized changes compare the tightened modified calculation against the
tightened original RelaxedSchedule. For Pi0 the denominator is its baseline
maximum; for derivatives and Z_star it is max(1,baseline maximum). In these
runs the Pi0 maximum exceeds one, so the common denominator implementation
agrees with that definition. Maxima are sampled, not certified suprema.
One-at-a-time differences round to zero in the total float64 values; those
are unresolved changes, not exact pressure conservation. Stagewise log
integrals still record the changed late contributions. The aggressive
change around 1e-11 is larger than the observed 2.68e-14 quadrature refinement
floor; its final digits are not rigorous error-certified.

Run `python scripts/compressed_not_theorem_admissible.py`. The config uses
source-chosen lengths or explicit factors, resolved to actual lengths against
the reference at runtime. All output directories must be new. The final
reference summary, three plots and condition table are selected for version
control; reconstructible NPZ arrays and temporary runs remain ignored.
The table's support flags concern geometry only; global moment and stress
verification flags remain false even for the relaxed baseline. Conditional
terminal Q identities do not remove that qualification.

## Fifth milestone numerical formulation

Use a tensor Chebyshev-Lobatto interpolant in Y on [0,4.1] and eta on
[-1,1], CPU float64. Unknowns are Phi and u in B.12; integrate pressure
from the already fixed scheduled Pi0, never impose a boundary at Y=4.1.
Eta endpoints are polynomial endpoint derivatives, not prescribed boundary
data. Radial regularity is imposed by J1/J2 and the fixed axis values.

Numerical radial inverses integrate the interpolation polynomial exactly
up to quadrature roundoff: J1 F=Y integral_0^1 integral_0^1 F(Yst) ds dt;
J2 F=Y integral_0^1 (1-t)F(Yt) dt. Gauss-Legendre rules integrate these
polynomials; pressure and averages use the corresponding single integral.
The angular order-one operator 1+J2 chi/2 is inverted as a small radial
matrix for each eta. Iterate the exact p148 map from the explicit comparison.
Monitor absolute Phi increments and U increments (u increment divided by
Lambda); stop at 1e-11, at nonfinite/zero-crossing Phi, growth beyond a
declared finite probe budget, or 80 iterations. A stopped increment is NOT
acceptance: original-source residuals at independent off-grid points and
three nested resolutions are required. No assumption of discrete contraction
is inherited from the proof's analytic coefficient norm.

Initial nested grids: (17,129), (25,257), (33,513) points in (Y,eta).
Correction during execution: those radial grids were not strictly nested.
The preserved initial probe used them; the reference rerun uses genuinely
nested (17,129), (33,257), (65,513) grids at the same parameter tuple.
Start Lambda512, sigma=.2, g_peak=.1, aggressive datum. Continue only if
residuals converge; a failed first case triggers the prompt's review stop,
not an automatic sweep of other parameters. A second reasonable initial
guess may test dependence on initialization at this same case.
Real-axis log g=log(g_peak)+Lambda integral_eta0^eta zeta_star is evaluated
without forming phi_star or C. log C is reported from the integral between
0 and eta0. Underflow of negligible g^2 tails is distinguished from loss
of its resolved central peak; derivative and normalization checks determine
whether the axis data are adequately represented. This is not a complex
neighborhood bound on g.

Off-grid residuals differentiate the interpolation polynomial and reconstruct
the original 4.9 sources independently of R1/R2. Norms include Linf and
unweighted sampled RMS, plus axis and outer-endpoint slices. If accepted,
subsequent continuation and control comparisons require the same tolerances.
Failed attempts are saved with histories and residuals, not called solutions.

### Fifth-milestone execution and rejection

The initial grid proposal was corrected to nested (17,129), (33,257),
(65,513) without changing any physical or axis-data parameter. Three runs
are retained locally: initial_probe (non-nested radial refinement), reference
(nested), and reference_v2 (same nested solve with complete L2/derivative
reporting). Only the small final reference summary and plots are allowlisted.
The final workflow is deliberately bounded to the initial failed gate, not a
general parameter-sweep or solution-acceptance API.

Per-iteration histories record increments and the input iterate's rescaled
collocation equation residuals. Those reuse R1/R2 and are explicitly NOT the
independent acceptance test. Final acceptance residuals reconstruct original
S_q and S_n on (36,259), (68,515), (132,1027) sampled grids, including the
axis and outer edge. L2 uses tensor trapezoidal integration of squared
residuals with respect to dY d_eta; RMS is additionally reported. The declared
absolute gate 1e-7 is an engineering criterion, not a theorem estimate, and
the required decreasing-refinement test fails regardless of that threshold.

Derivative changes use a common 129 by 1028 grid (including eta0), with
first and second Y and eta derivatives of Phi, U-U_star and Pi-Pi0.
Common axis terms cancel between refinements. These differences are not
errors against a known solution. The second initial guess Phi=1,u=0 is
compared only on the finest discrete grid. Neither check establishes
analytic regularity, uniqueness, or stable continuous dependence.

At eta0, local expansion gives log(g/g_peak) approximately
`-Lambda L(eta0) H_star'(eta0) (eta-eta0)^2/(2 sigma_star^2)`.
Its Gaussian standard-deviation scale is about .0042 at Lambda512 and
sigma=.2. Eta Lobatto spacing near zero is about .00614 for 513 points,
and .01227 for 257 points. Squaring g narrows it further. The measured
interpolant of g^2 has negative lobes and 17% peak-relative Linf error on
the finest grid, with order-one derivative error. Far-tail square underflow
is separately counted and does not explain the inaccurate central peak.

No automatic higher resolution, smaller sigma, different amplitude, relaxed
nonlinear control, or Lambda continuation follows this stop. Possible later
work under gate B is a source-equivalent locally resolved eta representation
or a factored pressure treatment, validated on the same first tuple before
any parameter continuation. Merely tightening the increment tolerance does
not address the observed failure.

## Sixth milestone: source-resolved, factored same-tuple experiment

All model parameters and the aggressive pressure evaluator are unchanged.
Source-only checks precede any nonlinear call. Exact B.3 derivatives are
tested against fourth-order finite differences, not a polynomial derivative.
The reference mesh has 8193 global uniform points plus 4097 points within
12 local standard deviations of eta0. Source errors include endpoints.
Peak location uses scalar optimization within one standard deviation of
eta0. Effective counts refer to widths of one and six standard deviations,
not intervals of +/- one and +/- six. Modal tails use the highest 10%.

The source benchmark reaches its declared value/first-derivative gate at
2049 Lobatto points with decreasing second-derivative errors. Retain global
Chebyshev polynomials but use DCT-I coefficients, coefficient differentiation
and inverse transforms instead of dense eta matrices. No filtering or
coefficient truncation is introduced. There are no domain interfaces. The
global second-derivative conditioning still needs explicit endpoint checks.

Pressure p=G Pbar is reconstructed with exact G and G_eta. The iteration
uses Pbar=I(Phi^2), Pbar_eta=I(2Phi Phi_eta); independent residuals instead
differentiate numerical Pbar and reconstruct original S_q/S_n. This tests
the product-rule identity without reusing its right-hand side as a residual.
The p148 map is unchanged; the old solver and reference results are retained.

Stage A fixes 65 radial points and starts at the first source-resolved eta
count, with nested doublings only while numerical stop conditions permit.
If Stage A converges, Stage B will fix eta and use 33/65/129 radial points,
then Stage C one combined pair. If the resolved first iteration fails, stop
without opening those later stages. The same 1e-11 increment threshold and
80-iteration budget remain; neither is numerical acceptance. Known failure
conditions keep the last finite positive iterate and record rejected proposals.

### Sixth-milestone executed stop

At 65x2049, both starts lose convergence and propose Phi<=0. Accordingly
Stages A (further eta refinement), B and C are not executed. The minimum
increment snapshot and last retained positive snapshot are saved, neither
accepted. Adding source-equivalent factorization did not restore stable
global endpoint iteration. No filtering, damping, parameter continuation,
domain truncation or hidden boundary condition was added after this failure.

Independent residuals zero-pad eta coefficients onto 4097 Lobatto nodes,
including interleaved off-grid nodes, and evaluate radial polynomials on 129
uniform points. Original S_q/S_n use independently quadrature-averaged U
and differentiated Pbar, not R1/R2. Pbar derivatives are compared against
integral product identities as separate, non-tautological checks. Report
all-eta, abs(eta)<=.98, abs(eta-eta0)<=6 G standard deviations, eta endpoint,
Y=0, Y=4.1 and interior-Y norms. Derivative magnitudes and differences
between failed initializations are not called refinement convergence.

Modal tails are computed without filtering at all iterations and on
Y=.5,2,4.1 slices. For an identically zero field the modal ratio is defined
as zero, avoiding undefined 0/0 in the flat-start provenance. First failed
serialization output is preserved separately from the final reference run.
The separate sigma side audit locates numerical Z_star roots and reports
abs(H_star)/sqrt(99) as a necessary strict upper bound, not a sufficient
neighborhood condition. No smaller sigma is applied to any nonlinear run.