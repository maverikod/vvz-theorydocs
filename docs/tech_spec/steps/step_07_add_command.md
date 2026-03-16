# Step 07: Add command (mtime + lock file)

Author: Vasiliy Zdanovskiy  
email: vasilyvz@gmail.com

**Step ID:** 07  
**Target file:** `docs/search/engine/theory_index/commands/add.py`

---

## Executor role

- **Role:** Implement exactly one step: add command that takes a directory of *.md; stores mtime in Redis; processes only new or changed files; uses lock file (PID) in that directory; exits if lock exists and process alive.
- **Input:** This step file + "Read first" (max 3 items).
- **Output:** New file `commands/add.py`; confirmations; validation evidence.

---

## Execution directive

- Execute only this step. Do not change CLI entrypoint or populate implementation.
- Read first the files listed in "Read first" before creating the file.
- Create only the target file. Stop immediately on any blackstop.

---

## Step scope

- **Target file:** `docs/search/engine/theory_index/commands/add.py`
- **Type:** New file
- **Purpose:** Add command: input = directory of *.md; mtime in Redis file entity; process only if file new or mtime ≠ stored; lock file (PID) in that directory; exit non-zero if lock exists and PID alive; else remove stale lock and proceed; remove lock on exit.

---

## Dependency contract

- **Prerequisites:** Step 06 (populate command; add will call it for files that need processing).
- **Unlocks:** Step 08 (CLI will dispatch to add).
- **Forbidden scope:** Do not add CLI argument parsing in search_theory_index.py or cli.py in this step; do not change populate.py logic (only call it from add).

---

## Required context

- **Spec reference:** TECH_SPEC.md §3.7 (Timestamps, add command, lock file), §9.10 (detail).
- **Project rules:** .cursor/rules; file ≤350–400 lines; docstrings; type hints.
- **Wave:** 4 (after step 06).

---

## Read first (max 3 items)

- `docs/tech_spec/search/TECH_SPEC.md` — §3.7, §9.10 (Timestamps, add command, lock file: mtime, directory, lock PID, exit if alive)
- `docs/search/engine/theory_index/commands/populate.py` — entry point to run pipeline for a set of files
- `docs/search/engine/theory_index/redis_batch.py` or config — how to read stored mtime for file_id (if read path exists)

---

## Expected file change

- New module commands/add.py that: (1) receives resolved config and directory path; (2) acquires lock: create lock file in that directory with current PID; if lock exists, read PID and check if process alive (e.g. os.kill(pid, 0)); if alive → exit non-zero and report PID; if not alive → remove lock, create new lock; (3) discover *.md in directory; (4) for each file: get current mtime; compare with stored mtime in Redis (file:<file_id> or equivalent); if new or mtime differs, call populate (or equivalent) for that file and write mtime to Redis; else skip; (5) on normal or fatal exit remove lock. Lock file name from config or documented default.

---

## Forbidden alternatives

- Do not use a global lock; lock is per directory. Do not hardcode lock file name. Do not process files whose stored mtime equals current mtime. Do not leave lock file in place on exit.

---

## Atomic operations

1. Create `commands/add.py` with module docstring (Author, email) and imports.
2. Implement lock acquire/release (PID in file; check alive; remove stale).
3. Implement directory scan and mtime comparison; call populate (or file-level write) only for new/changed files; update stored mtime when writing.
4. Unit tests: mock Redis and populate; assert skip when mtime equal, process when mtime differs; assert exit when lock held by alive process. Keep file under 400 lines.

---

## Expected deliverables

- Single new file `commands/add.py`; docstrings; type hints; lock per directory; mtime-driven processing.

---

## Mandatory validation

1. `black docs/search/engine/theory_index/commands/add.py`
2. `flake8 docs/search/engine/theory_index/commands/add.py`
3. `mypy docs/search/engine/theory_index/commands/add.py`
4. `pytest` (full project test suite — must be green)
5. Step-specific: test lock behavior and mtime skip/process.

**Completion condition:** All of the above pass.

---

## Decision rules

| If | Then |
|----|------|
| Lock file exists and PID is alive | Exit non-zero; report PID; do not process. |
| Lock file exists and PID not alive | Remove lock file; create new lock; proceed. |
| File mtime equals stored mtime | Skip file; do not call populate for it. |
| On exit (normal or fatal) | Remove lock file. |

---

## Blackstops

- Stop and report if: existing pytest is red; global lock is used; lock file name is hardcoded; lock is not removed on exit; file exceeds 400 lines.

---

## Handoff package

- **Modified file:** `docs/search/engine/theory_index/commands/add.py` (new)
- **Confirmations:** black, flake8, mypy, pytest passed
- **Validation evidence:** pytest output (last 20 lines)
- **Blockers:** None or list
