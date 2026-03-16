# Step 03b: Redis batch client

Author: Vasiliy Zdanovskiy  
email: vasilyvz@gmail.com

**Step ID:** 03b  
**Target file:** `docs/search/engine/theory_index/redis_batch.py`

---

## Executor role

- **Role:** Implement exactly one step: add Redis client that loads scripts from step 03a and performs batch write (one script per file = replace) and batch read via EVAL/EVALSHA. No single-key loops in main path.
- **Input:** This step file + "Read first" (max 3 items).
- **Output:** New file `redis_batch.py`; confirmations; validation evidence.

---

## Execution directive

- Execute only this step. Do not change Lua script sources (03a) or add CLI.
- Read first the files listed in "Read first" before creating the file.
- Create only the target file. Stop immediately on any blackstop.

---

## Step scope

- **Target file:** `docs/search/engine/theory_index/redis_batch.py`
- **Type:** New file
- **Purpose:** Redis client; load scripts from redis_lua_scripts; EVAL/EVALSHA for per-file replace and batch read; connection from config.

---

## Dependency contract

- **Prerequisites:** Step 01 (config), Step 03a (redis_lua_scripts.py must exist).
- **Unlocks:** Step 06 (populate command).
- **Forbidden scope:** Do not add Lua script source code (use 03a); do not perform single-key read/write in a loop in the main data path; do not hardcode connection params.

---

## Required context

- **Spec reference:** TECH_SPEC.md §3.8 (Integrity, replace in one batch), §3.9 (Redis and Lua), §9.11–9.12.
- **Project rules:** .cursor/rules; file ≤350–400 lines; docstrings; type hints.
- **Wave:** 2 (parallel with 02, 04, 05).

---

## Read first (max 3 items)

- `docs/tech_spec/search/TECH_SPEC.md` — §3.8, §3.9, §9.11 (replace in one batch)
- `docs/search/engine/theory_index/redis_lua_scripts.py` — script names and KEYS/ARGV contract
- `docs/search/engine/theory_index/config.py` — Redis connection keys (host, port, password, db)

---

## Expected file change

- New module that: (1) connects to Redis using config (host, port, password, db — no hardcode); (2) loads script(s) from redis_lua_scripts (import or read); (3) provides batch write: one EVAL/EVALSHA per file (replace script from 03a) with keys/args built from file_id and chunk data; (4) provides batch read (Lua or pipeline) for multiple keys; no single-key loop in main path. All writes for one file go through the single replace script.

---

## Forbidden alternatives

- Do not implement per-file update as separate delete and insert calls; use one script invocation per file. Do not hardcode host/port/password. Do not put Lua script source in this file (use 03a). Do not read/write in a loop one key at a time in the main data path.

---

## Atomic operations

1. Create `redis_batch.py` with module docstring (Author, email) and imports (redis, theory_index.redis_lua_scripts).
2. Add function or class that takes config (or connection params) and exposes: write_file_replace(file_id, file_data, chunks_data) (or equivalent) calling the 03a script once; batch_read(...) if needed.
3. Connection from config; SCRIPT LOAD + EVALSHA or EVAL with script from 03a.
4. Unit tests: mock Redis; assert one script invocation per file; assert no single-key loop for bulk write. Keep file under 400 lines.

---

## Expected deliverables

- Single new file `redis_batch.py` with Redis client, script loading from 03a, batch write (replace per file) and batch read. Docstrings; type hints; no hardcode.

---

## Mandatory validation

1. `black docs/search/engine/theory_index/redis_batch.py`
2. `flake8 docs/search/engine/theory_index/redis_batch.py`
3. `mypy docs/search/engine/theory_index/redis_batch.py`
4. `pytest` (full project test suite — must be green)
5. Step-specific: unit test with mocked Redis; one script call per file for replace.

**Completion condition:** All of the above pass.

---

## Decision rules

| If | Then |
|----|------|
| Config has no Redis keys | Document required keys (host, port, etc.); raise clear error at use time if missing. |
| Script from 03a fails (e.g. wrong KEYS) | Return error to caller; do not retry with partial data. |

---

## Blackstops

- Stop and report if: existing pytest is red; connection params are hardcoded; Lua script source is duplicated in this file; main path uses single-key loop for bulk data; file exceeds 400 lines.

---

## Handoff package

- **Modified file:** `docs/search/engine/theory_index/redis_batch.py` (new)
- **Confirmations:** black, flake8, mypy, pytest passed
- **Validation evidence:** pytest output (last 20 lines)
- **Blockers:** None or list
