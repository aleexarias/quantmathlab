# Contributing to quantmathlab

Thank you for your interest in contributing to `quantmathlab`! This document
provides guidelines for contributing to the project.

`quantmathlab` is built to accommodate many model families, not one, and new
models and methods are welcome contributions. See "Adding Code" below for the
bar a new addition has to clear.

## Design Principles

Contributions should preserve the principles the library is built on:

- **Arbitrage awareness.** Fitting routines that can enforce no-arbitrage
  constraints do so, and `quantmathlab.validation` provides independent
  checks so that any output can be audited.
- **Reference implementations first.** Every algorithm exists as readable,
  vectorized NumPy/SciPy. `quantmathlab.backend` is a dispatch layer so that
  accelerated C++ kernels can be introduced without changing any public API.
- **Typed and tested.** `mypy --strict` passes over the whole source tree, and
  every numerical function has unit tests against reference values plus
  property-based tests for its invariants.

## Project Layout

```
src/quantmathlab/        # the library
├── __init__.py          # version
├── py.typed             # marks the package as typed
├── _typing.py           # FloatArray, BoolArray type aliases
├── backend/             # C++ kernels (_cpp) and NumPy references
├── datasets/            # data loading and generation
├── models/              # analytic and semi-analytic pricers
├── validation/          # consistency checks and accuracy metrics
└── viz/                 # plotting functions

research/<slug>/         # one folder per paper, <slug> = its BibTeX key
├── README.rst           # documentation page
├── <slug>.py            # notebook (sphinx-gallery format, # %% cells)
└── latex/main.tex       # notes with the derivations

tests/                   # pytest suite
examples/                # sphinx-gallery examples of the API
docs/                    # Sphinx sources; docs/_ext/ publishes research/
cpp/                     # C++ kernel sources and their CMake build
```

## Branch Model

- **`main`**: Always releasable; protected with branch rules.
- **`develop`**: Integration branch for features; protected with the same
  branch rules.
- **Feature/fix branches**: `feature/<name>`, `fix/<name>`, `docs/<name>`
  branched from `develop`, merged back via squash-merge PR.

## Branch Protection Rules (on GitHub)

These rules are active on `main` and `develop`:

1. Require a pull request before merging.
2. Require status checks to pass before merging: `lint`, `docs`, and the
   six `test (<python>, <os>)` jobs (3.12, 3.13 × ubuntu/macos/windows).
3. Require branches to be up to date before merging.

Merged pull request branches are deleted automatically.

## Automated Updates

Dependabot opens pull requests for GitHub Actions versions only, targeting
`develop` so they are tested there before reaching `main`. Python
dependencies are not updated by bots: for a library without a lockfile
Dependabot would only raise minimum versions in `pyproject.toml`, and CI
already installs the latest releases on every run.

## Commit Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): subject

body

footer
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `perf`, `ci`, `chore`.

Example:
```
feat(models): implement Black-Scholes pricer

Add vectorized call and put prices with put-call parity tests.
Prices are checked against published reference values.

Closes #42
```

## Versioning

