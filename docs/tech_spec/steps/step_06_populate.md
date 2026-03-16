# Step 06: Populate command

Author: Vasiliy Zdanovskiy  
email: vasilyvz@gmail.com

**Step ID:** 06  
**Target file:** `docs/search/engine/theory_index/commands/populate.py`

---

## Executor role

- **Role:** Implement exactly one step: add the populate command — discover *.md, chunk via chunker_client, optionally enrich via summary_llm, write Redis (Lua replace) + FAISS; receive resolved config from CLI; no argparse in this module.
- **Input:** This step file + "Read first" (max 3 items).
- **Output:** New file `commands/populate.py`; confirmations; validation evidence.

---

## Execution directive

- Execute only this step. Do not add add command or CLI entrypoint logic.
- Read first the files listed in "Read first" before creating the file.
- Create only the target file. If `theory_index/commands/` is a new package, the only other file allowed in this step is `commands/__init__.py` (minimal, for import). No other code files. Stop immediately on any blackstop.

---

## Step scope

- **Target file:** `docs/search/engine/theory_index/commands/populate.py`
- **Type:** New file
- **Purpose:** Populate command: discover *.md, chunk (chunker_client), optionally enrich (summary_llm), write Redis (redis_batch replace per file) + FAISS (faiss_manager); receive resolved config; no argparse.

---

## Dependency contract

- **Prerequisites:** Steps 02, 03b, 04, 05 (faiss_manager, redis_batch, chunker_client, summary_llm and config must exist).
- **Unlocks:** Step 07 (add command).
- **Forbidden scope:** Do not parse CLI arguments in this module; do not load config (receive ready config from caller); do not add add command logic (mtime, lock file) here.

---

## Required context

- **Spec reference:** TECH_SPEC.md §3.5 (Application structure: Commands layer), §3.8 (replace in one batch), pipeline in §1.
- **Project rules:** .cursor/rules; file ≤350–400 lines; docstrings; type hints.
- **Wave:** 3 (after Wave 2).

---

## Read first (max 3 items)

- `docs/tech_spec/search/TECH_SPEC.md` — §3.5 (Commands), §1 (pipeline: discover → chunk → enrich → write Redis + FAISS)
- `docs/search/engine/theory_index/faiss_manager.py` — add_vectors, save, load
- `docs/search/engine/theory_index/redis_batch.py`, `chunker_client.py`, `summary_llm.py` — entry points (write_file_replace or equivalent; chunker and LLM call interfaces)

---

## Expected file change

- New module under theory_index/commands/: function or entry point that (1) receives resolved config and optional args (e.g. directory or file list); (2) discovers *.md files; (3) for each file: call chunker_client → get chunks+vectors+BM25; optionally call summary_llm per chunk/segment; (4) write Redis via redis_batch (one replace script per file); (5) add vectors to FAISS via faiss_manager. No argparse; config is passed in. Pipeline must use replace-in-one-batch for each file.

---

## Forbidden alternatives

- Do not parse sys.argv or use argparse in this module. Do not load config from file or env in this module. Do not implement mtime check or lock file (that is step 07). Do not write to Redis with separate delete and insert (must use one script per file).

---

## Atomic operations

1. Ensure `theory_index/commands/` exists with __init__.py if the project layout requires it.
2. Create `commands/populate.py` with module docstring (Author, email) and imports (config, chunker_client, redis_batch, faiss_manager, summary_llm).
3. Implement run_populate(config, ...) (or equivalent) that runs the pipeline; call redis_batch once per file (replace); call faiss_manager.add_vectors for the file’s chunks.
4. Add unit test that mocks chunker, Redis, FAISS and asserts flow (optional: integration test skippable in CI). Keep file under 400 lines.

---

## Expected deliverables

- Single deliverable code file: `commands/populate.py`. Optionally `commands/__init__.py` if the package is created in this step (no other files). Docstrings; type hints; no argparse; no config loading.

---

## Mandatory validation

1. `black docs/search/engine/theory_index/commands/populate.py`
2. `flake8 docs/search/engine/theory_index/commands/populate.py`
3. `mypy docs/search/engine/theory_index/commands/populate.py`
4. `pytest` (full project test suite — must be green)
5. Step-specific: test with mocks that populate calls chunker, redis_batch (one call per file), faiss_manager.

**Completion condition:** All of the above pass.

---

## Decision rules

| If | Then |
|----|------|
| Chunker returns error or rejected batch | Propagate error; do not write partial data for that file. |
| Redis or FAISS write fails for one file | Fail that file; do not roll back other files (one file = one script). |

---

## Blackstops

- Stop and report if: existing pytest is red; argparse or config loading is in this module; mtime/lock logic is implemented here; file exceeds 400 lines.

---

## Handoff package

- **Modified file:** `docs/search/engine/theory_index/commands/populate.py` (new)
- **Confirmations:** black, flake8, mypy, pytest passed
- **Validation evidence:** pytest output (last 20 lines)
- **Blockers:** None or list
