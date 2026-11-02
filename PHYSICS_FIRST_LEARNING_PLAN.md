# Physics-first learning plan (proposed, not yet activated)

**Recorded 2026-11-01, with the owner's added request to notice useful spin-offs.**
This is an **alternative learning roadmap**, not a replacement for the
mathematical/numerical plan in [PROJECT.md](PROJECT.md) or the bounded
seventh-milestone proposal in [SEVENTH_PROMPT.md](SEVENTH_PROMPT.md).

The owner would like to understand the fluid mechanics itself: how vortices
form, how small cores can arise, which Reynolds numbers matter, what balances
permit contraction, and what a practical experiment would measure. The existing
numerical work has not made these matters sufficiently clear.

**No stage is automatically authorized to run.** If a future request is
ambiguous about whether to resume numerical research, use this learning
plan, or leave both inactive, ask the owner and wait for an answer. Do not
run solvers, launch experiments, purchase equipment, or create a new
repository merely because this plan exists.

Read [PHYSICAL_INTERPRETATION.md](PHYSICAL_INTERPRETATION.md) for the
physical questions and the distinction between formal concentration and
validated flow. The existing repository results, including negative
numerical findings, remain part of the historical record.

## How a stage should work

Begin with the physical phenomenon and an accessible explanation, then
introduce enough mathematics to make its mechanism and limits precise.
For each authorized stage:

1. **Define the physical system.** Specify fluid, geometry, dimensions,
   velocities, forcing or boundary motion, and what is idealized.
2. **Explain the mechanism.** Identify vorticity, circulation, pressure,
   mass conservation, viscous diffusion, stretching, momentum and energy
   transfers. Keep Reynolds numbers tied to named velocity/length scales.
3. **Make a modest illustration or calculation** only if it genuinely
   advances understanding; label prescribed and solved fields correctly.
4. **Make predictions that could be checked.** Give observables, units,
   scales, error sources, and limitations, not merely attractive graphics.
5. **Stop for an explanation and review.** State what is understood,
   what was assumed, what is still unclear, and whether the owner wants
   any follow-up.

A useful failure to explain something is a reason to **clarify the model
before increasing numerical complexity**, not an automatic instruction to
run a more elaborate solver.

## Stage 1 — Understand an ordinary vortex in water

Questions: What do velocity, circulation, vorticity, radial pressure
gradient and viscous spreading mean? What is the vortex core, and how
should its radius be defined? What are the **apparatus** and **local core**
Reynolds numbers, and why can they differ?

Possible deliverable: one annotated diagram, explicit illustrative water
scales (speed, length and diffusion time), and a table distinguishing
established formulas, assumed inputs and measured quantities.

Do not infer that a small local Reynolds number establishes a unique
flow regime for a whole apparatus.

## Stage 2 — What can concentrate a vortex?

Use a classical stretched-vortex model, such as a **Burgers vortex**, to
explain the opposition between axial stretching/radial inflow and
viscous diffusion. Discuss how such an imposed strain field would be
produced—or might fail to be produced—in a finite vessel.

Possible deliverable: an intelligible diagram of radial inflow,
axial stretching, circulation and diffusion; a scale estimate with
its conventions and boundary conditions; and an explanation of why
a mathematically prescribed external strain is not a demonstrated
laboratory mechanism.

This classical example is **not** the singularity construction, and
a steady, driven vortex is not proof of finite-time blowup.

## Stage 3 — Could a real apparatus create and measure it?

Consider an illustrative water vessel. Compare candidate ways to
establish swirl and stretching (for example rotating surfaces,
recirculation or ports), and what cameras/tracers/pressure measurements
might reveal. Distinguish body forcing from boundary actuation.
Estimate physically meaningful size, speed, strain, diffusion,
pressure, power and uncertainty scales.

Possible deliverable: a first-pass feasibility table with
assumptions, measurement requirements, unknowns and potential
failure modes. No purchases or detailed apparatus design are implied.

## Stage 4 — Return to the paper with a physical vocabulary

Compare (a) the ordinary stretched vortex, (b) a hypothetical finite
physical analogue, and (c) the mathematical concentrating construction.

Ask why the oscillatory structures and averaged nonlinear stresses
are introduced; what transfers momentum or energy; and which extreme
scale hierarchies come from the proof versus any demonstrated physical
necessity.

Possible deliverable: a compact side-by-side map separating
**known mathematics**, **conditional dimensional estimates**,
**numerical results that passed their gates**, **failed/unattempted
computations**, and **untested engineering hypotheses**.

Do not call a prescribed shrinking plotting window a measured
contracting core. The repository has **no accepted nonlinear core
solution or demonstrated physical vortex**.

## Follow physically interesting or useful spin-offs

New ideas are not distractions to be silently discarded. As a stage is
discussed, look explicitly for **physical phenomena**, **possible
engineering uses**, **measurement methods**, and **teaching/visualization
opportunities** that are related but not necessary to finish the
central question.

Examples include vortex stretching, swirl-induced breakdown,
mixing and transport, cavitation near vortex cores, flow control,
or optical measurement of velocity. These are candidate avenues to
evaluate, not assumed practical benefits.

- A **small explanatory detour** is welcome within an authorized
  discussion if it illuminates the stage and can be completed without
  new experiments or a substantial new workstream.
- A promising **separate investigation** should be presented to the
  owner as an option, with why it is interesting, what would be
  learned or useful, and the smallest meaningful test. Ask before
  starting substantial coding, computation, an experiment, or a
  new repo.
- If it cannot be pursued now, **record it** in
  [notes/physical-opportunities.md](notes/physical-opportunities.md)
  under an appropriate category. Do not lose it just because the main
  line of research changes.
- If a separate study is later approved, link its results and any
  new repository from the opportunity entry. A Git branch or separate
  repository is not required merely to record an idea.

Every completed or paused stage should include a short
**"Physical or engineering spin-offs"** section with links to newly
recorded opportunities, even if the section simply says "None found."

## Stage-end decision gate

Before moving on, report:

- What physical insight did we acquire, and what remains confusing?
- Which Reynolds number, length scale and physical mechanism were used?
- Which aspects are imposed, calculated, measured or conjectured?
- What observables or order-of-magnitude estimates are credible?
- Which new opportunities arose, and were they noted in the backlog?
- Would the owner prefer to continue this learning sequence, pursue
  one opportunity, return to the earlier numerical roadmap, or stop?

**Wait for the owner's choice whenever that direction is not explicit.**
Do not use an old continuation prompt as automatic permission to proceed.
