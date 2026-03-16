# Step file template (canonical)

Author: Vasiliy Zdanovskiy  
email: vasilyvz@gmail.com

Every step file in this directory **must** contain the following sections. No code snippets; only exact file names, entry points, and expected change.

**Optimization for LLAMA-level executors:** "Read first" lists **at most 3 items**. One primary spec section in "Required context". Step file + Read first should fit in ~8K–16K tokens. No step requires reading the full codebase or entire TECH_SPEC.

---

## Executor role

- **Role:** [Executor model: implement exactly one step; no architectural changes outside this step.]
- **Input:** This step file + "Read first" (max 3 items). No other step files or full spec.
- **Output:** One modified/created code file; confirmations; validation evidence.

---

## Execution directive

- Execute **only** this step. Do not implement alternative designs or extra features.
- **Read first** the files listed in "Read first" before editing.
- Modify **only** the target file stated in "Step scope".
- **Stop immediately** on any blackstop (see Blackstops).
- Do not add code to other files unless the step scope explicitly includes them.

---

## Step scope

- **Target file:** [exact path, e.g. `docs/search/engine/theory_index/faiss_manager.py`]
- **Type:** [new file | existing file]
- **Purpose:** [one sentence]

---

## Dependency contract

- **Prerequisites:** [Step IDs or "None"; required so that dependencies are satisfied before this step.]
- **Unlocks:** [Step IDs that may start after this step.]
- **Forbidden scope:** [What this step must not touch; e.g. "Do not change CLI or config loading in core."]

---

## Required context

- **Spec reference (one primary section or one logical block):** TECH_SPEC.md §X.Y [e.g. §9.12 for Redis Lua; §9.14 for chunker]. If the step spans two tightly coupled subsections (e.g. §9.11 and §9.12), name both as a single "block" so the executor reads only that scope.
- **Project rules:** .cursor/rules (standards, science, search); file size ≤350–400 lines; one class = one file where applicable.

---

## Read first (max 3 items)

- [Exact path or spec section 1] — [entry point or section purpose]
- [Exact path or spec section 2] — [entry point or section purpose]
- [Optional third item] — [entry point or section purpose]

Do not list more than 3 items. Executor needs only these to complete the step.

---

## Expected file change

- [Concrete description: what will exist in the target file after the step. E.g. "Class FaissManager with methods add_vectors(chunk_ids, vectors), save(path), load(path); dimension check in add_vectors; path from config."]
- No placeholder logic (no TODO, no pass except in exception handlers); no hardcoded URLs or paths.

---

## Forbidden alternatives

- [Explicit list of what the executor must not do; e.g. "Do not implement vector search (top-k). Do not load config inside this module. Do not use a global default path."]

---

## Atomic operations

- [List of atomic edits or operations that together achieve the expected change; e.g. "1. Create file with module docstring and imports. 2. Add class FaissManager. 3. Add method add_vectors. 4. Add method save. 5. Add method load."]

---

## Expected deliverables

- Single file: [target path] with [brief description].
- All new code: docstrings (file, class, method); type hints; no hardcode; no incomplete code.

---

## Mandatory validation

1. `black <target file or package>`
2. `flake8 <target file or package>`
3. `mypy <target file or package>` (or project mypy config)
4. `pytest` (full project test suite — must be green)
5. [Step-specific check if any, e.g. "Unit test for FaissManager save/load round-trip."]

**Completion condition:** All of the above pass. Step is not done until tests are green.

---

## Decision rules

| If | Then |
|----|------|
| [Condition relevant to this step] | [Action] |

---

## Blackstops

- **Stop and report** if: [e.g. "Existing tests are red before any edit." | "Config is loaded inside the new module." | "Target file exceeds 400 lines."]
- Do not proceed until blocker is resolved or step scope is explicitly adjusted.

---

## Handoff package

After completion, the executor must provide:

- **Modified file:** [path]
- **Confirmations:** All validation commands passed; no blackstop hit.
- **Validation evidence:** [e.g. "pytest output (last 20 lines)."]
- **Blockers:** None, or list of open blockers that prevent the next step.
