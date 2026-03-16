# Step 08: CLI entrypoint (config + dispatch)

Author: Vasiliy Zdanovskiy  
email: vasilyvz@gmail.com

**Step ID:** 08  
**Target file:** `docs/search/engine/search_theory_index.py`

---

## Executor role

- **Role:** Implement exactly one step: add mandatory --config; load and resolve config; dispatch to add/populate commands; no business logic in this file.
- **Input:** This step file + "Read first" (max 3 items).
- **Output:** Modified `search_theory_index.py`; confirmations; validation evidence.

---

## Execution directive

- Execute only this step. Do not change commands or core modules.
- Read first the files listed in "Read first" before editing.
- Modify only the target file. Stop immediately on any blackstop.

---

## Step scope

- **Target file:** `docs/search/engine/search_theory_index.py`
- **Type:** Existing file
- **Purpose:** Add mandatory --config argument; load config (using config module from step 01); dispatch to add or populate command; no business logic; preserve existing modes (search, stats, validate, sqlite_build, sqlite_search).

---

## Dependency contract

- **Prerequisites:** Step 07 (add command exists and is callable).
- **Unlocks:** None (final step in main chain).
- **Forbidden scope:** Do not add business logic; do not load config inside core or commands; do not remove or break existing modes.

---

## Required context

- **Spec reference:** TECH_SPEC.md §3.5 (CLI = argparse + config load + dispatch only), §2 (Config mandatory).
- **Project rules:** .cursor/rules; file ≤350–400 lines; docstrings.
- **Wave:** 5 (after step 07).

---

## Read first (max 3 items)

- `docs/tech_spec/search/TECH_SPEC.md` — §2 (Contracts: config mandatory), §3.5 (CLI layer)
- `docs/search/engine/search_theory_index.py` — current main(), argument parsing, mode dispatch
- `docs/search/engine/theory_index/config.py` — load_config or equivalent

---

## Expected file change

- In search_theory_index.py: (1) add mandatory --config (or required positional) for modes that need config (add, populate); (2) load config via theory_index.config.load_config (or equivalent) when invoking add/populate; (3) pass resolved config to add or populate command; (4) keep existing modes unchanged (search, stats, validate, sqlite_build, sqlite_search); (5) no business logic; only argparse, config load, and dispatch. Missing config path → clear error, do not start core.

---

## Forbidden alternatives

- Do not add chunking, Redis, or FAISS logic in this file. Do not load config inside theory_index core or commands (only here at entrypoint). Do not make --config optional for add/populate. Do not break existing modes.

---

## Atomic operations

1. Open search_theory_index.py; locate argument parsing and mode dispatch.
2. Add --config (required for add/populate); add logic to load config and pass to commands.add / commands.populate (or equivalent entry points).
3. Ensure existing modes still work and do not require --config unless they are add/populate.
4. Run full test suite; ensure no regression. Keep file under 400 lines (if file grows, consider extracting CLI to theory_index/cli.py in a later step; not in this step).

---

## Expected deliverables

- Modified search_theory_index.py: mandatory --config for add/populate; config load and dispatch only; existing modes preserved.

---

## Mandatory validation

1. `black docs/search/engine/search_theory_index.py`
2. `flake8 docs/search/engine/search_theory_index.py`
3. `mypy docs/search/engine/search_theory_index.py`
4. `pytest` (full project test suite — must be green)
5. Step-specific: run with --config missing for add/populate → must fail with clear error; run existing mode (e.g. search or stats) → must work.

**Completion condition:** All of the above pass.

---

## Decision rules

| If | Then |
|----|------|
| --config missing for add or populate | Fail with clear error; do not start core. |
| Config path invalid or file missing | Fail with clear error at startup. |

---

## Blackstops

- Stop and report if: existing pytest is red; existing modes (search, stats, validate, sqlite_*) are broken; business logic is added to this file; --config is optional for add/populate; file exceeds 400 lines.

---

## Handoff package

- **Modified file:** `docs/search/engine/search_theory_index.py`
- **Confirmations:** black, flake8, mypy, pytest passed
- **Validation evidence:** pytest output; CLI test with/without --config
- **Blockers:** None or list
