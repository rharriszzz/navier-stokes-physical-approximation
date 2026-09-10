# Schedule compression and sacrifice audit

Fourth milestone; modified finite models, **NOT theorem-admissible**.
Source: the same 166-page PDF and SHA-256 recorded in [equation-map.md](equation-map.md).
Direct source readings: Appendix A.2-A.5, pp.129-137; moment matrix and
small-solution criteria pp.127-128; Appendix B.1-B.3 pp.144-147.

## Stage dependency matrix

Codes: P pressure/local datum; M moments/matching; S stress; R later reserved
corrections; T terminal/Q; U unresolved. Every finite interval is P: even a
uniform-in-eta interval contributes to Pi0 and hence 4A eta Pi0 in Z_star,
and its length shifts all subsequent amplitudes. Tiny contribution is not zero.
An absent code means no separate direct role identified, not a proof of independence.

| Stage | Source, PDF page | Paper length | Roles | Constraint or role affected by shortening |
| --- | --- | --- | --- | --- |
| Inner slope transition | A.2, p129; A.5, p135 | 1 | P M S | Matches l=3/5 to 0 with the fixed flat step; positive Q and relaxed cone propagation. Fixed shape retained. |
| Axial reduction | A.2 p129; A.26 p135 | exp(M_d)+10 | P M S | k=4[1-sigma(log(1+y)/M_d)] vanishes after exp(M_d)-1; final eleven units damp averaged k so L averaged k<1/2. Derivative bound e_d/(1+y), h much smaller than exp(-T_d), large P_star enter cone estimate. Not shortened here. |
| Transition to -lambda | A.2 p129; A.5 p135 | 1 | P M S | Flat join; W>=1/2 from prior damping; cone for l<0. Fixed shape retained. |
| Intermediate power | A.9 p129; A.14 p131; A.27 p135 | 60 log(1/lambda) | P M S R | Suppresses e_b to C_pre lambda^30 and averaged axial/moment discrepancies; relaxes Q toward its equilibrium; controls N/E. Four fixed-width reserved patches for profile correction after cone realization, heat compensation, higher-order background, phase-averaged corrections. |
| Axial-pulse swirl interval | A.2 p130; A.15 p131; A.19-A.20 p133; A.28-A.30 pp135-136 | 13/lambda | P M S | Main R0 pulse ends at 11/lambda; two width .3 axial bumps centered at length-3 and length-1 close M,J; separation produces exponentially small coefficients, principal S moment has exp(-26), K_b integral to 13. Shortening changes that amplitude argument, not just room for bumps. |
| Eta removal | A.10 p130; A.5 p136 | T_f sufficiently large | P M S T | Theta goes 1 to 0 smoothly; uniform exterior enables scalar Q and angular matching; slope in [-lambda-.1,-lambda] used for a bounds. All positive lengths retain endpoints and theta range, not the slope bound. |
| Angular-bump interval | A.11 p130; A.3 pp131-132 | 30 log(1/lambda) | P M S T | r_I discrepancy decays at rate 1-lambda; C_pre lambda^28 discrepancy gives small nonlinear I/pressure correction, E>0 and l<=-lambda/2 after actual bumps. Exact I=XH/(1-lambda) supplies Q initial value. Bumps remain omitted, existence unchecked. |
| Release down | A.2 p130; A.3 p132 | 1 | P M S T | Smooth l from -lambda to -1; nonnegative Q source; fixed shape retained. |
| Release hold | A.17-A.18 p132; A.5 p137 | 4 log(1/h) | P M S T | Q grows linearly with slope 1-h. Exact h^8 reduction in XE^2 and h^6 in E provide h-uniform S bound and small E/Q near terminal. Shorter hold has exp(-2T) and exp(-3T/2), not those h powers. |
| Release up | A.2 p130; A.3 p132 | 1 | P M S T | Smooth l from -1 to -h; Q endpoint sets next hold. Fixed shape retained. |
| Q stopping hold | A.13 p130; A.16 p132 | log(Q_start/Q_p)/(1-h) | P M S T | Derived matching identity, not an independently adjustable length. Must be positive. |
| Terminal collar | A.12-A.13 p130; A.16 p132 | 3 | P M S T | f_o constant through y=1 then flat transition to 1 by y=3; f_o'/f_o<h/4; exact Q terminal zero. Fixed shape retained. |

Inner/exterior matching is not effected by any length override here. The
reference inner profile is replaced by a regular axis later in Appendix B;
Corollary A.3 p128 describes five-moment corrections on the inner reference
power and intermediate power. Heat replacement (A.6, p137) changes three
moments restored in the second reserved patch. Removing that patch forfeits
that specified compensation placement, not the definition of an unheated datum.
The last two patches support higher-order and phase-averaged corrections;
those operations are outside this model. Their all-orders constants are not
numerically audited and are not asserted retained, even if space remains.

## Hard supports versus proof margins

1. T_w>25 keeps the four stated open patches inside the interval. Their widths
   and separations are explicit. This is only a support test. The factor 60
   additionally gives exp[-(1/2+lambda)T_w]<=lambda^30 and the smallness
   estimates (A.14), (A.27), later (A.29)-(A.30); no universal minimum T_w
   for those inequalities can be inferred without C_pre and tolerances.
