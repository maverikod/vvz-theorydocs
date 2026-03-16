# Tech spec: search (FAISS + MCP vectorization) — canonical

Author: Vasiliy Zdanovskiy  
email: vasilyvz@gmail.com

Technical specification for extending the theory search package with FAISS and MCP-based vectorization. **Current phase: population only** (наполнение базы); vector/hybrid search is out of scope.

## Files

| File | Purpose |
|------|--------|
| [TECH_SPEC.md](TECH_SPEC.md) | **Canonical spec:** Purpose & scope (§1), Contracts & invariants (§2), Components (§3), Validation (§4), Plan (§5), Decision rules (§6), Blackstops (§7), References (§8), Full requirement reference (§9–13). |
| [steps/STEPS_INDEX.md](steps/STEPS_INDEX.md) | Steps index: step ID, target file, dependencies, waves, one-line expected change, validation. 1 step = 1 code file = 1 step file. |
| [steps/PARALLEL_EXECUTION.md](steps/PARALLEL_EXECUTION.md) | **Parallel execution:** waves, assignment for LLAMA-level models, context budget, handoff rules. |
| [steps/STEP_FILE_TEMPLATE.md](steps/STEP_FILE_TEMPLATE.md) | Required sections for each step file; **Read first max 3 items**; one primary spec section; optimized for limited-context executors. |
| `steps/step_NN_*.md` | One step file per step; handoff-ready for one executor (no full codebase needed). |

## Plan rule

- **Completion:** A step is done only when **all tests pass** (full test suite green).
- **Parallel development (LLAMA-level):** Plan is optimized for parallel execution. Wave 1: steps 01, 03a, 09 (3 in parallel). Wave 2: steps 02, 03b, 04, 05 (4 in parallel). Each step file is self-contained; "Read first" ≤ 3 items; one primary spec section. See steps/PARALLEL_EXECUTION.md.

## Base

- **docs/search** — existing theory search (SQLite, FTS5, ALL_index.yaml, All.md). No regression allowed.

## References

- Certificates: project root `mtls_certificates/` (client certs for MCP proxy).
- Chunking: svo_client (venv); query language: chunk_metadata_adapter (venv); vectorization: mcp_proxy_adapter (venv).
