# Technical specification: search with FAISS and MCP vectorization (canonical)

Author: Vasiliy Zdanovskiy  
email: vasilyvz@gmail.com

**Document version:** 2.0 (canonical)  
**Phase:** Population only (наполнение базы). Vector/hybrid search — out of scope.

---

## 1. Purpose and scope

**Purpose:** Extend the theory search package with a FAISS vector index; chunking via **svo_client**, vectorization via MCP (mTLS), query language via **chunk_metadata_adapter**, and summary/keywords via a lightweight LLM. Base remains `docs/search`; new components are additive. **Transport:** WebSocket (wss) is the **default** for chunker and LLM when the adapter or service supports it; if transport options exist, WebSocket must be used unless config explicitly overrides.

**In scope (current phase):**
- Filling the search database: **Redis** (file, chunks, keywords, faiss_link) and **FAISS** index.
- Pipeline: discover `*.md` → chunk (svo_client) → parse (chunks, vectors, BM25) → optional LLM enrich → write Redis (Lua, atomic per file) + FAISS.
- **Add** command: directory of `*.md`; process only files whose mtime differs from Redis; lock file (PID) in that directory.
- Config (mandatory CLI arg); strict layering: **CLI → Commands → Core**; no hardcoded URLs/certs/model names.

**Out of scope:**
- Vector search or hybrid search commands.
- Changing SQLite/FTS5 schema or replacing FTS5.
- Implementing MCP proxy or embedding/chunk services (external).
- Certificate generation (use existing `mtls_certificates/`).

---

## 2. Contracts and invariants

| Contract | Rule |
|----------|------|
| Source of truth | Theory content = `7d-NN-*.md`; `All.md` = compilation; index built from these. |
| No regression | Existing modes (search, stats, validate, sqlite_build, sqlite_search) must remain working. New behaviour is additive only. |
| Completion | A step or task is done **only when all tests pass** (full test suite green). |
| Config | Config is a **mandatory** CLI argument. Core receives an **already-resolved** config object; core does not read files or env. |
| Layering | **CLI** = argparse + config load + dispatch only. **Commands** = orchestration, call core. **Core** = business logic only; no CLI/argparse, no config loading. |

---

## 3. Components

### 3.1. Base: docs/search

- **Scope:** `docs/search/` (db/, engine/, doc/). Index: `ALL_index.yaml`; SQLite shards; FTS5; theory from `7d-NN-*.md` and/or `All.md`.
- **Forbidden:** Removing or breaking existing modes or schema.

### 3.2. FAISS manager and index

- **Requirement:** One vector per chunk; vectors from chunker response (no separate embed call for indexing). Manager: build/add, save/load; path configurable. Keys = chunk_id; dimension fixed per model (default 384).
- **Forbidden:** Hardcoded index path; search API in this phase (deferred).

### 3.3. Chunking, vectorization, query language

- **Requirement:** **svo_client** for chunker (chunks + vectors + BM25 in one response). **chunk_metadata_adapter** for query language. Server and mTLS from config (no hardcode). **Transport: WebSocket (wss) by default**; when the client/adapter offers transport options (e.g. HTTP vs WebSocket), **use WebSocket** unless config explicitly sets another scheme. Default embedding model all-MiniLM-L6-v2, dimension 384; validate per batch (reject batch if inconsistent, log importance 8).
- **Forbidden:** Separate embed call for population; hardcoded URL/cert/model; using HTTP when WebSocket is available and not overridden by config.
- **Interface contract:** See **§9.14 Chunker and embedding model interface**.

### 3.4. Summary and keywords (LLM)

- **Requirement:** Lightweight LLM (e.g. Gemini 2.0 Flash-Lite via MCP) for summary + keywords per segment/chunk; output into existing `summary` and `keywords` fields. **Transport: WebSocket (wss) by default** when the adapter/service supports it; if options exist, use WebSocket unless config overrides. Rate limits and timeouts configurable.
- **Forbidden:** Hardcoded model name or API key; using HTTP when WebSocket is available and not overridden by config.
- **Interface contract:** See **§9.15 LLM (summary/keywords) interface**.

