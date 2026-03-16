# Step 03a: Redis Lua script sources

Author: Vasiliy Zdanovskiy  
email: vasilyvz@gmail.com

**Step ID:** 03a  
**Target file:** `docs/search/engine/theory_index/redis_lua_scripts.py`

---

## Executor role

- **Role:** Implement exactly one step: add a module that contains **only** Lua script sources (strings) for Redis. No Redis client code.
- **Input:** This step file + "Read first" (max 3 items).
- **Output:** New file `redis_lua_scripts.py`; confirmations; validation evidence.

---

## Execution directive

- Execute only this step. Do not add Redis connection or EVAL/EVALSHA logic.
- Read first the files listed in "Read first" before creating the file.
- Create only the target file. Stop immediately on any blackstop.

---

## Step scope

- **Target file:** `docs/search/engine/theory_index/redis_lua_scripts.py`
- **Type:** New file
- **Purpose:** Lua script sources only. One script: replace file — delete all keys for file_id, then write new file + chunks + keywords + faiss_link. Keys/ARGV contract documented in module.

---

## Dependency contract

- **Prerequisites:** None
- **Unlocks:** Step 03b (Redis client will load and EVAL these scripts).
- **Forbidden scope:** Do not import redis or perform any I/O; do not add Redis client code.

---

## Required context

- **Spec reference:** TECH_SPEC.md §9.11 (Integrity, atomicity, file update replace-in-one-batch), §9.12 (Redis and Lua, keys layout).
- **Project rules:** .cursor/rules; file ≤350–400 lines; docstrings; type hints.
- **Wave:** 1 (parallel with 01, 09).

---

## Read first (max 3 items)

- `docs/tech_spec/search/TECH_SPEC.md` — §9.11 (File update replace in one batch)
- `docs/tech_spec/search/TECH_SPEC.md` — §9.12 (Redis and Lua: chunk fields, key names, update script contract)
- (No code dependency; key layout: file:<file_id>, file_chunks:<file_id>, chunk:<chunk_id>, chunk_kw:<chunk_id>, faiss_link:<chunk_id>, kw:<keyword>)

---

## Expected file change

- New module that exports Lua script string(s). At least one script that: (1) accepts KEYS[] and ARGV[] per Redis convention; (2) for a given file_id: deletes file:<file_id>, file_chunks:<file_id>, all chunk/chunk_kw/faiss_link for chunks of that file, and updates kw:* sets to remove references to those chunk_ids; (3) then writes new file hash, file_chunks, chunk hashes, chunk_kw, faiss_link, and keyword index entries. Script must be documented: KEYS and ARGV layout (e.g. key names and argument order). No Redis client; only script source(s) and docstring with contract.

---

## Forbidden alternatives

- Do not use redis module or perform EVAL/EVALSHA in this file. Do not implement single-key loops in application code (logic belongs in Lua). Do not leave old chunks for the same file_id after the script runs.

---

## Atomic operations

1. Create `redis_lua_scripts.py` with module docstring (Author, email) describing KEYS/ARGV contract.
2. Implement one Lua script string: replace_file (or equivalent name) that does delete-then-write for one file_id.
3. Document in docstring: key patterns, ARGV order (e.g. file_id, path, mtime, then chunk data).
4. Add unit test that runs the script against a real or fake Redis only if project supports it; otherwise test that script string is non-empty and valid Lua (e.g. parse or minimal check). Keep file under 400 lines.

---

## Expected deliverables

- Single new file `redis_lua_scripts.py` with script source(s) and clear KEYS/ARGV documentation. No client code.

---

## Mandatory validation

1. `black docs/search/engine/theory_index/redis_lua_scripts.py`
2. `flake8 docs/search/engine/theory_index/redis_lua_scripts.py`
3. `mypy docs/search/engine/theory_index/redis_lua_scripts.py`
4. `pytest` (full project test suite — must be green)
5. Step-specific: script string exists and is valid (e.g. no syntax error; optional: run against mock/mini Redis).

**Completion condition:** All of the above pass.

---

## Decision rules

| If | Then |
|----|------|
| Script needs more than one EVAL for one file | Not allowed; one script = one file replace (delete + write). |
| Key layout differs from §9.12 | Align with §9.12 (file:<id>, file_chunks:<id>, chunk:<id>, etc.). |

---

## Blackstops

- Stop and report if: existing pytest is red; Redis client or I/O is added in this file; script does not implement full replace (delete then write) for one file_id; file exceeds 400 lines.

---

## Handoff package

- **Modified file:** `docs/search/engine/theory_index/redis_lua_scripts.py` (new)
- **Confirmations:** black, flake8, mypy, pytest passed
- **Validation evidence:** pytest output (last 20 lines)
- **Blockers:** None or list
