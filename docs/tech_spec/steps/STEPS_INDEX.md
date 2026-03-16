# Steps index: search population (FAISS + MCP)

Author: Vasiliy Zdanovskiy  
email: vasilyvz@gmail.com

**Rule:** 1 step = 1 code file = 1 step file. Completion = all tests pass.  
**Optimization:** Plan is tuned for **parallel development by LLAMA-level models**: minimal context per step, maximal parallelism, self-contained step files. See [PARALLEL_EXECUTION.md](PARALLEL_EXECUTION.md).

---

## Steps table

| Step ID | Target file | Depends on | One-line expected change | Validation |
|---------|-------------|------------|--------------------------|------------|
| 01 | `docs/search/engine/theory_index/config.py` | — | New module: load/resolve project config (FAISS path, URL, model, key, certs, LLM); no hardcode; use svo_client ConfigLoader where applicable. | black, flake8, mypy, pytest |
| 02 | `docs/search/engine/theory_index/faiss_manager.py` | 01 | New module: FAISS index lifecycle (add vectors by chunk_id, save/load); path from config; dimension validation per batch. | black, flake8, mypy, pytest |
| 03a | `docs/search/engine/theory_index/redis_lua_scripts.py` | — | New module: **Lua script sources only** (strings). One script: replace file — delete all keys for file_id (file, file_chunks, chunk, chunk_kw, faiss_link, kw), then write new file + chunks + keywords + faiss_link. Keys/ARGV contract documented in module. No Redis client code. | black, flake8, mypy, pytest |
| 03b | `docs/search/engine/theory_index/redis_batch.py` | 01, 03a | New module: Redis client; load scripts from 03a; EVAL/EVALSHA for batch write (one script per file = replace) and batch read. Config for connection. | black, flake8, mypy, pytest |
| 04 | `docs/search/engine/theory_index/chunker_client.py` | 01 | New module: wrap svo_client; **contract §9.14**: WebSocket (wss) by default; one call → chunks+vectors+BM25; map to chunk_id, body, file_id, ordinal, embedding, vector_dim, model; batch consistency (reject + log 8 if model/vector_dim differ); connection errors → fail, no silent fallback. | black, flake8, mypy, pytest |
| 05 | `docs/search/engine/theory_index/summary_llm.py` | 01 | New module: **contract §9.15**: WebSocket (wss) by default when supported; input text → summary + keywords; one call per segment/chunk; config for model/endpoint/timeout/retry; output to summary, keywords; timeout/error after retries → fail item, log ≥6. | black, flake8, mypy, pytest |
| 06 | `docs/search/engine/theory_index/commands/populate.py` | 02, 03b, 04, 05 | New module: populate command — discover *.md, chunk, enrich, write Redis (Lua) + FAISS; receive resolved config from CLI; no argparse. | black, flake8, mypy, pytest |
| 07 | `docs/search/engine/theory_index/commands/add.py` | 06 | New module: add command — directory of *.md; mtime in Redis; process only new/changed; lock file (PID) in directory; exit if lock and PID alive. | black, flake8, mypy, pytest |
| 08 | `docs/search/engine/search_theory_index.py` | 07 | Add: mandatory --config; load config; dispatch to add/populate; no business logic. | black, flake8, mypy, pytest |
| 09 | `docs/tech_spec/search/docker/build_redis_image.sh` | — | New script: build Docker image for Redis; tag; Dockerfile path from project root or documented dir. | shell check, doc |
| 10 | `docs/tech_spec/search/docker/run_redis_container.sh` | 09 | New script: run container with mounts (data, config, logs), user 1000:1000; create host dirs, chown. | shell check, doc |

---

## Execution waves (parallel assignment)

| Wave | Steps | Prerequisite | Parallelism |
|------|-------|-------------|-------------|
| **1** | 01, 03a, 09 | None | **3 agents**: config, Lua scripts, Docker image |
| **2** | 02, 03b, 04, 05 | 01 (for 02, 03b, 04, 05); 03a (for 03b) | **4 agents**: FAISS, Redis client, chunker, LLM |
| **3** | 06 | 02, 03b, 04, 05 | 1 agent: populate command |
| **4** | 07 | 06 | 1 agent: add command |
| **5** | 08 | 07 | 1 agent: CLI entrypoint |
| **6** | 10 | 09 | 1 agent: run container |

**For LLAMA-level executors:** Assign one step per agent. Each agent receives only: (1) the step file `step_NN_*.md`, (2) the files listed in that step’s “Read first” (max 3). No need to read other step files or the full TECH_SPEC.

---

## Context budget per step

- **Read first:** At most **3 items** (file path or spec section, e.g. `TECH_SPEC.md §9.14`).
- **Required context:** Exactly **one** primary spec section in the step file (e.g. §9.11 and §9.12 for 03a; §9.14 for 04).
- Step file + Read first should fit in **~8K–16K tokens** so a single executor can hold full context.

---

## Dependency graph (summary)

```
01 ─┬─► 02 ─┐
    ├─► 03b ◄── 03a   ├─► 06 ─► 07 ─► 08
    ├─► 04 ─┘
    └─► 05 ─┘

09 ─► 10   (Docker, independent of 01–08)
```

---

## Interface steps

For step **04** (chunker) and **05** (LLM), the step file **must** list TECH_SPEC.md **§9.14** and **§9.15** respectively in “Read first”; implementation must conform to those contracts.

---

## Step files

| Step ID | Step file |
|---------|-----------|
| 01 | [step_01_config.md](step_01_config.md) |
| 02 | [step_02_faiss_manager.md](step_02_faiss_manager.md) |
| 03a | [step_03a_redis_lua_scripts.md](step_03a_redis_lua_scripts.md) |
| 03b | [step_03b_redis_batch.md](step_03b_redis_batch.md) |
| 04 | [step_04_chunker_client.md](step_04_chunker_client.md) |
| 05 | [step_05_summary_llm.md](step_05_summary_llm.md) |
| 06 | [step_06_populate.md](step_06_populate.md) |
| 07 | [step_07_add_command.md](step_07_add_command.md) |
| 08 | [step_08_cli_entrypoint.md](step_08_cli_entrypoint.md) |
| 09 | [step_09_docker_build.md](step_09_docker_build.md) |
| 10 | [step_10_docker_run.md](step_10_docker_run.md) |

Content must follow [STEP_FILE_TEMPLATE.md](STEP_FILE_TEMPLATE.md).
