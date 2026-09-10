# Suggested AI Project Handoff Process

The goal of this process is to make the repository, not the conversation, the authoritative project state.

A chat should be disposable. A fresh AI should be able to resume the project accurately from a small number of repository files without rereading a long transcript.

---

## Core principle

Use Git and a few canonical project files to preserve:

- current accepted state;
- current next task;
- detailed experiment history;
- major scientific decisions;
- technical equation/method references.

Do **not** rely on accumulated chat history as the primary handoff mechanism.

---

## Recommended canonical files

### `STATUS.md`

This is the authoritative current project state.

It should be rewritten at the end of each milestone and contain only the current understanding.

Recommended sections:

```text
ESTABLISHED

FAILED / REJECTED

OPEN QUESTIONS

NOT YET ATTEMPTED

CURRENT NUMERICAL REFERENCE

CURRENT SCIENTIFIC INTERPRETATION
```

Examples of the distinction:

```text
ESTABLISHED:
- Appendix-A pressure datum validated numerically.
- Narrow g^2 source resolved at the selected reference tuple.

FAILED / REJECTED:
- No accepted nonlinear B.15 solution yet.
- Current global eta representation develops endpoint instability.

OPEN QUESTIONS:
- Can a multi-domain eta discretization stabilize B.15?
- Is the finite fixed-point map contractive?

NOT YET ATTEMPTED:
- Global moment/stress compatibility.
- Outer matching.
- Time integration.
- Laboratory realization.
```

This file should be concise enough for a new AI to read first.

---

### `NEXT_TASK.md`

This is the only active AI task prompt.

Instead of creating:

```text
SEVENTH_PROMPT.md
EIGHTH_PROMPT.md
NINTH_PROMPT.md
...
```

replace `NEXT_TASK.md` at the end of every milestone.

Git history preserves previous versions automatically.

A new conversation can then begin with:

```text
Read STATUS.md and follow NEXT_TASK.md.
Consult the project notes as needed.
```

The task should be narrow and bounded.

It should clearly state:

- fixed parameters;
- what may change;
- what must not change;
- validation requirements;
- stop conditions;
- required report;
- exact next gate.

---

### `notes/experiment-log.md`

Keep this as the append-only scientific record.

Each milestone should add a dated section containing:

- equations used;
- numerical formulation;
- parameters;
- grids/resolution;
- convergence results;
- failed runs;
- residuals;
- plots/results;
- hardware/software information;
- interpretation;
- next recommendation.

This is the detailed historical record.

`STATUS.md` summarizes the current accepted interpretation.

---

### `notes/decisions.md`

Keep a short record of important strategic decisions.

Examples:

```text
- The project is not attempting to reproduce the theorem hierarchy literally.
- Relaxed finite models must always be labeled NOT theorem-admissible.
- Pressure surrogates may not be invented.
- Do not change sigma_star until the current endpoint numerical problem is understood.
- Small fixed-point increments are not evidence of a solved nonlinear core.
```

The purpose is to prevent a new AI from unknowingly reopening questions that were already deliberately decided.

Each entry should include:

```text
date
decision
reason
what would justify revisiting it
```

---

### `HANDOFF.md`

This should be a very short entry point.

Example:

```text
# Start Here

1. Read STATUS.md.
2. Read NEXT_TASK.md.
3. Read notes/decisions.md.
4. Consult notes/equation-map.md and notes/numerical-method.md for technical details.
5. Consult notes/experiment-log.md for historical results.
6. Do not rely on old prompts or old chats unless something is missing.
```

This file should rarely need to change.

---

## Existing technical reference files

Keep the existing technical files:

```text
notes/equation-map.md
notes/numerical-method.md
```

Their purpose is different from `STATUS.md`.

`notes/equation-map.md` should answer:

> What exact source equations correspond to the implemented quantities?

`notes/numerical-method.md` should answer:

