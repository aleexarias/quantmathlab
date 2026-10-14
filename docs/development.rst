Development Guide
==================

This guide covers the development workflow for quantmathlab contributors.

Branch Model
------------

- **main**: Always releasable. Protected with required checks.
- **develop**: Integration branch for features (optional staging).
- **Feature branches**: `feature/<name>`, `fix/<name>`, `docs/<name>`.
  Squash-merge back to main via PR.

All branches require:

- Tests (tests.yml passes)
- Lint (ruff check passes)
- Type checking (mypy --strict passes)
- Docs build (docs.yml passes)

Commit Convention
-----------------

Follow `Conventional Commits <https://www.conventionalcommits.org/>`_:

.. code-block:: text

   type(scope): subject

   body

   footer

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `perf`, `ci`, `chore`.

Example:

.. code-block:: text

   feat(models): implement Black-Scholes pricer

   Add vectorized call and put prices with put-call parity tests.
   Prices are checked against published reference values.

   Closes #42

Changelog and version bumps are automated from these commits.

Setting Up Development Environment
-----------------------------------

Clone and install with dev dependencies:

.. code-block:: bash

   git clone https://github.com/aleexarias/quantmathlab.git
   cd quantmathlab
   pip install -e ".[dev,docs]"
   pre-commit install

Quality Checks
--------------

Run locally before pushing:

.. code-block:: bash

   ruff check src tests       # Lint
   ruff format src tests      # Format
   mypy --strict src          # Type check
   pytest tests/              # Unit tests

All checks must pass in CI before merge.

Testing Requirements
--------------------

Every numerical function gets:

1. **Unit tests** against known reference values or independently verified
   results
2. **Property tests** (via hypothesis) for invariants
3. **Integration tests** in the end-to-end pipelines that use them

Example:

.. code-block:: python

   def test_bs_price_put_call_parity():
       """Test C - P = S - K*exp(-rT)."""
       # Unit test
       calls = bs_price(S, K, T, r, sigma, flag='C')
       puts = bs_price(S, K, T, r, sigma, flag='P')
       parity_lhs = calls - puts
       parity_rhs = S - K * df
       np.testing.assert_allclose(parity_lhs, parity_rhs, rtol=1e-10)

   @given(K=st.floats(50, 150))
   def test_bs_call_decreasing_in_strike(K):
       """Property: call price decreases with strike."""
       c1 = bs_price(100, K, T, r, sigma, flag='C')
       c2 = bs_price(100, K*1.01, T, r, sigma, flag='C')
       assert c1 > c2  # Stricter = lower price

Building Documentation
----------------------

Build locally:

.. code-block:: bash

   cd docs
   make clean
   make html
   # Open _build/html/index.html

The docs build will:

- Run all gallery examples and research notebooks
- Compile each paper's LaTeX notes with ``latexmk``
- Auto-generate API reference from docstrings

Research Workflow
-----------------

Each paper studied for the project lives in ``research/<slug>/``, where
``<slug>`` is its BibTeX key:

- ``README.rst``: the documentation page, summarising the paper
- ``latex/main.tex``: notes with the derivations
- ``<slug>.py``: a notebook with the numerical experiments

The ``research`` extension in ``docs/_ext/research.py`` finds every folder
with a ``README.rst`` and publishes it in the :doc:`research/index`
section: the README becomes the paper's page, the notebook is executed by
sphinx-gallery, and the notes are compiled and embedded in a Notes page.
Methods a paper needs go into ``src/quantmathlab/`` with the usual tests,
and every number quoted in the notes is produced by the notebook.
``research/README.md`` describes how to add a paper.

API Documentation
------------------

Write numpydoc docstrings on all public functions/classes:

.. code-block:: python

   def density_estimation(
       chain: OptionChain, smoothness: float
   ) -> RiskNeutralDensity:
       """Extract risk-neutral density from option chain.

       Fits an arbitrage-free surface using constrained cubic splines,
       then applies the formula of
       :footcite:t:`breeden+litzenberger_1978_prices` to extract density.

       Parameters
       ----------
       chain : OptionChain
           Option chain with bid-ask quotes.
       smoothness : float
           Regularization parameter (higher = smoother surface).

       Returns
       -------
       RiskNeutralDensity
           Object with pdf(), cdf(), moments, etc.

       References
       ----------
       .. footbibliography::

       Examples
       --------
       >>> from quantmathlab.datasets import synthetic_heston_chain
       >>> chain = synthetic_heston_chain(T=0.5, n_strikes=40)
       >>> density = density_estimation(chain, smoothness=0.001)
       >>> print(density.mean())  # Should be ~forward price
       """

Versioning
----------

Semantic versioning: MAJOR.MINOR.PATCH

- **MAJOR**: Incompatible API changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

The version is single-sourced in ``src/quantmathlab/__init__.py`` as
``__version__`` (currently |release|). Everything else derives from it:

- **Distribution metadata**: ``pyproject.toml`` declares
  ``dynamic = ["version"]`` and ``[tool.hatch.version]`` reads that line,
  so wheels and sdists pick it up at build time.
- **Documentation**: ``docs/conf.py`` imports
  ``quantmathlab.__version__``, which Sphinx exposes as the ``|release|``
  and ``|version|`` substitutions and renders into the footer of every
  page.

``CITATION.cff`` is the one exception: it is static metadata read by GitHub and
citation managers, so it cannot derive the version and must be bumped by hand.

To bump the version:

1. Edit ``__version__`` in ``src/quantmathlab/__init__.py``
2. Edit ``version:`` in ``CITATION.cff`` to match

Release Process
---------------

1. Bump the version as above
2. Update CHANGELOG.md with version and changes
3. Tag the release: ``git tag vX.Y.Z`` (must match ``__version__``)
4. Push tag: ``git push origin vX.Y.Z``
5. GitHub Actions builds and publishes to PyPI (via trusted publishing)

Performance
-----------

Profile hot paths before optimizing:

.. code-block:: bash

   python -m cProfile -s cumtime -m pytest tests/test_<module>.py

For C++ acceleration plans, see `cpp/README.md`.

Questions?
----------

See ``CONTRIBUTING.md`` for the full conventions and contribution
guidelines.
