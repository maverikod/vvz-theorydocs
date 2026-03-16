# vvz-theorydocs

**Author:** Vasiliy Zdanovskiy  
**email:** vasilyvz@gmail.com

Theory search package: SQLite/FTS5 base, FAISS vector index, MCP-based chunking and vectorization.

## Status

- **Current:** Technical specification and project layout; package is installable, implementation in progress.
- **Spec:** [docs/tech_spec/search/](docs/tech_spec/search/) — FAISS + MCP vectorization (population phase).

## Install

```bash
pip install vvz-theorydocs
```

From source:

```bash
git clone https://github.com/vasilyvz/vvz-theorydocs.git
cd vvz-theorydocs
pip install -e .
```

## Usage

After implementation, the package will provide:

- **Base:** SQLite/FTS5 search over theory docs (`7d-NN-*.md`, `All.md`).
- **Add (current phase):** Populate Redis + FAISS from markdown via svo_client chunking and MCP vectorization; config-driven, no hardcoded URLs/certs.

CLI entry point and API will be documented here and in [docs/tech_spec/search/](docs/tech_spec/search/) when available.

## Development

```bash
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
black theorydocs tests
flake8 theorydocs tests
mypy theorydocs
pytest
```

## Links

- **PyPI:** [vvz-theorydocs](https://pypi.org/project/vvz-theorydocs/)
- **Repository:** [github.com/vasilyvz/vvz-theorydocs](https://github.com/vasilyvz/vvz-theorydocs)
- **License:** MIT — see [LICENSE](LICENSE).
