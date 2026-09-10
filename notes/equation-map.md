# Equation map

Source: OpenAI, *Finite Time Blowup for Navier-Stokes*, September 2026,
https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf

Read directly: Section 3.1, Section 4.1, Lemma 4.8, Appendix B.1-B.3.
Page numbers below are PDF page numbers. No equations are inferred from the
repository's planning estimates.

PDF retrieved 2026-09-09, 166 pages, SHA-256:
`0e779481c4da40bd28d1e642e1d8ca57447d129610df28dfa5a11e9af8ae228f`.

| Quantity | Paper equation | Code function | Notes |
| --- | --- | --- | --- |
| tau=1-t; A=1/2+h; D=1/2-h | Section 3.1, (3.2), (4.1), pp. 7, 24 | `coordinates` | tau is accepted directly to avoid subtractive loss near t=1. |
| tau=q(1-eta^2), z=q^D eta, X=r^2/(2q) | (3.2), (4.1); Lemma 4.1 | `to_physical`, `to_similarity` | q is implicit off z=0; never replaced by tau. |
| U_star=4 eta+j0; H_star=D eta+(1-eta^2) U_star | (B.1), p. 144 | `comparison_profiles` | Published axis datum, used as the zeroth-order axial comparison, not the full U. |
| chi=H_star^2/(H_star^2+sigma_star^2) | (B.2), p. 144 | `comparison_profiles` | Finite sigma is a numerical choice; the condition involving Z_star is NOT certified. |
| zeta_star=-L H_star/(H_star^2+sigma_star^2); phi_star=exp(Lambda integral_0^eta zeta_star) | (B.3), p. 145 | `comparison_profiles` | Evaluate a normalized logarithm to avoid overflow. |
| f0(argument)=sum (-argument/2)^alpha/[alpha!(alpha+1)!] | (B.11), p. 146 | `comparison_function` | Implemented with the equivalent SciPy 0F1 special function. |
| Phi approximately f0(Lambda X chi) | (B.12)-(B.13), pp. 146-147 | `comparison_profiles` | EXPLICIT COMPARISON ONLY. O(1/Lambda) corrections to Phi and U are omitted. |
| E=sqrt(2X) phi/C; u_theta=q^(-A) E; u_z=q^(-A) U; r u_r=V0 | (4.3), p. 25 | `velocity` | Uses comparison profiles, not the solved nonlinear core. |
| V0=X/L [2 eta U-2D eta A_X(U)-(1-eta^2) partial_eta A_X(U)] | (4.6)-(4.7), pp. 25-26 | `comparison_profiles`, `velocity` | For U=U_star independent of X, A_X(U)=U and partial_eta A_X(U)=4. Exact incompressibility for this comparison. |
| div u=partial_r u_r+u_r/r+partial_z u_z | Section 3.1; physical specialization of (3.11) | `divergence` | Second-order physical-grid differences; smooth-axis limit 2 partial_r u_r+partial_z u_z. |
| radial extent ~tau^(1/2); axial extent ~tau^D; tangential velocity ~tau^(-A) | Section 3.1, p. 8 | `scripts/plot_profiles.py` | Exact geometry on fixed (X,eta) domains. Tangential slope versus radius is -2A=-1-2h; total speed includes a differently scaled radial component. |

## Deliberately not implemented

- The exterior pressure datum Pi0(eta), (4.31), and its Appendix A construction.
  It is a function, not an arbitrary pressure-gauge constant. Setting it to zero
  would change the axial momentum balance.
- Z_star in (B.1), the axial correction -Y Z_star/(2 L Lambda) in (B.13),
  and the nonlinear corrections solving (B.15).
- Absolute swirl normalization selected by the proof: C0(Lambda) is existential.
  The diagnostic normalization is declared in the run configuration/report.
- Inner-to-exterior joining, five-moment matching, the stress annulus, heat
  exterior, oscillations, and spatial/time cutoffs.
- Pressure, full Navier-Stokes residual, and the claim of vanishing leading
  tangential residual. These require more than the comparison implemented here.

This first pass evaluates a finite domain without multiplying the field by a
cutoff. It is not a globally localized velocity field. Numerical finite parameter
choices do not certify the theorem's hierarchy or its asymptotic error bounds.

## Second milestone: pressure-datum source audit (2026-09-09)

Status: source audit, not implemented mathematics. The same PDF digest above
was verified locally before reading these equations.

