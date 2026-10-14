# Changelog

All notable changes to this project will be documented in this file.

The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

Project scaffold. No methods are implemented yet; they are added paper by
paper.

### Added

- Package skeleton: `models`, `datasets`, `validation`, `viz` and
  `backend` subpackages, fully typed (`py.typed`, `mypy --strict`), with the
  version single-sourced in `quantmathlab.__version__`.
- `research/`: one folder per paper with a documentation page, LaTeX notes
  and a notebook, starting from a placeholder.
- Sphinx documentation, built warning-free with `-W`: API reference per
  subpackage, sphinx-gallery examples, a References page generated from
  `docs/references.bib`, and a Research section that shows each paper's
  page, its notes compiled with latexmk, and its executed notebook.
- Project conventions: 79-character lines enforced by ruff, BibTeX keys of
  the form `surname+surname_year_word`, `CITATION.cff`.
- Requires Python 3.12+ and NumPy 2.0+.
