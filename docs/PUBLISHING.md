# Publishing: PyPI and GitHub

Author: Vasiliy Zdanovskiy  
email: vasilyvz@gmail.com

## Structure for PyPI and GitHub

| Item | Purpose |
|------|---------|
| `pyproject.toml` | Build system and project metadata; PyPI name `vvz-theorydocs`, package `theorydocs`. |
| `theorydocs/` | Installable Python package (import `theorydocs`). |
| `MANIFEST.in` | Files included in sdist (README, LICENSE, docs). |
| `.gitignore` | Ignore build artifacts, .venv, IDE, secrets. |
| `README.md` | Project description for GitHub and PyPI long description. |
| `LICENSE` | MIT. |
| `.github/workflows/ci.yml` | CI on push/PR: black, flake8, mypy, pytest. |
| `.github/workflows/publish-pypi.yml` | Publish to PyPI on Release, tag `v*`, or workflow_dispatch. |

## PyPI

- **Project name:** `vvz-theorydocs`  
- **Install:** `pip install vvz-theorydocs`  
- **Import:** `import theorydocs`

**Publish (after adding secret):**

1. In GitHub repo: Settings → Secrets and variables → Actions → New repository secret: `PYPI_API_TOKEN` (token from [pypi.org/manage/account/token/](https://pypi.org/manage/account/token/)).
2. Either:
   - Create a **Release** (Actions → Publish to PyPI runs), or  
   - Push a tag: `git tag v0.1.0 && git push --tags`, or  
   - Run workflow manually: Actions → Publish to PyPI → Run workflow.

**Local build:**

```bash
pip install build
python -m build
# Artifacts in dist/
```

## GitHub

- Push to `main`/`master`: CI runs (lint + tests).
- Replace `vasilyvz/vvz-theorydocs` in README and pyproject.toml `project.urls` with your repo if different.