| Quantity or dependency | Source / PDF pages | Numerical significance | Implementation status |
| --- | --- | --- | --- |
| Pi0=-integral E_o^2/(2X) dX | (4.31), Lemma 4.8, p. 35 | Requires the complete reference swirl, not merely its inner branch. | Not implemented |
| T_d=exp(M_d)+10; P_star>exp(T_d); h<min(0.01,lambda,exp(-T_d)) | Lemma 4.8, p. 35 | Extra hierarchy not imposed by the comparison-only configuration. | Source constraint only |
| Pi0=-1/2 integral E_id,sched(y,eta)^2 dy, y=log(X/X_R) | (A.21), Lemma A.5, pp. 133-134 | Angular bumps preserving the total pressure increment can be omitted, but all schedule transition intervals remain. Independent of X_R. | Not implemented |
| E_id,sched=c(y) f(eta)^vartheta(y), f=(1+eta^2)^(-1), 0<=vartheta<=1 | Proof of Lemma A.5, pp. 133-134; schedule in Section A.2 | Reduces pressure evaluation to a prescribed schedule; c and vartheta are not arbitrary replacement profiles. | Audited; finite admissible schedule not selected |
| Pi0<=-(5/2) P_star^2 f^2, Pi0 even, eta Pi0'>0 off zero | (A.22), pp. 133-134 | The right side is the exact inner-branch contribution and a bound, NOT the full datum. | Not implemented |
| Pi(X,eta)=-1/2 integral_y^infinity E(v,eta)^2 dv | (A.23), pp. 133-134 | Later pressure-preserving edits leave the axis datum unchanged. | Not implemented |

Do not implement (A.22)'s bound as equality or substitute a pressure of zero.

### Schedule dependency inventory

Read directly: Section A.2, pp. 129-130; Section A.3, pp. 131-133;
Lemma A.5, pp. 133-134; Proposition A.7, pp. 139-140; Appendix B,
pp. 144-147. These give the following dependencies of (A.21).

| Dependency | Source / PDF pages | Explicit versus finite numerical choice |
| --- | --- | --- |
| Smooth radial step sigma(y) | (A.5), p. 129 | Explicit flat exponential ratio. Not the axial width sigma_star in (B.2). |
| Schedule order M_d, T_d, P_star, lambda, h | (A.6), p. 129; Lemma 4.8, p. 35 | T_d and inequalities explicit; sufficiently large/small admissible thresholds are not numerical values. lambda is distinct from inner Lambda. |
| Reference inner E=P_star f exp(y/10), U=4 eta | (A.7), p. 129 | Explicit for y<=0; its pressure contribution alone is -(5/2) P_star^2 f^2. |
| Unit slope transition and axial-reduction interval of length T_d | Section A.2, p. 129 | Integrate (log E)'=l-1/2; l and k(y) specified with (A.5). M_d controls the derivative bound 4 norm(sigma')/M_d. |
| Intermediate slope -lambda and T_w=60 log(1/lambda) | (A.9), p. 129 | Explicit once lambda is fixed; reserved patches must fit. |
| Pulse interval of length 13/lambda | Section A.2, p. 130 | E retains slope -1/2-lambda. Axial amplitude and its two bumps do not set E or Pi0. |
| Removal of eta dependence over T_f | (A.10), p. 130 | Formula explicit; choose sufficiently large T_f to keep -lambda-0.1<=l<=-lambda. This changes the pressure integral. |
| Angular moment adjustment over 30 log(1/lambda) | (A.11), pp. 130, 132 | Two angular bumps restore I=XH/(1-lambda), with zero total pressure change. Omit bumps, NOT the interval, in (A.21). |
| Exterior slope transitions and 4 log(1/h) hold | Section A.2, p. 130 | Unit transitions specified by (A.5). |
| Terminal f_o, rho_o=c_o h, Q_p | (A.12)-(A.13), p. 130 | Choose c_o>0 small enough for 0<=f_o'/f_o<h/4. This affects Q_p and the schedule. |
| Length of constant -h interval before terminal collar | Section A.2, p. 130; Section A.3, p. 132 | Determined by integrating Q'+(1+l)Q=-l-h, starting Q=(lambda-h)/(1-lambda) at exterior transition start, and stopping at Q_p. Positive length must be verified, not guessed. |
| Terminal power-law tail pressure | (A.12), (A.21), pp. 130, 133 | Integral converges; tail slope is -1/2-h. Its integral must be included, not windowed away. |
| Heat replacement and compensated moments | (A.39)-(A.43), Proposition A.7, pp. 139-140 | Preserves total pressure increment and Pi0. Not needed to evaluate the original datum (A.21). |
| Axial amplitude and moment closure | (A.14)-(A.20), pp. 131-133 | Needed to validate a full admissible exterior, but not to evaluate scheduled E once its parameters are fixed. |

