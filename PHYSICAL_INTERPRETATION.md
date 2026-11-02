# Physical interpretation: Reynolds number, vortex size, and what is missing

**Discussion recorded: 2026-11-01.** This is a physics-first reading guide,
not a new simulation result, an experimental design, or a new work order.
It captures questions that remain difficult to understand from the numerical
reports alone. The prior mathematical research and its negative results remain
intact. This note does not direct anyone to resume numerical development.

## Start with the physical questions

The central difficulty is not merely how to render a vortex. It is how a
real fluid could develop and sustain an increasingly concentrated vortex.

Before proposing another numerical campaign, an understandable physical
account would need to answer:

1. What initial flow is produced, and by what mechanism?
2. How are its characteristic velocity, radial and axial dimensions, and
   circulation defined and measured?
3. What makes the core contract despite viscosity? What provides the
   necessary momentum transport and energy?
4. What drives the motion: a prescribed **body force**, motions or ports at
   the **boundary**, or nonlinear transfer from other parts of the flow?
   These are not interchangeable.
5. At what spatial and temporal scales do cavitation, finite sound speed,
   heating, instrumentation limits, or microscopic fluid effects matter?
6. Which quantities are **computed from an accepted fluid solution**, and
   which are imposed by a formula or chosen for a diagram?

The published mathematical construction motivated these questions. It does
not itself supply a validated laboratory mechanism for generating the flow.

## Reynolds number: which one?

For a Newtonian fluid, a characteristic Reynolds number is

\[
\mathrm{Re}=\frac{U L}{\nu},
\]

where \(U\) is a **specified characteristic velocity**, \(L\) a
**specified characteristic length**, and \(\nu\) the kinematic viscosity.
It expresses the ratio of inertial to viscous scales for those choices.

A mosquito and a jet aircraft have very different characteristic Reynolds
numbers, but the comparison is incomplete without stating the size and
speed used. Likewise, a flow with a large apparatus-scale Reynolds number
may contain much smaller regions where viscosity is important.

**A vortex has no single Reynolds number until its relevant velocity and
length scales are identified.** There may be a tank-scale Re, a core-scale
Re, and different values for perturbation wavelengths or shear layers.
No universal Reynolds-number threshold decides what happens in every
geometry. A small *local* Re does not, by itself, characterize the
entire flow as nonturbulent or physically realizable.

### A useful—but conditional—core scaling

