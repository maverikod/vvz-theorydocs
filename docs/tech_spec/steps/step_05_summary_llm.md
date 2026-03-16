# Step 05: Summary and keywords LLM

Author: Vasiliy Zdanovskiy  
email: vasilyvz@gmail.com

**Step ID:** 05  
**Target file:** `docs/search/engine/theory_index/summary_llm.py`

---

## Executor role

- **Role:** Implement exactly one step: call LLM for summary + keywords per segment/chunk; WebSocket (wss) by default when supported; output to summary and keywords fields; config for model/endpoint/timeout/retry.
- **Input:** This step file + "Read first" (max 3 items). **Must** conform to TECH_SPEC §9.15.
- **Output:** New file `summary_llm.py`; confirmations; validation evidence.

---

## Execution directive

- Execute only this step. Do not add populate command or CLI.
- Read first the files listed in "Read first" before creating the file.
- Create only the target file. Stop immediately on any blackstop.

---

## Step scope

- **Target file:** `docs/search/engine/theory_index/summary_llm.py`
- **Type:** New file
- **Purpose:** One call per segment/chunk: input text → summary (string) + keywords (list of strings); WebSocket default when supported; config for model, endpoint, timeout, retry; on timeout/error after retries → fail item, log ≥6.

---

## Dependency contract

- **Prerequisites:** Step 01 (config for LLM model, endpoint, timeout, retry).
- **Unlocks:** Step 06 (populate command).
- **Forbidden scope:** Do not hardcode model name or API key; do not use HTTP when WebSocket is available and config does not override.

---

## Required context

- **Spec reference:** TECH_SPEC.md §9.15 (LLM summary/keywords interface). Implementation must not deviate from this contract.
- **Project rules:** .cursor/rules; file ≤350–400 lines; docstrings; type hints.
- **Wave:** 2 (parallel with 02, 03b, 04).

---

## Read first (max 3 items)

- `docs/tech_spec/search/TECH_SPEC.md` — §9.15 (LLM interface: transport, input/output, timeout, retry, config)
- `docs/search/engine/theory_index/config.py` — config shape for LLM model, endpoint (wss), API key, timeout, retry
- (Optional) MCP proxy or LLM client docs — if calling Gemini 2.0 Flash-Lite or similar via proxy

---

## Expected file change

- New module that: (1) takes config (model, API base URL with scheme wss when WebSocket used, API key if required, timeout, retry count/backoff); (2) exposes function that accepts one segment/chunk text and returns summary (string) and keywords (list of strings); (3) one call per segment/chunk; (4) on timeout or API error: apply retry policy from config; if exhausted, fail that item and log importance ≥6; (5) output format: structured (e.g. JSON) or parsed; documented or configurable. Use WebSocket when endpoint supports it unless config overrides.

---

## Forbidden alternatives

- Do not hardcode model name or API key. Do not use HTTP when WebSocket is available and not overridden. Do not write partial summary/keywords on error after retries exhausted.

---

## Atomic operations

1. Create `summary_llm.py` with module docstring (Author, email) and imports.
2. Implement function or class: input text → call LLM (via MCP proxy or configured client); parse response to summary and keywords; return (summary, keywords).
3. Apply timeout and retry from config; on exhaustion log ≥6 and raise or return error.
4. Unit tests: mock LLM response; assert summary and keywords parsed; assert retry/timeout behavior. Keep file under 400 lines.

---

## Expected deliverables

- Single new file `summary_llm.py` conforming to §9.15; docstrings; type hints; no hardcode.

---

## Mandatory validation

1. `black docs/search/engine/theory_index/summary_llm.py`
2. `flake8 docs/search/engine/theory_index/summary_llm.py`
3. `mypy docs/search/engine/theory_index/summary_llm.py`
4. `pytest` (full project test suite — must be green)
5. Step-specific: unit test with mocked LLM; assert output shape (summary, keywords); assert fail and log on timeout after retries.

**Completion condition:** All of the above pass.

---

## Decision rules

| If | Then |
|----|------|
| Timeout or API error after retries exhausted | Fail enrich for that item; log importance ≥6; do not write partial data. |
| Config has no LLM keys | Document required keys; raise clear error at use time if missing. |

---

## Blackstops

- Stop and report if: existing pytest is red; model name or API key is hardcoded; partial summary/keywords written after error; file exceeds 400 lines.

---

## Handoff package

- **Modified file:** `docs/search/engine/theory_index/summary_llm.py` (new)
- **Confirmations:** black, flake8, mypy, pytest passed
- **Validation evidence:** pytest output (last 20 lines)
- **Blockers:** None or list
