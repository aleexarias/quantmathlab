quantmathlab
============

I figured that instead of waiting for someone to invite me onto a research
team, I might as well start doing research myself. I enjoy reading academic
papers, and at some point I decided to start turning ideas on paper into
experiments. I began implementing them, testing their assumptions, and
occasionally discovering that reproducing a paper is a lot harder than reading
one.That's how ``quantmathlab`` came about.

.. image:: _static/logo_light_full.svg
   :class: only-light
   :align: center
   :width: 200px
   :alt: quantmathlab logo

.. image:: _static/logo_dark_full.svg
   :class: only-dark
   :align: center
   :width: 200px
   :alt: quantmathlab logo

``quantmathlab`` is a personal research lab for quantitative finance, built
one paper at a time. Each paper gets its mathematics worked through and
documented in LaTeX, while the methods are implemented as typed, tested
Python code. The goal is to gradually build a reusable library with a
consistent API, making it easier to combine and compare ideas from different
papers on the same data.

Curious about what I have been working on? Head over to the
:doc:`research/index` section: every paper has its own page with a short
summary, my LaTeX notes working through the mathematics, and a notebook with
the experiments.

I'm always open to suggestions, and I'd especially love to hear about papers
you think I should take on next. Send them my way at
aleexariasg@gmail.com.

.. admonition:: Latest update

   :doc:`Is attention all you need for intraday Forex trading? <research/gradzki+wojcik_2023_attention/index>`,
   can the Transformer architecture predict short-term movements of foreign
   exchange rates?

.. toctree::
   :maxdepth: 1
   :hidden:

   installation
   research/index
   modules/index
   auto_examples/index
   references
   development
   contributors

Library Layout
--------------

The library is organised in subpackages, each an extension point for one
family of methods:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Subpackage
     - Role
   * - :doc:`modules/models`
     - Analytic and semi-analytic pricers
   * - :doc:`modules/datasets`
     - Data loading and generation
   * - :doc:`modules/features`
     - Indicators and model inputs
   * - :doc:`modules/validation`
     - Quality assessment
   * - ``quantmathlab.viz``
     - Plotting helpers
   * - ``quantmathlab.backend``
     - Kernel dispatch

Research Workflow
-----------------

Every paper gets a folder ``research/<slug>/`` with a documentation page
(``README.rst``), notes with the derivations (``latex/main.tex``) and a
notebook with the numerical experiments (``<slug>.py``). The documentation
lists the papers in its Research section, where each one shows its page,
the compiled notes and the executed notebook.

The :doc:`development` describes how to add a paper.

Installation
------------

The :doc:`installation` page covers setting up an environment, installing
the package, the LaTeX distribution the documentation build needs, and the
git hooks for development.

Scope
-----

**quantmathlab is a research library.** It is intended for academic work,
method development, backtesting, and validating numerical implementations
against references.

**It is not a trading system.** It does not provide real-time pricing, order
management, or execution.

Extending quantmathlab
----------------------

Every new addition to the library must be:

1. Placed in the subpackage of ``src/quantmathlab/`` whose role it fits.
2. Documented, with docstrings and on its API page in ``docs/modules/``.
3. Tested.
4. Preferably shown in an example in ``examples/``.

The :doc:`development` has the full workflow and project conventions.

Citation
--------

If you use quantmathlab in published research, please cite:

.. code-block:: bibtex

   @software{ariasgomez_2026_quantmathlab,
     author = {Arias Gomez, Alejandro},
     title = {quantmathlab: A research library for quantitative finance},
     year = {2026},
     url = {https://github.com/aleexarias/quantmathlab}
   }

License
-------

BSD-3-Clause. See the
`LICENSE <https://github.com/aleexarias/quantmathlab/blob/main/LICENSE>`__
file.

Contributing
------------

Contributions are welcome. See :doc:`contributors` and the
:doc:`development`.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