### 3.5. Application structure

- **Requirement:** **CLI → Commands → Core** strictly separated. Config loaded only in CLI (or adapter); core receives ready config. Core under `docs/search/engine/theory_index/` (e.g. faiss_manager, vector_client, summary_llm); Commands in separate module; single entrypoint `search_theory_index.py`.
- **Forbidden:** CLI parsing or config loading inside core; business logic inside CLI.

### 3.6. Configuration and paths

- **Requirement:** Use **svo_client** ConfigLoader and config generators (§6 in full spec). Project config: URL (scheme **wss** by default for chunker and LLM), model, key, FAISS path, certs, LLM options; mandatory keys documented; missing required keys → clear error at startup.
- **Forbidden:** Hardcoded server URL, cert path, or model name in production code.

### 3.7. Timestamps, add command, lock file

- **Requirement:** Redis file entity stores **mtime**. Add command: input = directory of `*.md`; process only if file new or mtime differs from stored. Lock file in **that directory**; content = PID; if lock exists and process alive → exit non-zero; else remove stale lock and proceed. Lock file name configurable or documented.
- **Forbidden:** Global lock; hardcoded lock file name.

### 3.8. Integrity, atomicity, deletion, batch access

- **Requirement:** Referential integrity via logical links in Redis. **File update = one Lua script:** first **delete all existing data** for that `file_id` (file, file_chunks, every chunk, chunk_kw, faiss_link for that file), then **write all new data** for the file in the same script — **replace in one batch**, no leftover old content. On explicit file delete = one Lua script remove/mark all related keys; FAISS cleanup or rebuild as per §11.3. **All** Redis read/write **only in batches** (Lua scripts); no single-key loop in main path.
- **Forbidden:** Partial file write on failure; read/write outside Lua batches; updating a file without removing old chunks/keywords/faiss_link in the same script (no “append-only” update).

### 3.9. Redis and Lua

- **Requirement:** Redis = primary store; minimal entity = chunk. Keys: `file:<file_id>`, `file_chunks:<file_id>`, `chunk:<chunk_id>`, `faiss_link:<chunk_id>`, keyword index (e.g. `kw:<keyword>`, `chunk_kw:<chunk_id>`). All batch ops = Lua (EVAL/EVALSHA). Connection params from config.
- **Forbidden:** Single-key operations in a loop from application; hardcoded connection params.

### 3.10. Docker: Redis container

- **Requirement:** Redis in Docker; mounts for data, config, logs; process as user **1000:1000**. Two scripts: one to **build image**, one to **create/run container**; paths configurable or documented; create host dirs and set ownership so container can write.
- **Forbidden:** Hardcoded mount paths that break when run from another directory.

---

## 4. Validation

- **Every code change:** black, flake8, mypy, **full test suite (pytest)** must pass.
- **Step completion:** A step is done only when **all tests pass** and step-specific checks (if any) are satisfied.
- **Tests:** Unit tests for FAISS manager, MCP/chunker wrapper (mocked), summary/LLM wrapper (mocked); optional integration test with local server (skippable in CI).

---

## 5. Plan

**Steps directory:** `docs/tech_spec/search/steps/`  
**Rule:** 1 step = 1 code file = 1 step file. Each step file is handoff-ready: Executor role, Execution directive, Step scope, Dependency contract, Read first, Expected file change, Forbidden alternatives, Atomic operations, Deliverables, Mandatory validation, Decision rules, Blackstops, Handoff package. No code snippets in step file; exact file names and entry points only.

**Optimization for parallel development (LLAMA-level models):**

