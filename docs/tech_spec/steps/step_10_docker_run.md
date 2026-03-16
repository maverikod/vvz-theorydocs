# Step 10: Docker container run script for Redis

Author: Vasiliy Zdanovskiy  
email: vasilyvz@gmail.com

**Step ID:** 10  
**Target file:** `docs/tech_spec/search/docker/run_redis_container.sh`

---

## Executor role

- **Role:** Implement exactly one step: add a script that creates and runs the Redis container with mounts (data, config, logs), user 1000:1000; create host dirs if missing; chown for mounts.
- **Input:** This step file + "Read first" (max 3 items).
- **Output:** New script `run_redis_container.sh`; confirmations; validation evidence.

---

## Execution directive

- Execute only this step. Do not change build script or application code.
- Read first the files listed in "Read first" before creating the file.
- Create only the run script. Stop immediately on any blackstop.

---

## Step scope

- **Target file:** `docs/tech_spec/search/docker/run_redis_container.sh`
- **Type:** New file
- **Purpose:** Create and start container from image built in step 09; mounts for data, config, logs; user 1000:1000; create host dirs and set ownership so container can write.

---

## Dependency contract

- **Prerequisites:** Step 09 (image must exist; build_redis_image.sh run first).
- **Unlocks:** None
- **Forbidden scope:** Do not hardcode mount paths that break when run from another directory; do not skip user 1000:1000.

---

## Required context

- **Spec reference:** TECH_SPEC.md §3.10 (Docker), §9.13 (Script 2: run container, mounts, user 1000:1000).
- **Project rules:** .cursor/rules; documentation in English.
- **Wave:** 6 (after step 09); can run in parallel with 02–08 if image exists.

---

## Read first (max 3 items)

- `docs/tech_spec/search/TECH_SPEC.md` — §3.10, §9.13 (run container: mounts, user 1000:1000, create dirs, chown)
- `docs/tech_spec/search/docker/build_redis_image.sh` — image name/tag used
- (Optional) docs/tech_spec/search/docker/ — existing layout

---

## Expected file change

- New executable script run_redis_container.sh that: (1) uses the image from step 09; (2) sets mounts for data, config, logs (paths configurable or documented; e.g. host ./data, ./config, ./logs); (3) runs container with --user 1000:1000; (4) creates host directories if missing (mkdir -p); (5) sets ownership 1000:1000 for those dirs so container can write; (6) container name and port mapping (e.g. 6379) documented or configurable. Paths may come from env or script-relative so they work when run from project root or documented dir.

---

## Forbidden alternatives

- Do not hardcode mount paths that break when run from another directory. Do not omit user 1000:1000. Do not skip creating host dirs or chown (container must be able to write to mounts).

---

## Atomic operations

1. Create run_redis_container.sh in docs/tech_spec/search/docker/.
2. Implement: mkdir -p for data, config, logs; chown 1000:1000 (or document that operator must do it); docker run with --user 1000:1000, -v for each mount, port mapping, image tag from build script.
3. Make script executable; document how to run (e.g. from project root).
4. Optionally read paths from env (e.g. REDIS_DATA_DIR) so operators can override.

---

## Expected deliverables

- Script run_redis_container.sh; short doc or comments; container starts with correct user and mounts.

---

## Mandatory validation

1. Shell check or equivalent if available; script runs without path errors when invoked from documented directory.
2. Document run instructions; note that image must be built first (step 09).
3. Full project pytest still green (no code regression).

**Completion condition:** Script runs; container starts with user 1000:1000 and mounts; host dirs created and chown documented or applied.

---

## Decision rules

| If | Then |
|----|------|
| Host dirs do not exist | Create with mkdir -p; then chown 1000:1000 (or document). |
| Image not built | Document “Run build_redis_image.sh first”; script may exit with clear message if image missing. |

---

## Blackstops

- Stop and report if: script fails due to path when run from project root; user 1000:1000 is omitted; mount paths are hardcoded in a way that breaks from other cwd.

---

## Handoff package

- **Modified file:** `docs/tech_spec/search/docker/run_redis_container.sh` (new)
- **Confirmations:** Script executed successfully; container runs with correct user and mounts
- **Validation evidence:** Script output or doc note
- **Blockers:** None or list
