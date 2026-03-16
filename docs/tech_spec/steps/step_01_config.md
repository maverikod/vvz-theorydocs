# Step 01: Project config module

Author: Vasiliy Zdanovskiy  
email: vasilyvz@gmail.com

**Step ID:** 01  
**Target file:** `docs/search/engine/theory_index/config.py`

---

## Executor role

- **Role:** Implement exactly one step: add a new config module under `theory_index`. No changes to CLI or other modules in this step.
- **Input:** This step file + "Read first" (max 3 items). No other step files or full spec.
- **Output:** New file `config.py`; confirmations; validation evidence.

---

## Execution directive

- Execute only this step. Do not implement CLI config loading or populate/add commands.
- Read first the files listed in "Read first" before creating the file.
- Create only the target file; do not modify `search_theory_index.py` or `cli.py` in this step.
- Stop immediately on any blackstop.

---

## Step scope

- **Target file:** `docs/search/engine/theory_index/config.py`
- **Type:** New file
- **Purpose:** Load and resolve project config (FAISS path, URL, model, key, certs, LLM options); no hardcoded values; optional use of svo_client ConfigLoader for chunker/MCP-related keys.

---

## Dependency contract

- **Prerequisites:** None
- **Unlocks:** Steps 02, 03b, 04, 05 (03a and 09 have no deps; 03b needs 01 and 03a)
- **Forbidden scope:** Do not add CLI argument parsing or entrypoint logic. Do not modify existing theory_index modules except by adding this new file.

---

## Required context

- **Spec reference (one primary section):** TECH_SPEC.md §3.6 (Configuration).
- **Project rules:** .cursor/rules; file ≤350–400 lines; docstrings (file, class, function); type hints.
- **Wave:** 1 (can run in parallel with 03a, 09).

---

## Read first (max 3 items)

- `docs/tech_spec/search/TECH_SPEC.md` — §2 (Contracts), §3.6 (Configuration)
- `docs/search/engine/theory_index/index_io.py` — `load_theory_lines`, `load_index` (paths usage)
- (Optional) Project root `pyproject.toml` or existing config example — for config file format only

---

## Expected file change

- New module `config` with: (1) a typed structure or dataclass/dict contract for URL, model, key, FAISS index path, cert paths, LLM model/endpoint/timeouts; (2) a function to load config from file path (YAML or JSON) and optionally merge with env (e.g. SVO_* from svo_client); (3) no hardcoded default URLs or cert paths—defaults only via documented default config or env. All keys required by TECH_SPEC §3.6 must be representable; missing required keys must be detectable (validation function or documented contract).

---

## Forbidden alternatives

- Do not load config inside any other theory_index module in this step.
- Do not add CLI subcommands or argparse in this step.
- Do not hardcode `https://localhost:8009` or `mtls_certificates/` in this file; use config keys or env only.

---

## Atomic operations

1. Create `docs/search/engine/theory_index/config.py` with module docstring (Author, email) and imports.
2. Define config structure (dataclass or TypedDict) with fields: url, model, key, faiss_index_path, cert paths, LLM options, lock_file_name (or equivalent).
3. Add `load_config(path: str) -> ...` (or equivalent) that reads file and returns resolved config; document env override if used.
4. Add validation (e.g. required keys) and raise clear error if required key missing.
5. Keep file under 400 lines.

---

## Expected deliverables

- Single new file: `docs/search/engine/theory_index/config.py` with docstrings, type hints, no hardcode, no TODO/pass (except in exception handlers if any).

---

## Mandatory validation

1. `black docs/search/engine/theory_index/config.py`
2. `flake8 docs/search/engine/theory_index/config.py`
3. `mypy docs/search/engine/theory_index/config.py` (or project mypy including this file)
4. `pytest` (full project test suite — must be green; add unit test(s) for config load/validation if none exist)
5. Step-specific: at least one test that loads a minimal config and asserts required keys are present or missing key raises.

**Completion condition:** All of the above pass.

---

## Decision rules

| If | Then |
|----|------|
| Config file path does not exist | Raise clear error (e.g. FileNotFoundError or custom with message). |
| Required key missing in config file and not in env | Raise with message naming the key. |
| svo_client not installed | Document in docstring; optional import or skip svo_client merge if not available; do not fail at import time if svo_client is optional. |

---

## Blackstops

- Stop and report if: existing pytest suite is red before edits; file exceeds 400 lines; hardcoded URL or cert path is introduced; config is loaded from inside another module in this step.

---

## Handoff package

- **Modified file:** `docs/search/engine/theory_index/config.py` (new)
- **Confirmations:** black, flake8, mypy, pytest passed
- **Validation evidence:** pytest output (last 20 lines)
- **Blockers:** None or list