- **Maximal parallelism:** Steps are split and ordered so that the maximum number of steps can run in parallel (see [steps/PARALLEL_EXECUTION.md](steps/PARALLEL_EXECUTION.md)). After the minimal prerequisite (e.g. step 01 config), steps 02, 03a, 04, 05 are independent and can be assigned to different executors simultaneously.
- **Minimal context per step:** Each step file must list **at most 3 “Read first”** files (or 3 items: file or spec section) and **exactly one** primary spec section. The step must be completable without reading the full codebase or the entire TECH_SPEC. Step file + Read first must fit in a limited context window (~8K–16K tokens target).
- **Self-contained step:** No step requires cross-step reasoning or output from another step except via the **target file** of a prerequisite step (e.g. step 06 reads only the *files* produced by 02, 03b, 04, 05; the executor does not need to read other step files). Each step file contains everything the executor needs: exact target file, exact expected change, forbidden alternatives, validation commands.
- **Single deliverable:** One step = one code file. No step produces multiple modules or coordinates with another step’s implementation. Dependencies are by *artifact* (existing file on disk), not by design discussion.
- **Execution waves:** See steps/STEPS_INDEX.md and steps/PARALLEL_EXECUTION.md. Assigners may give one wave to multiple agents (one step per agent); each agent needs only its step file and the listed “Read first”.

**Step file structure (required sections):**
- Executor role
- Execution directive (execute only this step; read "Read first"; modify only target file; no alternative implementations; stop on blackstop)
- Step scope (target file, type, purpose)
- Dependency contract (prerequisites; unlocks; forbidden scope)
- Required context (single spec section; project rules reference)
- Read first (**max 3 items:** exact paths or spec §X.Y)
- Expected file change
- Forbidden alternatives
- Atomic operations
- Expected deliverables
- Mandatory validation (black, flake8, mypy, all tests pass, step-specific check)
- Decision rules (if X then Y)
- Blackstops
- Handoff package (modified file, confirmations, validation evidence, blockers)

**Steps index:** See [steps/STEPS_INDEX.md](steps/STEPS_INDEX.md). Execution waves and parallel assignment: [steps/PARALLEL_EXECUTION.md](steps/PARALLEL_EXECUTION.md).

---

## 6. Decision rules

| If | Then |
|----|------|
| Config path missing or invalid | Fail at CLI with clear error; do not start core. |
| Chunker returns inconsistent vector_dim or model within batch | Reject batch; log importance 8; do not write to Redis/FAISS (§9.14). |
| Chunker/connection error (refused, TLS, timeout) | Fail build step with clear message; optional retry from config; no silent “no vectors” (§9.14). |
| Adapter supports both HTTP and WebSocket; config does not override | Use **WebSocket** (default). |
| LLM timeout or API error after retries | Fail enrich for that item; log importance ≥6; do not write partial summary/keywords (§9.15). |
| Lock file exists and PID is alive | Exit non-zero; report PID; do not process. |
| Lock file exists and PID not alive | Remove lock file; create new lock; proceed. |
| Lua script fails for one file | No partial data for that file; other files unaffected. |
| Writing/updating a file in Redis | **One Lua script** per file: delete all existing keys for that file_id, then write all new data (replace in one batch); no separate delete and insert. |
| FAISS does not support per-chunk deletion | Use soft-delete in Redis; rebuild FAISS or filter at query time (later phase). |

---

## 7. Blackstops

- **Do not proceed** if: existing test suite is red; required config keys are missing; certs or server URL are hardcoded; core layer imports CLI or loads config; Redis/FAISS write is not atomic per file; **file update is not implemented as replace-in-one-Lua-batch** (old content must be fully removed then new written in the same script); batch access is implemented as single-key loop.
- **Do not merge** new features without green tests.

---

## 8. References

- **Base:** `docs/search/README.md`, `docs/search/doc/AUTO_INDEX_AND_EMBEDDED_MODEL.md`, `docs/search/engine/theory_index/sqlite_schema.py`, `docs/search/engine/theory_index/index_io.py`.
- **Certificates:** project root `mtls_certificates/` (client from `mtls_certificates/client/`).
- **Adapters:** svo_client (chunking), chunk_metadata_adapter (query language), mcp_proxy_adapter (client); venv packages.
- **Interfaces:** Chunker and embedding model contract §9.14; LLM (summary/keywords) contract §9.15.

---

