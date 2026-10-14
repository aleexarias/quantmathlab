# Instructions for Claude Code

The project's layout, conventions and workflows are in CONTRIBUTING.md,
imported here. Follow them in every change:

@CONTRIBUTING.md

## Working in this repository

- **The user writes the methods.** The library is built paper by paper by
  the user. Do not implement a method, estimator or notebook experiment
  unless asked to.
- **Environment.** Run tools from the `quantmathlab` conda environment; the
  base environment has no Sphinx.
- **Before saying work is done**, run these and fix every error and
  warning:

  ```bash
  ruff check src tests
  ruff format --check src tests
  mypy --strict src
  pytest tests/
  ```

  When `docs/`, `research/` or a docstring changed, also build the docs as
  CI does: `cd docs && make html SPHINXOPTS="-W --keep-going"`.
- **Never commit with warnings or failures.**
- **Ask before adding a dependency** outside the list in CONTRIBUTING.md.
