Research
========

The library grows paper by paper. Each paper studied for the project has a
folder ``research/<slug>/`` in the repository with three parts:

- a documentation page summarising the paper (``README.rst``),
- notes with the derivations, written in LaTeX (``latex/main.tex``),
- a notebook with the numerical experiments (``<slug>.py``).

Methods that come out of a paper are implemented in the library itself and
documented in the :doc:`../modules/index`.

.. toctree::
   :maxdepth: 1
   :glob:

   */index
