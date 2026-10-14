Research
========

Welcome to the heart of ``quantmathlab``. This folder is my playground:
everything else in the repository exists to serve what happens here.

One folder per paper studied for the project. Reading a paper produces
three things, and the documentation publishes all of them under its
Research section. Each paper's folder ``research/<slug>/`` holds:

- ``README.rst``: the documentation page summarising the paper
- ``<slug>.py``: the notebook with the numerical experiments
- ``latex/main.tex``: the notes with the derivations

Methods a paper needs are implemented in ``src/quantmathlab/``, with tests,
and used from its notebook. Results quoted in the notes come from the
notebook, never typed in by hand.

.. toctree::
   :maxdepth: 1
   :glob:

   */index