## 9. Full requirement reference (sections 10–15)

Detailed requirements for §3 are expanded in the following sections (retained for traceability). Implementation must satisfy both the component summaries in §3 and the details below.

### 10. Timestamps, add command, lock file (detail)

- Redis **file** entity: store **mtime** of source file. Add command: input = directory; discover `*.md`; only new or changed (mtime ≠ stored) are processed. Lock file **in that directory**; content = PID. Before processing: if lock exists, check PID alive; if alive → exit non-zero; if not alive → remove lock, create new lock, proceed. On exit (normal or fatal): remove lock. Lock name configurable or documented default.

### 11. Integrity, atomicity, deletion, batch access (detail)

- **Integrity:** Redis keys: file → file_chunks → chunk; chunk → chunk_kw, faiss_link. Lua scripts enforce order on delete and insert.
- **Atomicity:** One file = one Lua script; no partial write.
- **File update (replace in one batch):** When writing or updating a file, the **same Lua script** must: (1) **remove all existing data** for that `file_id` — delete `file:<file_id>`, `file_chunks:<file_id>`, every `chunk:<chunk_id>` whose chunk belongs to this file, every `chunk_kw:<chunk_id>` and `faiss_link:<chunk_id>` for those chunks, and remove keyword set entries that referenced those chunk_ids; (2) **then** write the new `file:<file_id>`, `file_chunks:<file_id>`, all new `chunk:<chunk_id>`, `chunk_kw:<chunk_id>`, `faiss_link:<chunk_id>`, and keyword index entries. **Old content is fully removed and replaced by new in one batch**; no separate “delete” and “insert” invocations from the application — a single EVAL. If the file is new (no prior data), the delete phase is a no-op for that file_id.
- **Explicit file delete:** One Lua script removes or marks all keys for that file; FAISS cleanup after Redis (or soft-delete + rebuild).
- **Batch-only:** All Redis read/write in batches (Lua or pipeline); no single-key loop in main path.

### 12. Redis and Lua (detail)

- Chunk fields: model, body, file_id, ordinal, vector_dim. File: `file:<file_id>` (path, mtime, status), `file_chunks:<file_id>`. faiss_link: `faiss_link:<chunk_id>`. Keywords: e.g. `kw:<keyword>`, `chunk_kw:<chunk_id>`. Scripts: KEYS[] and ARGV[]; return simple result.
- **Update script contract:** The script that “writes one file” implements **replace**: first delete all keys belonging to the file_id (discover chunk_ids from `file_chunks:<file_id>` if present, then delete those chunk, chunk_kw, faiss_link keys and update kw:* sets; then delete file and file_chunks), then write all new keys for that file. One script invocation per file; no leftover old chunks or keyword references.

### 13. Docker (detail)

- Redis container; mounts: data, config, logs. User 1000:1000. Script 1: build image (docker build, tag, Dockerfile path from project root or documented dir). Script 2: create/run container (image, mounts, user, port); create host dirs if missing; chown 1000:1000 for mounts.

### 14. Chunker and embedding model interface (detail)

**Purpose:** Single source of truth for the contract between this project and the chunker service (svo_client) and the embedding model. Implementation must not deviate from this contract without spec change.

**Chunker — single call contract:**

| Aspect | Contract |
|--------|----------|
| **Call** | One invocation per input (e.g. one file or one document). No separate “chunk” and “embed” calls for population. |
| **Input** | Determined by svo_client API: e.g. document path or raw text; optional options (chunk size, overlap). Caller supplies `file_id` for mapping results to the file. |
| **Output** | One response containing: (1) **Chunks** — list of items with: stable **chunk_id** (e.g. UUID), **text/body**, boundaries/offsets; (2) **Vectors** — one embedding per chunk, same order as chunks; (3) **BM25** — tokens or term stats as returned by the service. |
| **Primary key** | `chunk_id` from the response is the unique key for Redis (`chunk:<chunk_id>`) and FAISS link (`faiss_link:<chunk_id>`). |
| **Model identity** | Each chunk (or the response as a whole) must carry **model name** (e.g. `all-MiniLM-L6-v2`) and **vector_dim** (e.g. 384). Our pipeline maps these to chunk fields `model` and `vector_dim`. |
| **Parsing** | Use svo_client result_parser (or documented parser) to obtain chunks, vectors, and BM25. Map to internal shape: `chunk_id`, `body`, `file_id`, `ordinal`, `embedding`, `vector_dim`, `model`. |

