# Step 04: Chunker client wrapper

Author: Vasiliy Zdanovskiy  
email: vasilyvz@gmail.com

**Step ID:** 04  
**Target file:** `docs/search/engine/theory_index/chunker_client.py`

---

## Executor role

- **Role:** Implement exactly one step: wrap svo_client for chunking; one call returns chunks + vectors + BM25; WebSocket (wss) by default; map response to internal shape; batch consistency check.
- **Input:** This step file + "Read first" (max 3 items). **Must** conform to TECH_SPEC §9.14.
- **Output:** New file `chunker_client.py`; confirmations; validation evidence.

---

## Execution directive

- Execute only this step. Do not add populate command or CLI.
- Read first the files listed in "Read first" before creating the file.
- Create only the target file. Stop immediately on any blackstop.

---

## Step scope

- **Target file:** `docs/search/engine/theory_index/chunker_client.py`
- **Type:** New file
- **Purpose:** Wrap svo_client; one call → chunks, vectors, BM25; WebSocket default; map to chunk_id, body, file_id, ordinal, embedding, vector_dim, model; reject batch if model/vector_dim inconsistent (log 8); connection errors → fail, no silent fallback.

---

## Dependency contract

- **Prerequisites:** Step 01 (config for URL, certs, scheme wss).
- **Unlocks:** Step 06 (populate command).
- **Forbidden scope:** Do not add separate embed call for population; do not hardcode URL/cert/model; do not use HTTP when WebSocket is available and not overridden by config.

---

## Required context

- **Spec reference:** TECH_SPEC.md §9.14 (Chunker and embedding model interface). Implementation must not deviate from this contract.
- **Project rules:** .cursor/rules; file ≤350–400 lines; docstrings; type hints.
- **Wave:** 2 (parallel with 02, 03b, 05).

---

## Read first (max 3 items)

- `docs/tech_spec/search/TECH_SPEC.md` — §9.14 (Chunker and embedding model interface: call contract, transport, connection and errors, config keys)
- `docs/search/engine/theory_index/config.py` — config shape for URL (wss), certs, model
- svo_client package (venv): result_parser / API for chunk response — use documented entry point only

---

## Expected file change

- New module that: (1) uses config for base URL (wss by default), client cert, key, CA; (2) calls chunker (svo_client) once per input; (3) parses response to chunks, vectors, BM25; (4) maps to internal shape: chunk_id, body, file_id, ordinal, embedding, vector_dim, model; (5) validates per batch: same model and vector_dim for all chunks; if not, reject entire batch, log importance 8, do not write to Redis/FAISS; (6) on connection refused / TLS / timeout: fail with clear message, optional retry from config, no silent "no vectors". Use WebSocket when adapter supports it unless config overrides.

---

## Forbidden alternatives

- Do not add a separate embedding call for population. Do not hardcode server URL, cert path, or model name. Do not use HTTP when WebSocket is available and config does not override. Do not accept inconsistent vector_dim or model within a batch without rejecting and logging 8.

---

## Atomic operations

1. Create `chunker_client.py` with module docstring (Author, email) and imports (svo_client, config).
2. Implement function or class that takes config and input (e.g. file path or text, file_id); calls svo_client once; parses via result_parser; maps to list of dicts or typed structs: chunk_id, body, file_id, ordinal, embedding, vector_dim, model.
3. Add batch consistency check: same model and vector_dim; on mismatch reject and log importance 8.
4. Handle connection/TLS/timeout: fail with clear message; no silent fallback. Add unit tests with mocked svo_client; assert reject on inconsistent dimension. Keep file under 400 lines.

---

## Expected deliverables

- Single new file `chunker_client.py` conforming to §9.14; docstrings; type hints; no hardcode.

---

## Mandatory validation

1. `black docs/search/engine/theory_index/chunker_client.py`
2. `flake8 docs/search/engine/theory_index/chunker_client.py`
3. `mypy docs/search/engine/theory_index/chunker_client.py`
4. `pytest` (full project test suite — must be green)
5. Step-specific: unit test with mock; assert batch rejected when vector_dim or model differs; assert no silent fallback on error.

**Completion condition:** All of the above pass.

---

## Decision rules

| If | Then |
|----|------|
| Chunker returns inconsistent vector_dim or model in batch | Reject batch; log importance 8; surface error to caller; do not write. |
| Connection refused, TLS error, timeout | Fail with clear message; optional retry from config; no silent "no vectors". |
| Adapter supports WebSocket and config does not override | Use WebSocket (wss). |

---

## Blackstops

- Stop and report if: existing pytest is red; URL/cert/model are hardcoded; separate embed call is added; inconsistent batch is accepted; silent fallback on connection error; file exceeds 400 lines.

---

## Handoff package

- **Modified file:** `docs/search/engine/theory_index/chunker_client.py` (new)
- **Confirmations:** black, flake8, mypy, pytest passed
- **Validation evidence:** pytest output (last 20 lines)
- **Blockers:** None or list
