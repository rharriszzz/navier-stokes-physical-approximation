# Initial Codex Prompt

Use this as the first instruction after opening the repository in Codex Local.

---

Read `RESEARCH_CONTEXT.md` first so you understand the scientific goal and the decisions already made.

Then read `PROJECT.md` completely.

Carry out only **Tasks 1–6** in the section titled **"Immediate task for the coding agent"**, in order.

Use the local WSL2 Ubuntu environment for Python execution.

Before implementing any mathematical formula from the Navier–Stokes blowup construction, read the cited source paper directly and record the corresponding paper equation number in `notes/equation-map.md` and, where useful, in source-code comments.

Do not guess uncertain formulas from summaries.

For this first pass:

- keep the implementation CPU-first and transparent;
- use double precision;
- do not require JAX, PyTorch, or GPU acceleration yet;
- do not build a full 3-D solver;
- do not use nekRS;
- do not over-engineer the repository;
- write tests for the coordinate transforms and cylindrical differential operators as they are introduced;
- save generated plots and concise run summaries in a sensible results directory;
- keep large numerical output out of Git.

After completing Task 6, stop and report:

1. exactly which equations from the paper were implemented;
2. which approximations, cutoffs, or terms were omitted;
3. the grid or grids used;
4. the measured divergence error;
5. whether the expected concentrating-core scaling was reproduced;
6. the generated plots and where they are saved;
7. all test results;
8. any numerical-conditioning or cancellation issues noticed;
9. any ambiguity in the paper that matters for implementation;
10. your recommendation for the next experiment.

Do **not** proceed automatically to a time-dependent full Navier–Stokes solver or to 3-D DNS.

The immediate goal is to establish a trustworthy numerical representation of the published concentrating core and its finite-truncation residual before adding more machinery.