Uses [Semantic Versioning](https://semver.org/). The version is single-sourced
in `src/quantmathlab/__init__.py` as `__version__`. Everything else derives
from it, so never hardcode the version anywhere else:

- **Distribution metadata**: `pyproject.toml` declares
  `dynamic = ["version"]` and `[tool.scikit-build.metadata.version]`
  reads that line, so wheels and sdists pick it up at build time.
- **Documentation**: `docs/conf.py` imports `quantmathlab.__version__`,
  exposing it as the `|release|` and `|version|` substitutions and in the
  footer of every page.

`CITATION.cff` is the one exception. It is static metadata read by GitHub and
citation managers, so it cannot derive the version and must be bumped by hand.

To bump the version:

1. Edit `__version__` in `src/quantmathlab/__init__.py`.
2. Edit `version:` in `CITATION.cff` to match.

## Release Process

Releases are made by hand:

1. Bump the version as above.
2. Update `CHANGELOG.md` with a section for the new version.
3. Create a git tag and push it: `git tag v<version>`, then
   `git push origin v<version>`. The tag must match `__version__`.
4. Build the sdist and wheel and upload them to PyPI:

   ```bash
   pip install build twine
   python -m build
   twine upload dist/*
   ```

## Code Conventions

- **Type hints everywhere.** `mypy --strict` must pass. No `Any` except in
  rare cases, justified with a comment.
- **Docstrings.** numpydoc format on every public function and class: a
  one-line summary, an extended description if needed, Parameters,
  Returns and Raises sections, and an Examples section with executable
  code.
- **Citations.** Papers are never written out; they live in
  `docs/references.bib`. Docstrings cite them with `:footcite:t:` and end
  with a `References` section containing only `.. footbibliography::`;
  hand-written `.rst` pages use `:cite:t:` / `:cite:p:` instead. Keys are
  `<surnames>_<year>_<word>`: lowercase surnames joined with `+`, the year
  and one identifying word, e.g. `heston_1993_closed`,
  `breeden+litzenberger_1978_prices`.
- **Mathematics as LaTeX**, never plain text: short expressions inline with
  `:math:`, larger ones in a `.. math::` block. A docstring containing a
  backslash must be a raw string (`r"""`).
- **No comments by default.** Code should explain itself. Comment only when
  the *why* is not obvious: a hidden constraint, a workaround, a subtle
  invariant. No step labels that restate the code, no narrated reasoning
  or arithmetic, and no comments restating the assertion below them.
- **79-character lines** for code and prose alike (Python, Markdown,
  reStructuredText, config). `ruff format` wraps code; docstrings, comments
  and string literals are wrapped by hand, and `ruff check` enforces the
  limit (E501). Only URLs and Markdown table rows may run longer.
- **Few dependencies.** Stick to NumPy, SciPy, pandas and matplotlib, plus
  cvxpy for optimization. Discuss anything else in an issue first.

## Testing Standards

Every function that computes or manipulates numbers has:

- unit tests against analytic or reference results,
- property-based tests (hypothesis) for its invariants,
- tests in isolation and in the end-to-end pipelines that use it.

Every line of code is tested, even one that only calls other functions.
Test thresholds come from running the code, never from guesses, with a
note on why they are reasonable.

## Adding Code

### A numerical function

1. Write it with complete type hints and a numpydoc docstring.
2. Add a unit test against a known reference (an analytic formula, another
   library).
3. Add a property test (hypothesis) for its invariants, where applicable.
4. Run the checks under "Running Tests and Checks".
5. Add a CHANGELOG entry and document it on its `docs/modules/` page.
6. Preferably, add a gallery example in
   `examples/<n>_<topic>/plot_<name>.py`.

### A C++ kernel

Follow "Adding a kernel" in `cpp/README.md`: the C++ function, its pybind11
binding, its signature in `backend/_cpp.pyi`, and a NumPy version in
`backend/_python.py` that the tests compare it against. The public function
calling it validates the inputs and follows the steps above. After changing
C++ files, reinstall the package to recompile them.

### A research paper

1. Create `research/<slug>/`, with `<slug>` the paper's BibTeX key,
   holding a documentation page `README.rst`, the notes in
   `latex/main.tex` and a notebook `<slug>.py`; notebook names must be
   unique across papers.
2. Add the paper to `docs/references.bib`.
3. Implement what the paper needs in `src/quantmathlab/` as above, and use
   it from the notebook.
4. Build the docs: the paper appears under Research with its page, notes
   and notebook.

Every number or figure in the notes is produced by the paper's notebook,
never by hand. Notebooks run in every docs build, so a library change that
breaks one is fixed before merging. `research/README.md` has the details.

## Running Tests and Checks

Set up as described under [Installation](README.md#installation) in the
README: your own conda environment, the project installed with
`pip install -e ".[dev,docs]"`, LaTeX for the documentation, and the git
hooks. The hooks run the same checks as CI before your code leaves your
machine: ruff and mypy on every commit, and the test suite on every push.
Only the documentation build is left to CI.

```bash
# Install development and documentation dependencies
pip install -e ".[dev,docs]"

# Install the git hooks
pre-commit install

# Run linter
ruff check src tests

# Format code
ruff format src tests

# Type check
mypy --strict src

# Run tests with coverage
pytest --cov=quantmathlab --cov-report=html tests

# Run tests matching a name, or only the slow ones
pytest tests -k <substring>
pytest tests -m slow

# Run benchmarks
pytest --benchmark-only benchmarks
```

## Documentation

Documentation lives in `docs/` and builds with Sphinx. CI builds it with
`-W`, so every warning is an error. Gallery examples are in `examples/`
organized by numbered subfolders. Each `.py` file in `examples/` must start
with a docstring header (see `sphinx-gallery` docs).

Papers live in `research/<slug>/`, each with a documentation page, LaTeX
notes and a notebook, and are published in the Research section of the
documentation by `docs/_ext/research.py`. Every `.py` file directly inside
a paper's folder is executed as a notebook. Building the documentation
needs the LaTeX installation from [Installation](README.md#installation)
to compile the notes.

In reStructuredText:

- Library objects named in prose are cross-references, not literals:
  `` :class:`~quantmathlab.<subpackage>.<Class>` ``,
  `` :func:`~quantmathlab.<subpackage>.<function>` ``,
  `` :mod:`~quantmathlab.models` ``.
- A bullet or numbered list needs a blank line before it, or it renders as
  a run-on paragraph.

```bash
# Build docs locally
cd docs && make html
# Open _build/html/index.html
```

## Questions?

Open an issue on GitHub or email
[aleexariasg@gmail.com](mailto:aleexariasg@gmail.com).