> How are those equations represented and solved numerically?

Neither should become a general status summary.

---

## End-of-milestone procedure

At the end of every substantial milestone, the AI should perform these steps in order:

```text
1. Append detailed results to notes/experiment-log.md.

2. Update STATUS.md.
   Remove obsolete current-state statements.
   Preserve only the present accepted interpretation.

3. Update notes/decisions.md only if a strategic decision was made or changed.

4. Replace NEXT_TASK.md with the recommended next bounded milestone.

5. Run the full relevant test suite.

6. Record the Git commit, dirty status, numerical environment and result paths.

7. Commit the milestone.

8. Stop for review.
```

The AI should not silently begin the next milestone after writing `NEXT_TASK.md`.

---

## Required status discipline

Every numerical result should be classified correctly.

Use terminology such as:

```text
validated
accepted numerical solution
failed acceptance test
diagnostic only
first-order estimate
not theorem-admissible
not physically realizable
not dynamically simulated
not yet attempted
```

Avoid ambiguous statements such as:

```text
works
looks good
seems solved
probably physical
```

A result belongs in `ESTABLISHED` only when its stated validation criteria were actually met.

---

## Failed runs are first-class results

Do not hide or overwrite failed runs.

If a run fails because:

- residuals do not converge;
- derivatives become unstable;
- the source is underresolved;
- the fixed-point map is not contractive;
- a parameter condition fails;

record that clearly in `notes/experiment-log.md`.

Then summarize the consequence in `STATUS.md`.

A failed numerical acceptance test is different from evidence that a mathematical solution does not exist.

---

## Git should replace chains of archival prompts

Git already preserves every version of:

```text
STATUS.md
NEXT_TASK.md
notes/decisions.md
notes/experiment-log.md
```

Therefore there is usually no need to preserve a growing chain of:

```text
SECOND_PROMPT.md
THIRD_PROMPT.md
FOURTH_PROMPT.md
...
```

Old prompts may remain in the current repository for historical reasons, but the preferred future workflow is one evolving `NEXT_TASK.md`.

Likewise, milestone-specific progress summaries should normally be replaced by one evolving `STATUS.md`.

---

## Conversation transcripts

Full conversation transcripts are optional archival material.

They can be useful when:

- investigating why a decision was made;
- reconstructing a missing handoff;
- preserving historical context.

They should **not** be the primary operational record.

The repository should contain enough structured state that a new AI does not need the transcript.

If a transcript is saved, treat it as archival evidence, not authoritative project status.

---

## Starting a fresh AI conversation

The preferred opening message should be short:

```text
Please read HANDOFF.md, then STATUS.md and NEXT_TASK.md.
Consult the linked project notes as needed.
Do not begin work until you understand the current accepted state and stop conditions.
```

The AI should not need the previous chat.

---

## Recommended repository structure

A future cleaned-up structure could look like:

```text
README.md
PROJECT.md
RESEARCH_CONTEXT.md

HANDOFF.md
STATUS.md
NEXT_TASK.md

notes/
    decisions.md
    equation-map.md
    numerical-method.md
    experiment-log.md

configs/
src/
scripts/
tests/
results/
```

This structure separates:

```text
orientation       -> HANDOFF.md
current state     -> STATUS.md
next action       -> NEXT_TASK.md
decisions         -> notes/decisions.md
source equations  -> notes/equation-map.md
numerics          -> notes/numerical-method.md
history           -> notes/experiment-log.md
```

---

## Why this is preferable

This process should reduce:

- token use;
- repeated explanations;
- contradictory summaries;
- accidental reuse of outdated prompts;
- dependence on one long conversation;
- confusion between accepted and rejected numerical results.

It should also make the project easier to audit scientifically.

A fresh AI should be able to answer three questions quickly:

```text
What do we actually know?

What has already failed?

What exact experiment should I run next?
```

If the repository answers those three questions clearly, the handoff is working.