**Embedding model — consistency and validation:**

| Aspect | Contract |
|--------|----------|
| **Source of vectors** | Vectors are **only** taken from the chunker response. No separate call to an embedding service during population. |
| **Default model** | all-MiniLM-L6-v2; default dimension 384. Config may override; chunker response must declare model and dimension. |
| **Per-batch consistency** | For one batch (e.g. one file): every chunk must have the same `model` and the same `vector_dim`. **If any chunk has a different `model` or `vector_dim`:** reject the entire batch, do not write to Redis or FAISS, log at importance 8, surface error to caller. |
| **Dimension check** | `vector_dim` = length of the embedding list for that chunk; must match the declared model (e.g. 384 for all-MiniLM-L6-v2). |

**Transport:**

| Aspect | Contract |
|--------|----------|
| **Default** | **WebSocket (wss)**. The client must use WebSocket to connect to the chunker/MCP service unless config explicitly selects another transport. |
| **When options exist** | If the adapter (svo_client / MCP client) supports both HTTP and WebSocket, **use WebSocket**. Config may override via scheme (e.g. `wss://` vs `https://`) or a dedicated transport key (e.g. `transport: websocket`). |
| **URL/scheme** | Base URL from config (e.g. `wss://localhost:8009` for WebSocket). No hardcoded scheme; default scheme in config or env may be `wss`. |

**Connection and errors:**

| Event | Behaviour |
|-------|-----------|
| Server URL / certs | From config only (e.g. URL with scheme wss/https, client cert, key, CA). Defaults only in config or env, never in code. |
| Connection refused, TLS error, timeout | Build step **fails** with a clear message. Optional retry policy from config. **No** silent fallback to “no vectors” or empty chunks. |
| Malformed or incomplete response | Reject batch; log; do not write partial data. |

**Config keys (minimum for chunker/embedding):** Base URL with scheme (default **wss** for WebSocket), client cert path, client key path, CA path (if required), embedding model name, embedding dimension (optional). Optional: `transport` or `scheme` (e.g. `websocket` / `wss`) to enforce WebSocket. All from config/env; no hardcode.

### 15. LLM (summary/keywords) interface (detail)

**Purpose:** Contract for the component that produces `summary` and `keywords` for segments or chunks (e.g. Gemini 2.0 Flash-Lite or alternative).

| Aspect | Contract |
|--------|----------|
| **Transport** | **WebSocket (wss) by default.** When the LLM endpoint or MCP proxy supports WebSocket, use it. If the client offers transport options (HTTP vs WebSocket), use WebSocket unless config overrides (e.g. scheme `wss://` or `transport: websocket`). |
| **Input** | One segment or chunk **text** (string). Caller may pass segment id or chunk_id for logging only. |
| **Output** | **summary** (string, 1–3 sentences) and **keywords** (list of strings, e.g. 5–15 terms). Format: structured (e.g. JSON `{"summary": "...", "keywords": ["a", "b"]}`) or plain text that the caller parses; format must be documented or configurable. |
| **Call frequency** | One call per segment or per chunk (as defined by pipeline). Rate limiting and retries configurable (no hardcoded magic numbers). |
| **Timeout** | Per-call timeout from config. On timeout or API error: apply retry policy from config; if exhausted, fail the enrich step for that item and log (importance ≥ 6). |
| **Config** | Model name or endpoint, API base URL with scheme (default **wss** when WebSocket is used), API key (if required), timeout, retry count/backoff — all from config or env. |
| **Integration** | Output is written into the same fields used by existing index: `summary`, `keywords`. YAML and SQLite schema unchanged. |
