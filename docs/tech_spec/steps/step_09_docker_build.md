# Step 09: Docker image build script for Redis

Author: Vasiliy Zdanovskiy  
email: vasilyvz@gmail.com

**Step ID:** 09  
**Target file:** `docs/tech_spec/search/docker/build_redis_image.sh`

---

## Executor role

- **Role:** Implement exactly one step: add a script that builds the Docker image for Redis; tag; use Dockerfile path from project root or documented directory.
- **Input:** This step file + "Read first" (max 3 items).
- **Output:** New script `build_redis_image.sh` (and optional Dockerfile if not existing); confirmations; validation evidence.

---

## Execution directive

- Execute only this step. Do not add run-container script or application code.
- Read first the files listed in "Read first" before creating the file.
- Create the script (and optionally Dockerfile). Stop immediately on any blackstop.

---

## Step scope

- **Target file:** `docs/tech_spec/search/docker/build_redis_image.sh`
- **Type:** New file
- **Purpose:** Build Docker image for Redis; tag with defined name/version; Dockerfile path from project root or documented dir; no hardcoded paths that break when run from another directory.

---

## Dependency contract

- **Prerequisites:** None
- **Unlocks:** Step 10 (run container script uses this image).
- **Forbidden scope:** Do not add run-container logic; do not hardcode paths that fail when script is run from a different cwd.

---

## Required context

- **Spec reference:** TECH_SPEC.md §3.10 (Docker), §9.13 (Docker detail: script 1 = build image).
- **Project rules:** .cursor/rules; documentation in English.
- **Wave:** 1 (parallel with 01, 03a).

---

## Read first (max 3 items)

- `docs/tech_spec/search/TECH_SPEC.md` — §3.10, §9.13 (build script, tag, Dockerfile path)
- `docs/tech_spec/search/README.md` or project root — layout and where to place Dockerfile (e.g. docs/tech_spec/search/docker/)

---

## Expected file change

- New executable script build_redis_image.sh that: (1) uses docker build (or podman build) with a Dockerfile path resolved from script location or project root (documented); (2) tags the image with a defined name and optionally version; (3) accepts or documents any build args; (4) does not rely on hardcoded absolute paths so it works when run from project root or documented directory. Optionally create a minimal Dockerfile for Redis if none exists.

---

## Forbidden alternatives

- Do not hardcode paths that break when run from another directory. Do not add container run logic (that is step 10).

---

## Atomic operations

1. Create directory docs/tech_spec/search/docker/ if missing.
2. Create build_redis_image.sh: resolve Dockerfile path (e.g. same dir or project root via script dir); run docker build; tag image.
3. Make script executable (chmod +x); document in script or README how to run (e.g. from project root).
4. Optionally add Dockerfile for Redis (official Redis image or custom with USER 1000:1000 if required by §13).

---

## Expected deliverables

- Script build_redis_image.sh; optional Dockerfile; short doc or comments on usage.

---

## Mandatory validation

1. Shell check or equivalent if available; otherwise manual run from project root (or documented dir) — script must complete without path errors.
2. Document run instructions (e.g. “Run from project root: ./docs/tech_spec/search/docker/build_redis_image.sh”).
3. No pytest for shell script; full project pytest still green (no regression in code).

**Completion condition:** Script runs and produces image; path logic documented; no regression in codebase tests.

---

## Decision rules

| If | Then |
|----|------|
| Dockerfile not in repo | Create minimal Dockerfile (Redis base; USER 1000:1000 per §13 if required). |
| Script run from other dir | Use script’s directory or PROJECT_ROOT env to resolve Dockerfile; document. |

---

## Blackstops

- Stop and report if: script fails when run from project root due to path; hardcoded absolute path to Dockerfile; run-container logic is added here.

---

## Handoff package

- **Modified file:** `docs/tech_spec/search/docker/build_redis_image.sh` (new); optional Dockerfile
- **Confirmations:** Script executed successfully; doc updated
- **Validation evidence:** Script output or doc note
- **Blockers:** None or list
