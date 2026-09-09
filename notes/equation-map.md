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