The original [research context](RESEARCH_CONTEXT.md#4-physical-picture-of-the-concentrating-core)
describes an approximate relation, after introducing dimensional water
viscosity and neglecting a small exponent,

\[
U_{\mathrm{core}} r_{\mathrm{core}}\ \sim\ \nu,
\qquad
U_{\mathrm{core}}\ \sim\ \frac{\nu}{r_{\mathrm{core}}}.
\]

If **those are the appropriate velocity and radius for the same core**,
then

\[
\mathrm{Re}_{\mathrm{core}}
=\frac{U_{\mathrm{core}}r_{\mathrm{core}}}{\nu}
\sim O(1).
\]

Thus increasing core speed while the radius shrinks does **not
automatically mean increasing local Reynolds number**. It is not simply
a miniature version of the high-Reynolds-number flow around an airplane.

This is a *scaling interpretation*, **not** a measurement or proof that
the proposed core has Re exactly one. The original exponents contain
corrections; dimensional prefactors, distinct radial/axial scales, and the
choice of velocity component matter. A numerical Reynolds number cannot
be read off merely from the nondimensional plots. The paper's actual
core equations and a justified dimensionalization would be required to
establish it for a particular candidate.

The fact that the smallest dissipative motions in ordinary turbulence
can also have local Reynolds numbers of order unity is a useful analogy
only. It **does not** demonstrate that this construction is a conventional
turbulent cascade or a physically attainable small-scale vortex.

## How small is "small"? Illustrative water arithmetic

Take room-temperature water with \(\nu\approx10^{-6}\,\mathrm{m^2/s}\).
Assuming, solely for this illustration, the conditional relation
\(U=\nu/r\), and using \(t_\nu=r^2/\nu\) as a viscous diffusion time
scale:

| Assumed core radius | Speed from \(U=\nu/r\) | Viscous time \(r^2/\nu\) |
| --- | ---: | ---: |
| 1 cm | 0.1 mm/s | 100 s |
| 1 mm | 1 mm/s | 1 s |
| 100 μm | 1 cm/s | 0.01 s |
| 10 μm | 10 cm/s | 0.0001 s |
| 1 μm | 1 m/s | 0.000001 s |

Each factor-of-ten contraction raises this illustrative speed tenfold
and shortens the viscous time by a factor of 100. These are
**dimensional estimates, not predicted or measured flow states**.
The diffusion time is not necessarily a vortex's actual lifetime.

For scale: a \(1\,\mu\mathrm m\) radius is much smaller than an
ordinary laboratory vortex; it would make imaging, flow control and
measurement formidable. Smaller radii require explicit consideration
of the continuum approximation and other real-fluid effects. A
mathematical profile can be evaluated at arbitrarily small formal
coordinates without thereby constructing the corresponding water flow.

Pressure provides another physical check. A rough inertial pressure
scale is \(\Delta p\sim\rho U^2\), with water density about
\(1000\,\mathrm{kg/m^3}\). At the *illustrative* 1 m/s velocity this
scale is about 1000 Pa (up to geometry-dependent factors), not a
calculated core pressure. Cavitation depends on the **absolute local
pressure**, vapor pressure, temperature, nuclei and the actual
pressure field; neither a radius nor a speed by itself proves it
will or will not occur. Energy and power requirements must also be
computed for a specified volume and driving mechanism.

## A plotted shrinking radius is not evidence that a vortex shrunk

The [first-pass experiment log](notes/experiment-log.md) reports an
Appendix B **explicit comparison** with a *prescribed* window radius
shrinking by a factor of 1000. Its velocity scale grows according to
the chosen comparison profile. This is a useful numerical and scaling
check, **not** a time-integrated physical vortex or a successful
nonlinear concentrating solution.

The later finite-hierarchy investigations record extremely large
mathematical separations. For example, the
[compressed-model conditions](results/compressed_not_theorem_admissible_reference_v2/compressed_not_theorem_admissible_conditions.md)
list 70.44 radius decades for the baseline geometry and about 8.78
for an aggressive shortened variant. These are **relative, formal
scale-separation requirements**, not the diameter of a vortex observed
in water. The shortened variant gives up several conditions of the
original construction, and its global moments and required stress
were not verified. One cannot choose a macroscopic starting radius,
subtract eight or seventy decades and call the endpoint physically
achieved.

The [README](README.md#fifth-milestone-failed-local-core-acceptance-gate)
records that the attempted nonlinear core did **not** pass acceptance.
A subsequent representation/source-resolution study improved some
diagnostics but still failed the required iteration/acceptance criteria.
No accepted nonlinear core, demonstrated concentration of a real fluid,
or physically implemented forcing has resulted from those experiments.

## What a successful physical explanation would look like

A useful next *discussion*, if the owner chooses to return, should begin
with an ordinary vortex in a specified vessel and then explain:

- **Geometry:** tank/core sizes, axial versus radial scales, and the
  meaning of "core radius" (for example from a measured vorticity profile,
  not just a plotting window).
- **Flow:** radial inflow, axial motion, swirl, circulation, vorticity,
  and where each component originates.
- **Driving and balances:** the available actuator/body-force mechanism,
  viscous diffusion, pressure gradients, mass conservation, energy input
  and dissipation, and any proposed nonlinear momentum transfer.
- **Dimensionless parameters:** Re at each stated scale, plus other
  relevant ratios for the apparatus and perturbations.
- **Observables:** measurable core radius, speeds, pressure, vorticity
  proxies and uncertainty, with predictions that could be wrong.
- **Feasibility:** required driving and sensors, and what stops the
  contraction before continuum or numerical resolution limits.

A transparent tank with moving tracer dots may be a helpful schematic,
but it is not automatically evidence for any of these balances. The
separate [Vortex Lab repository](https://github.com/rharriszzz/navier-stokes-vortex-lab)
describes its current particle movie as a **kinematic illustration**,
not a validated Navier–Stokes solution or generated boundary-driven
flow. Do not conflate that movie with the mathematical experiments here.

## Decision and next step

The owner requested that **both Navier–Stokes projects be omitted from
the public project index for now**, while leaving their repositories and
research intact. The owner wants a more intelligible explanation of
Reynolds numbers, physical length scales and the contraction mechanism
before deciding whether to return to the work.

This is an **editorial and scientific-interest decision**, not a
retraction of the mathematical work or proof that the physical goal is
impossible. It does not mandate an engineering project in preference to
the previous numerical research.

**No new research or visualization is authorized by this note.**
A proposed [physics-first learning roadmap](PHYSICS_FIRST_LEARNING_PLAN.md)
would examine ordinary vortices, their contraction and measurement, and
their relation to the mathematical construction. It also records potentially
interesting [physical and engineering spin-offs](notes/physical-opportunities.md)
for later consideration. These documents are **options**, not standing
commands. If a future request is ambiguous, explain the alternatives,
ask which direction the owner wants, and wait for an answer rather
than launching numerical work from old handoffs.
