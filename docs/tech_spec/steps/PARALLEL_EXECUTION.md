# Parallel execution guide (LLAMA-level models)

Author: Vasiliy Zdanovskiy  
email: vasilyvz@gmail.com

This document defines how to assign steps to multiple executors (e.g. LLAMA-level models with limited context) so that work proceeds in **parallel** with minimal coordination and no need for full codebase context.

---

## Principles

1. **One step = one agent.** Assign each step to a single executor. The executor receives only the step file and the items in “Read first” (max 3).
2. **No cross-step reading.** An executor does not read other step files or the full TECH_SPEC. Required spec section is stated inside the step file.
3. **Dependencies are by artifact.** Step B depends on step A only in the sense that the **target file** of A must exist before B runs. The executor of B reads A’s output file(s) only if listed in B’s “Read first”.
4. **Waves enforce order.** Steps in the same wave can run in parallel. Steps in wave N+1 start only after all steps in wave N are complete and their target files are committed.

---

## Waves and assignment

| Wave | Steps | Assign to | Notes |
|------|-------|-----------|--------|
| **1** | 01, 03a, 09 | Agent A, Agent B, Agent C | 01 = config; 03a = Lua scripts only; 09 = Docker build. No shared deps. |
| **2** | 02, 03b, 04, 05 | Agent D, Agent E, Agent F, Agent G | After Wave 1: 01 and 03a exist. 02, 04, 05 need config (01). 03b needs 01 and 03a. |
| **3** | 06 | Agent H | Populate command; needs 02, 03b, 04, 05. |
| **4** | 07 | Agent I | Add command; needs 06. |
| **5** | 08 | Agent J | CLI; needs 07. |
| **6** | 10 | Agent K | Run container; needs 09. Can run in parallel with 02–08 if desired. |

**Maximum parallel width:** Wave 1 = 3 agents, Wave 2 = 4 agents. Total steps = 11 (01, 02, 03a, 03b, 04, 05, 06, 07, 08, 09, 10).

---

## Handoff between waves

- **Completion condition for a step:** All validation commands pass (black, flake8, mypy, **all tests pass**). The step is not done until the test suite is green.
- **Before starting wave N+1:** Ensure all target files from wave N are present and the test suite still passes (run full pytest after merging or applying wave N results).
- **Conflict avoidance:** Each step touches only its **target file**. No step modifies another step’s target. The only integration point is the **populate** command (06), which imports modules from 02, 03b, 04, 05; no concurrent edits to the same file.

---

## Context budget (LLAMA-level)

- **Per step:** “Read first” must list **at most 3 items** (paths or spec sections). Example: `TECH_SPEC.md §9.14`, `theory_index/config.py`, `theory_index/redis_lua_scripts.py`.
- **Step file size:** Step file should be concise (template sections only; no long prose). Target: step file + 3 “Read first” documents ≤ ~8K–16K tokens so a single context window suffices.
- **Spec reference:** In each step file, “Required context” names **exactly one** primary TECH_SPEC section (e.g. §9.11 and §9.12 for Redis Lua). The executor does not need to read the entire TECH_SPEC.

---

## If X then Y (for assigners)

| If | Then |
|----|------|
| Step 01 or 03a or 09 fails validation | Do not start Wave 2. Fix the failed step and re-run its validation. |
| Step 02, 03b, 04, or 05 fails | Do not start Wave 3. Fix the failed step; ensure 01 and (for 03b) 03a are unchanged. |
| Full test suite is red after a wave | Fix the failing step(s) in that wave before starting the next wave. Do not proceed with “we’ll fix later”. |
| Executor has no access to prerequisite file | Provide the prerequisite target file (e.g. config.py) as a read-only input; executor still writes only its own target file. |

---

## Summary

- **Wave 1:** 3 steps in parallel (01, 03a, 09).  
- **Wave 2:** 4 steps in parallel (02, 03b, 04, 05).  
- **Waves 3–5:** One step each (06 → 07 → 08).  
- **Wave 6:** Step 10 (optional parallel to 02–08).  
- Each step is self-contained; max 3 “Read first” items; one primary spec section; completion = all tests pass.
