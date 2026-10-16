# Changelog

All notable changes to this project will be documented in this file.

The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] - 2026-10-16

### Added

- `quantmathlab.datasets.load_histdata`: one-minute foreign exchange quotes
  from histdata.com, downloaded once per pair and year and returned as a
  pandas DataFrame with histdata.com's own timestamps (US Eastern Standard
  Time, without a time zone), without the repeated bars some yearly files
  contain.
- `quantmathlab.datasets.resample_bars`: aggregation of any time-indexed
  open, high, low and close bars into longer bars of a given length, laid
  out from a chosen time of day, recording how many bars each was built
  from and skipping periods without any.
- `quantmathlab.features`, a subpackage turning market data into model
  inputs: the relative strength index, MACD, stochastic oscillator,
  Williams %R and Bollinger bands of a price series; `cyclical_encoding`,
  the sine and cosine of a periodic quantity such as the hour; and
  `sliding_windows`, overlapping windows of consecutive rows as a view of
  the table.
- `quantmathlab.validation.accuracy` and `quantmathlab.validation.roc_auc`:
  the share of correct predictions of a classifier, and the area under the
  ROC curve of a binary classifier, computed from the ranks of its scores.
- Research papers can run work too slow for the documentation build, such
  as training a model, from a script in a subfolder, committing its output
  in `results/` for the notebook to read.
- Research notes for Grądzki and Wójcik (2023), "Is attention all you need
  for intraday Forex trading?" A training script trains the paper's
  Transformer with PyTorch, and saves its predictions for the notebook.

### Changed

- Requires pandas 2.0+ and histdata.
- Documentation built locally or in CI shortens the branch name shown next
  to the logo: names of 30 or more characters show their first 27 followed
  by `...`, and hovering over the label shows the full name.

## [0.1.1] - 2026-10-14

### Added

- `quantmathlab.models.bs_call_price` and `bs_put_price`: Black-Scholes
  prices of European options, broadcasting over all arguments, computed by
  a C++ kernel.
- C++ backend: kernels in `cpp/src/`, bound to Python with pybind11 as
  `quantmathlab.backend._cpp`, with readable NumPy reference versions in
  `quantmathlab.backend._python` that the tests compare against.

### Changed

- The package is built with scikit-build-core and CMake instead of
  hatchling, so installing from source compiles the C++ kernels and needs a
  C++17 compiler.

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