The datum therefore requires at least a concrete tuple
`(M_d, P_star, lambda, h, T_f, c_o)` plus a validated Q stopping event,
quadrature choices and their error checks. `T_d` and `T_w` are derived,
not independent fit parameters. X_R cancels from Pi0. Moment-bump placement,
the heat cutoff and X_R are additional choices for completing the exterior,
not missing inputs to (A.21) itself. Lack of a unique tuple is not a defect in
the existence construction: many choices are allowed. The unresolved numerical
issue is choosing an admissible, computationally useful tuple, not inventing
an arbitrary pressure function. No unvalidated tuple has been installed in config.

### Axial correction and a necessary size check

The following formulas were verified and documented, but no production pressure
or nonlinear solver was implemented in this milestone:

| Quantity | Source / PDF pages | Interpretation |
| --- | --- | --- |
| Z_star=-A(1-2 eta U_star)U_star-H_star U_star_eta-d Pi0_eta+4A eta Pi0 | (B.1), p. 144 | Requires both the pressure datum and its eta derivative; d=1-eta^2. |
| U=U_star+Lambda^(-1) u; u approximately -Y Z_star/(2L) | (B.12)-(B.13), pp. 146-147 | The first omitted correction to U is -Y Z_star/(2L Lambda), not -Y Z_star/(2L). |
| -2L(X U_XX+U_X)=S_n; Pi_X=phi^2/C^2 | (B.15), p. 147; (4.9), p. 26 | At X=0, S_n=Z_star, so any regular solution has U_X(0,eta)=-Z_star/(2L). |

At the unique negative root eta0 of H_star, combine (A.22), the sign of Pi0',
and (B.1). Without evaluating Pi0, one obtains

$$
Z_*(\eta_0)\ge
10 A |\eta_0|P_*^2 f(\eta_0)^2
-A(1-2\eta_0 U_*(\eta_0))U_*(\eta_0).
$$

This is a derived necessary bound, not a pressure model. Since T_d>10 and
P_star>exp(T_d), replacing P_star^2 by exp(20) yields a weaker conservative
bound. The strict schedule also requires h<exp(-10). Neither statement depends
on a chosen smoothing length or on quadrature. The baseline h=0.005 and all
suggested h values violate that necessary condition. Evaluating this bound at
a smaller illustrative h is not a certificate that the full schedule exists
for that tuple; all other admissibility conditions remain to be checked.

## Third milestone: relaxed scheduled pressure

Authorization: [THIRD_PROMPT.md](../THIRD_PROMPT.md). All new numerical
results are **relaxed-hierarchy, not theorem-admissible**. Direct PDF reading
for implementation: pp. 129-130, 133-134, 144, 147; same verified digest above.
The first two milestone sections are historical records, not claims about
which routines exist after this milestone.

| Implemented quantity | Paper source | Code location |
| --- | --- | --- |
| Flat radial step and its derivatives | (A.5), p. 129 | `relaxed_schedule.smooth_step` |
| Stage slopes, lengths, and amplitude continuity | Section A.2, (A.7)-(A.12), pp. 129-130 | `RelaxedSchedule` |
| Q'+(1+l)Q=-l-h and terminal Q_p | Section A.2, (A.13), p. 130 | `RelaxedSchedule` Q construction |
| Complete pressure integral, including both infinite ends | (A.21), Lemma A.5, pp. 133-134 | `RelaxedSchedule.pressure` |
| Pressure eta derivatives under the integral | Derived from (A.21), proof of Lemma A.5 | `RelaxedSchedule.pressure` |
| Z_star and negative root of H_star | (B.1), p. 144 | `relaxed_schedule.axial_diagnostic` |
| delta U1=-Y Z_star/(2 L Lambda) | (B.12)-(B.13), pp. 146-147 | `relaxed_schedule.first_axial_correction` |

Write J=log(1+eta^2), E=exp(a-vartheta J), and G=E^2. At each radial
quadrature point the differentiated integrands are exactly
`G_eta=-2 vartheta J_eta G` and
`G_etaeta=(4 vartheta^2 J_eta^2-2 vartheta J_etaeta) G`, where
`J_eta=2 eta/(1+eta^2)` and `J_etaeta=2(1-eta^2)/(1+eta^2)^2`.
These are derivatives of the prescribed schedule, not a pressure surrogate.

For the terminal collar, (A.12)-(A.13) simplify to
`Q_p=integral_0^3 exp((1-h)v) f_o'(v) dv / f_o(0)`.
After the release transitions, a positive Q_start greater than Q_p gives
`T_hold=log(Q_start/Q_p)/(1-h)`. The whole release Q solution must be
independently checked; omitting the angular bumps does NOT justify computing
the initial Q from the uncorrected scheduled swirl. The prescribed initial
value `(lambda-h)/(1-lambda)` is retained from the moment-corrected construction,
whose realization is not certified in this relaxed experiment.