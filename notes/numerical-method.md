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