2. The original main pulse ends at 11/lambda. Keeping both fixed-width end
   bumps strictly beyond it requires T_p>11/lambda+3.15. This derived finite
   support threshold is not sufficient for the exponentially small correction
   or S-amplitude argument. At lambda=.2 it is 58.15; use 59 as a support-aware
   test. The source's assertion that both s1=.5-lambda and s2=.5-2lambda
   exceed .4 requires lambda<.05 and already fails in the relaxed baseline.
3. T_f>=80 log(2)=55.45177444 preserves the A.10 slope bound with the
   published step, whose maximal derivative is 8. Use 56 for a slope-retaining
   branch and 8 for an explicitly slope-sacrificing branch. No eta dependence
   or slope formula is replaced; the same theta(y/T_f) is used.
4. The two angular width-.3 bumps at T_a-3,T_a-1 fit if T_a>3.15. Their
   fixed separation is 2. The factor 30 makes exp[-(1-lambda)(T_a-3)] small
   enough for the cited lambda^28 estimate in the small-lambda regime. Room
   for bumps does not establish Lemma A.2's quantitative smallness
   8 beta_0^2 kappa_0 d_0<=1 or the post-edit slope sign.
5. The release hold produces the exact A.17 factors only at the paper length.
   A shorter hold can still yield Q_start>Q_p. That is a conditional terminal
   match, not an h-uniform stress estimate. Test one half-length and length 2.
6. The Q stopping hold must always be recalculated; it cannot be overridden.
   Its initial Q is still conditional on the imposed A.11 moment value, not
   a moment computed from the unbumped compressed swirl. No run asserts actual
   global angular matching, axial M,J closure, or S(infinity)=0.

No dominant stage has an unresolved formula preventing this length-only
experiment. Optimal constants, actual moment corrections, and stress margins
remain unchecked, rather than being silently inferred from the support audit.

## Model and experiment choices

The separate `CompressedNotTheoremAdmissibleSchedule` subclasses the existing
schedule and overrides only the insertion of five constant/interpolation stage
lengths. It inherits the original construction, swirl, pressure quadrature,
and Q solver unchanged. RelaxedSchedule and its parameters stay unchanged.
Original lengths, ratios, retained identities, lost support, forfeited
estimates, and unchecked properties accompany each override. All lengths
remain positive: we use short finite intervals, not zero-length discontinuities.

OAT levels: T_w=26 and 1; T_p=59 and 1; T_a=4 and 1; T_f=56 and 8;
release hold=half its reference length and 2. These bracket explicit support
or slope thresholds and one deliberately abandoning choice, not a full product.

Combined candidates (local-data changes must be measured, not presumed zero):

| Candidate | T_w | T_p | T_a | T_f | Release hold | Interpretation |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| principal_support | 1 | 59 | 4 | 56 | 2 | Retains space for original main pulse and principal moment bumps, NOT solved moments; omits reserved patch layout and forfeits asymptotic estimates. |
| local_slope | 1 | 1 | 1 | 56 | 2 | Preserves smooth integral, eta removal slope bound and conditional Q; sacrifices pulse and angular supports and reserved machinery. |
| aggressive | 1 | 1 | 1 | 8 | 2 | Additionally sacrifices A.10 slope bound; retains its smooth theta formula and sequence, infinite ends, conditional Q. |

The word pressure-preserving is not used to claim equality with baseline:
length edits change the integral. Moment-aware means support-aware only.
None of the three is a complete matched exterior or a physical realization.

## Geometry targets and lower bounds

Radius decades are Delta y/(2 log(10)), not X decades. With the early
reference/axial stages and fixed transitions/collar retained, even deleting
all five adjustable intervals and the positive Q hold leaves
`1+T_d+1+1+1+3=19.71828183` log units, or 4.281770 radius decades. Thus
3 radius decades are impossible within the selected length-only scope,
independently of the pressure result. We do not alter an unrelated parameter
to force that target. Keeping the eta slope bound adds at least 55.45177444
log units, so 10 radius decades are impossible in that branch even before
including its other positive intervals and Q hold. Actual evaluated candidates
will determine the 30- and 10-decade status; targets are not fitted values.

### Conservative principal-support lower bound

During both unit release ramps, the Q source is nonnegative and 1+l<=1.
The intervening nonnegative-length l=-1 hold only increases Q. Thus
`Q_start >= exp(-2) Q_initial`, without estimating either ramp integral.
The conditional stopping construction therefore requires at least
`max(0,(log(Q_initial/Q_p)-2)/(1-h))=3.59800497` log units of Q hold.
Combining this with the fixed stages, T_p>11/lambda+3.15, T_a>3.15, and
T_f>=80 log(2) gives a strict lower bound of 30.415393 radius decades.
It holds with the same conditional Q initial value and fixed ramps/collar;
it is not a general theorem about every possible modified exterior.

The numerical outcomes are in the
[fourth-milestone report](experiment-log.md#fourth-milestone-schedule-compression-2026-09-10-utc).
The first run's crowded plot labels were corrected and the final workflow
rerun to a fresh `compressed_not_theorem_admissible_reference_v2` directory.
No earlier run was overwritten.