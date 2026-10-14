# Changelog

All notable changes to this project will be documented in this file.

The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-10-14

First release, version 0.1.0: the project setup. No methods are implemented
yet.

### Added

- Package skeleton: `models`, `datasets`, `validation`, `viz` and
  `backend` subpackages, each describing the methods it will hold. Fully
  typed (`py.typed`, `mypy --strict`), with the version single-sourced in
  `quantmathlab.__version__`.
- `research/`: one folder per paper, holding a documentation page, LaTeX
  notes and a notebook, starting from a placeholder paper.
- Sphinx documentation with the pydata theme, built warning-free with `-W`:
  installation and development guides, an API reference per subpackage,
  sphinx-gallery examples, a References page generated from
  `docs/references.bib`, and a Research section that shows each paper's
  page, its notes compiled with latexmk, and its executed notebook. The
  navbar shows the git branch the documentation was built from, with a
  version switcher between `main` and `develop` on Read the Docs.
- Continuous integration on GitHub Actions: ruff and mypy, the test suite
  on Python 3.12 and 3.13 across Linux, macOS and Windows, and the
  documentation build. Dependabot keeps the Actions up to date.
- Pre-commit hooks that run the same checks before code leaves the
  machine: ruff and mypy on every commit, the test suite on every push.
- Project conventions in `CONTRIBUTING.md`: 79-character lines, numpydoc
  docstrings with LaTeX mathematics, BibTeX keys of the form
  `surname+surname_year_word`, testing standards, the `main`/`develop`
  branch model and the manual release process. Also a code of conduct,
  `CITATION.cff`, issue and pull request templates and `CODEOWNERS`.
- Requires Python 3.12+ and NumPy 2.0+. Licensed under BSD-3-Clause.
