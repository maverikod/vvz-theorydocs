# Step 02: FAISS manager

Author: Vasiliy Zdanovskiy  
email: vasilyvz@gmail.com

**Step ID:** 02  
**Target file:** `docs/search/engine/theory_index/faiss_manager.py`

---

## Executor role

- **Role:** Implement exactly one step: add FAISS index lifecycle module. No search API; no CLI.
- **Input:** This step file + "Read first" (max 3 items).
- **Output:** New file `faiss_manager.py`; confirmations; validation evidence.

---

## Execution directive

- Execute only this step. Do not add vector search (top-k) or CLI.
- Read first the files listed in "Read first" before creating the file.
- Create only the target file. Stop immediately on any blackstop.

---

## Step scope

- **Target file:** `docs/search/engine/theory_index/faiss_manager.py`
- **Type:** New file
- **Purpose:** FAISS index: add vectors by chunk_id, save/load; path from config; dimension validation per batch.

---

## Dependency contract

- **Prerequisites:** Step 01 (config module must exist; faiss index path comes from config).
- **Unlocks:** Step 06 (populate command).
- **Forbidden scope:** Do not implement top-k/search; do not load config inside this module (receive config or path from caller); do not hardcode index path.

---

## Required context

- **Spec reference:** TECH_SPEC.md §3.2 (FAISS manager and index).
- **Project rules:** .cursor/rules; file ≤350–400 lines; docstrings; type hints.
- **Wave:** 2 (parallel with 03b, 04, 05).

---

## Read first (max 3 items)

- `docs/tech_spec/search/TECH_SPEC.md` — §3.2 (FAISS manager)
- `docs/search/engine/theory_index/config.py` — config shape / faiss_index_path (or equivalent key)
- Project root `pyproject.toml` — optional deps: faiss-cpu / faiss-gpu

---

## Expected file change

- New module with class (or functions) that: (1) add_vectors(chunk_ids, vectors) — add/update vectors keyed by chunk_id; validate same dimension for the batch, reject and log importance 8 if inconsistent; (2) save(path) and load(path) — persist/load index; path from config when called by caller. No search/top-k method in this phase. Dimension fixed per model (default 384); configurable or from caller.

---

## Forbidden alternatives

- Do not implement vector search (top-k lookup). Do not hardcode index path. Do not load config inside this module. Do not accept dimension mismatch within a batch without rejecting.

---

## Atomic operations

1. Create `faiss_manager.py` with module docstring (Author, email) and imports (faiss, typing).
2. Add class or API: add_vectors(chunk_ids, vectors), save(path), load(path).
3. In add_vectors: check all vectors same length; if not, reject batch and log importance 8.
4. Add unit tests: build with dummy vectors, save/load round-trip, dimension check rejects inconsistent batch.
5. Keep file under 400 lines.

---

## Expected deliverables

- Single new file `faiss_manager.py` with docstrings, type hints, no hardcode, no TODO/pass (except in exception handlers).

---

## Mandatory validation

1. `black docs/search/engine/theory_index/faiss_manager.py`
2. `flake8 docs/search/engine/theory_index/faiss_manager.py`
3. `mypy docs/search/engine/theory_index/faiss_manager.py`
4. `pytest` (full project test suite — must be green)
5. Step-specific: unit test(s) for save/load and for batch dimension rejection.

**Completion condition:** All of the above pass.

---

## Decision rules

| If | Then |
|----|------|
| Vectors in batch have different lengths | Reject batch; log importance 8; do not add to index. |
| Path for save/load is empty or invalid | Raise clear error or document contract (caller provides valid path). |

---

## Blackstops

- Stop and report if: existing pytest is red; file exceeds 400 lines; index path is hardcoded; top-k/search is implemented; config is loaded inside this module.

---

## Handoff package

- **Modified file:** `docs/search/engine/theory_index/faiss_manager.py` (new)
- **Confirmations:** black, flake8, mypy, pytest passed
- **Validation evidence:** pytest output (last 20 lines)
- **Blockers:** None or list
