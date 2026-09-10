# Fourth Milestone Prompt — Schedule-Compression and Sacrifice Audit

Read, in this order:

1. `README.md`
2. `RESEARCH_CONTEXT.md`
3. `PROJECT.md`
4. `SECOND_PROMPT.md`
5. `THIRD_PROMPT.md`
6. `notes/equation-map.md`
7. `notes/numerical-method.md`
8. all three milestone sections of `notes/experiment-log.md`
9. the relevant source-paper sections directly, especially Appendix A.2–A.5 and Appendix B.1–B.3

Do not rely on project summaries where an exact paper condition is needed.

---

# Decision for this milestone

Do **not** solve the nonlinear core equations (B.15) yet.

The third milestone established that the relaxed scheduled pressure datum can be
computed accurately and that, for compressed pressure amplitude, the first
explicit Appendix-B correction can be modest at Lambda around 128–512.

However, the baseline relaxed schedule still spans

```text
Delta y = 324.409099
log10(X_outer/X_R) = 140.889082
```

or about 70.44 decades in physical radius at fixed q.

That global geometric separation is now the dominant obstacle to physical
interpretation.

The purpose of this milestone is therefore:

> **Determine which long Appendix-A schedule intervals are essential to the local pressure/core data, which are present for later proof machinery, and how far the schedule can be shortened before specific matching, moment, stress, or pressure properties are lost.**

This is an explicitly modified finite model.

No shortened schedule is theorem-admissible unless separately proved.

---

# Confirmed starting point

The following third-milestone results may be treated as validated:

- the stage-by-stage implementation of (A.5)–(A.13);
- the Q evolution and Q_p stopping construction;
- the complete scheduled pressure integral (A.21);
- analytic first and second eta derivatives;
- symmetry and sign checks;
- pressure quadrature convergence;
- Z_star from (B.1);
- the first explicit diagnostic `delta U1=-Y Z_star/(2 L Lambda)`.

The baseline relaxed parameters are:

```text
M_d = 1
P_star = 2
lambda = 0.2
h = 0.005
j0 = 0.025
T_f = 64
c_o = 0.025
```

The baseline finite stage lengths are approximately:

```text
inner slope transition        1
axial reduction              12.718282
transition to -lambda         1
intermediate power           96.566275
axial-pulse swirl interval   65
eta-removal interpolation    64
angular-bump interval        48.283137
release down                  1
release hold                 21.193269
release up                    1
Q stopping hold               9.648136
terminal collar               3
```

The four intervals

```text
intermediate power
axial-pulse swirl interval
eta-removal interpolation
angular-bump interval
```

account for about 84.4% of the finite logarithmic span.

Yet their pressure contributions after the early axial transition are tiny in
the third-milestone baseline.

This does **not** automatically authorize deleting them: several exist to
support moment matching, pulse construction, stress inequalities, or later
corrections.

---

# Task 1 — Build a condition/dependency map for every stage

Before changing code, reread Appendix A.2–A.5 and make a table mapping every
finite schedule stage to its mathematical role.

For each stage record:

- source equation / proposition / page;
- prescribed length formula;
- whether that exact length affects `Pi0`;
- whether it is needed for axial moment matching;
- angular moment matching;
- the S-moment pulse construction;
- Q evolution / terminal matching;
- stress-cone estimates;
- reserved support for later correction layers;
- heat compensation;
- higher-order background or phase-averaged corrections;
- inner/exterior matching;
- any separation-of-support argument;
- any explicitly stated smallness estimate depending on its length.

Classify each role as one of:

```text
P = pressure/local-axis-data relevant
M = moment/matching relevant
S = stress-cone or admissible-stress relevant
R = reserved for later proof correction machinery
T = terminal/Q matching relevant
U = unclear; needs further source audit
```

Do not infer that an interval is expendable merely because its pressure
contribution is small.

Save this table in `notes/equation-map.md` or a new clearly linked note.

---

# Task 2 — Distinguish hard constraints from proof-scale margins

For every stage length, determine whether the paper gives:

1. an exact identity or support requirement that cannot simply be shortened;
2. a finite minimum implied by explicit bump widths or ordering;
3. a sufficient asymptotic length chosen to obtain clean estimates;
4. a reserved region for later corrections that are outside our current finite model;
5. an unspecified "sufficiently large" separation.

This distinction is central.

For example, do not treat

```text
T_w = 60 log(1/lambda)
```

as physically mandatory without identifying what the factor 60 is used to
guarantee.

Similarly, identify what would fail if the following are shortened:

- `T_w`;
- `13/lambda`;
- `T_f`;
- `30 log(1/lambda)`;
- `4 log(1/h)`.

For `T_f`, preserve the explicit interpolation-slope bound in one branch of
the experiment and separately label any run that violates it.

For the Q stopping hold, do **not** shorten it arbitrarily while claiming the
same terminal matching. It is derived from `Q_start` and `Q_p`.

---

# Task 3 — Add an explicitly modified schedule model

Do not alter or overwrite `RelaxedSchedule`.

Create a separate model/config whose name contains something like:

```text
compressed_not_theorem_admissible
```

The existing relaxed schedule remains the reference.

Allow selected stage lengths to be overridden or multiplied by explicit
compression factors.

Every override must carry metadata stating:

- original paper length;
- modified length;
- ratio;
- exact conditions known to remain satisfied;
- conditions intentionally sacrificed;
- conditions not checked.

Do not silently change formulas for `E`, `f`, `l`, `Q`, or `Pi0`.

The experiment is about changing lengths, not inventing a new arbitrary
pressure profile.

---

