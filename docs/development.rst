Development Guide
==================

This guide covers the development workflow for quantmathlab contributors.

Branch Model
------------

- **main**: Always releasable; protected with branch rules.
- **develop**: Integration branch for features; protected with the same
  branch rules.
- **Feature/fix branches**: ``feature/<name>``, ``fix/<name>``,
  ``docs/<name>`` branched from ``develop``, merged back via squash-merge
  PR.

The branch rules apply to both ``main`` and ``develop``:

1. Require a pull request before merging.
2. Require status checks to pass before merging: ``lint`` (ruff and
   mypy), ``docs`` (the documentation build), and the six
   ``test (<python>, <os>)`` jobs (3.12, 3.13 × ubuntu/macos/windows).
3. Require branches to be up to date before merging.

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

Setting Up Development Environment
-----------------------------------

Have your own conda environment (or any other virtual environment) with
Python 3.12+ ready and activated, then clone the repository and install it
with the development and documentation dependencies:

.. code-block:: bash

   git clone https://github.com/aleexarias/quantmathlab.git
   cd quantmathlab
   pip install -e ".[dev,docs]"

Building the documentation also needs LaTeX with ``latexmk``; see
:doc:`installation` for the command on each platform.

If you are developing, also install the git hooks. They run the same
checks as CI before your code leaves your machine: ruff and mypy on every
commit, and the test suite on every push. Only the documentation build is
left to CI.

.. code-block:: bash

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

Write numpydoc docstrings on all public functions and classes. The example
below, a Black-Scholes call pricer, uses every section the project relies
on: a one-line summary, an extended description with inline and display
mathematics and a citation, then ``Parameters``, ``Returns``, ``Raises``,
``See Also``, ``Notes``, ``References`` and ``Examples``, in numpydoc's
order. The docstring is a raw string (``r"""``) because the LaTeX contains
backslashes, and the examples are executable, with outputs taken from
running the code. Only the signature and docstring are shown.

.. code-block:: python

   import numpy.typing as npt

   from quantmathlab._typing import FloatArray


   def bs_call_price(
       spot: float,
       strike: npt.ArrayLike,
       maturity: float,
       rate: float,
       volatility: float,
   ) -> FloatArray:
       r"""Price European call options with the Black-Scholes formula.

       Computes the price of a European call under the model of
       :footcite:t:`black+scholes_1973_pricing`, in which the underlying
       follows a geometric Brownian motion with constant volatility
       :math:`\sigma` and the risk-free rate :math:`r` is constant:

       .. math::

          C = S\,\Phi(d_1) - K e^{-rT}\,\Phi(d_2),
          \qquad
          d_{1,2} = \frac{\ln(S/K) + \left(r \pm \tfrac{1}{2}\sigma^2\right) T}
                         {\sigma\sqrt{T}},

       where :math:`\Phi` is the standard normal distribution function.

       Parameters
       ----------
       spot : float
           Current price of the underlying, :math:`S > 0`.
       strike : array_like
           Strike prices, :math:`K > 0`; a scalar or an array.
       maturity : float
           Time to expiry in years, :math:`T > 0`.
       rate : float
           Continuously compounded risk-free rate :math:`r`.
       volatility : float
           Annualized volatility of the underlying, :math:`\sigma > 0`.

       Returns
       -------
       FloatArray
           Call prices, with the shape of ``strike``.

       Raises
       ------
       ValueError
           If ``spot``, ``maturity`` or ``volatility`` is not positive, or
           if any strike is not positive.

       See Also
       --------
       bs_put_price : Put prices under the same model.
       implied_volatility : Recovers :math:`\sigma` from a quoted price.

       Notes
       -----
       Prices satisfy put-call parity, :math:`C - P = S - K e^{-rT}`, and
       decrease and are convex in the strike; the property-based tests check
       both.

       References
       ----------
       .. footbibliography::

       Examples
       --------
       A single at-the-money call:

       >>> print(f"{bs_call_price(100.0, 100.0, 1.0, 0.05, 0.2):.4f}")
       10.4506

       Several strikes at once:

       >>> bs_call_price(100.0, [90.0, 100.0, 110.0], 1.0, 0.05, 0.2).round(4)
       array([16.6994, 10.4506,  6.0401])
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

Releases are made by hand:

1. Bump the version as above.
2. Update ``CHANGELOG.md`` with a section for the new version.
3. Create a git tag and push it: ``git tag v<version>``, then
   ``git push origin v<version>``. The tag must match ``__version__``.
4. Build the sdist and wheel and upload them to PyPI:

   .. code-block:: bash

      pip install build twine
      python -m build
      twine upload dist/*

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