# Task 4 — One-at-a-time sensitivity study

Begin from the third-milestone baseline.

Shorten **one long interval at a time** while leaving all others unchanged.

Prioritize:

1. intermediate power interval;
2. axial-pulse swirl interval;
3. angular-bump interval;
4. eta-removal interval;
5. release `l=-1` hold.

For each interval use a small number of compression levels chosen from the
source audit rather than a huge Cartesian sweep.

For each modified schedule recompute:

- total `Delta y`;
- `log10(X_outer/X_R)`;
- radius decades = half the X decades;
- `Pi0`;
- `Pi0_eta`;
- `Pi0_etaeta`;
- `Z_star`;
- first explicit correction for Lambda = 128 and 512;
- Q diagnostics where applicable.

Compare against the unmodified relaxed baseline.

Use normalized changes such as:

```text
||Pi0_modified-Pi0_baseline||inf / ||Pi0_baseline||inf
||Pi0_eta_modified-Pi0_eta_baseline||inf / max(1,||Pi0_eta_baseline||inf)
||Zstar_modified-Zstar_baseline||inf / max(1,||Zstar_baseline||inf)
```

The point is to identify intervals that consume enormous geometry while having
little influence on local core data.

---

# Task 5 — Preserve-versus-sacrifice experiments

Construct a small number of combined compressed schedules in increasing order
of aggressiveness.

A useful conceptual hierarchy is:

## A. Pressure-preserving/local-data experiment

Keep enough stage structure that the (A.21)-style pressure evaluator remains
well-defined and smooth, but permit removal of proof-reserved support intervals
that are not needed for the local datum.

## B. Moment-aware experiment

Retain explicit support needed for the principal radial/angular moment
adjustments that can be identified from Appendix A, but omit support reserved
only for later all-orders corrections.

## C. Aggressive physical analogue

Keep the qualitative sequence

```text
inner profile
axial reduction
outer decay
eta removal
transition to terminal tail
```

plus whatever Q/terminal matching remains mathematically coherent, while
explicitly abandoning proof-only pulse/moment/stress guarantees.

Do not use these labels unless the dependency audit supports them.

For every combined schedule include a **sacrifice matrix** stating exactly what
paper properties are no longer being asserted.

---

# Task 6 — Target geometry rather than arbitrary compression factors

Try to determine whether useful variants can reach approximate radial spans of:

```text
30 decades
10 decades
3 decades
```

where these are **radius** decades, not X decades.

These are diagnostic targets, not success criteria.

If a target cannot be reached without sacrificing a particular condition,
state which condition blocks it.

Do not force a schedule to hit a target by changing an unrelated parameter.

The most important output is a Pareto-style relationship:

> radial scale separation versus retained mathematical structure versus change in local pressure/core data.

---

# Task 7 — Identify what should precede B.15

At the end, recommend one of the following:

```text
A. Solve B.15 using the original relaxed schedule datum.
B. Solve B.15 using a specific compressed schedule datum.
C. Do not solve B.15 yet because compression destroys a core prerequisite.
D. First implement a particular missing moment/stress condition.
```

Base this choice on quantitative results, not intuition.

If one compressed schedule changes `Pi0`, its derivatives, and `Z_star` only
slightly while reducing radius separation dramatically, that schedule should
be the leading candidate for the later core-only nonlinear solve.

---

# Validation

Retain all existing tests.

Add tests for:

- exact reproduction of the unmodified relaxed schedule when all compression
  factors are one;
- schedule join continuity for modified runs;
- pressure quadrature convergence;
- derivative convergence;
- Q endpoint identities where Q-related stages are retained;
- explicit failure when an override makes a required stage length nonpositive;
- correct metadata for sacrificed conditions.

Do not define a successful test merely as "the code ran."

---

# Plots

Produce a small set of scientifically useful plots:

1. cumulative logarithmic radius with stage labels for baseline versus compressed schedules;
2. `Pi0` comparison;
3. `Z_star` comparison;
4. local-data error versus radius-decades saved;
5. a condition-retention / geometry summary figure or table.

Avoid generating dozens of nearly duplicate plots.

---

# Stop conditions

Stop and report if:

- source dependencies of a dominant interval remain materially ambiguous;
- shortening a stage invalidates the pressure formula itself;
- Q/terminal matching becomes incoherent;
- pressure derivatives cease to converge;
- local data change by order one before geometry becomes substantially smaller;
- or the only way to reach physically interesting geometry is to abandon nearly
  every structural feature of Appendix A.

All are useful conclusions.

---

# Do not do yet

Do not:

- solve (B.15);
- time-integrate Navier–Stokes;
- implement oscillatory realization;
- run 3-D CFD;
- claim dynamical concentration;
- claim physical realizability;
- claim theorem admissibility;
- optimize for GPU.

---

# Required report

Append a new dated milestone section to `notes/experiment-log.md`.

Report:

1. stage-condition dependency matrix;
2. hard constraints versus proof-scale margins;
3. each one-at-a-time compression;
4. combined compressed candidates;
5. explicit sacrificed conditions for each;
6. total X and radius scale separation;
7. changes in `Pi0`, derivatives, `Z_star`, and first correction;
8. Q/terminal status;
9. which interval lengths dominate the remaining geometry;
10. whether a compressed candidate is suitable for a core-only B.15 solve;
11. recommended next milestone.

Then stop for review.

The central question is:

> **Can we remove most of the 70-decade radial geometry while retaining enough of the Appendix-A mechanism that the local pressure datum and inner-core forcing remain essentially unchanged, and can we state precisely what proof guarantees were sacrificed to do so?**
