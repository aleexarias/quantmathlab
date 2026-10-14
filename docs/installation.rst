Installation
=============

Requirements
------------

- Python 3.12+
- NumPy >= 2.0

Installation from Source
-------------------------

Have your own conda environment (or any other virtual environment) with
Python 3.12+ ready and activated, then clone the repository and install it
in editable mode:

.. code-block:: bash

   git clone https://github.com/aleexarias/quantmathlab.git
   cd quantmathlab
   pip install -e .

Install with development and documentation dependencies. Building the
documentation also compiles the LaTeX notes of the :doc:`research/index`
section, which needs a TeX distribution with ``latexmk``. It is a system
package that pip cannot install, so add it alongside:

.. code-block:: bash

   pip install -e ".[dev,docs]"

   # LaTeX for the research notes (Debian/Ubuntu)
   sudo apt-get install latexmk texlive-latex-recommended \
       texlive-fonts-recommended

On macOS install `MacTeX <https://www.tug.org/mactex/>`_, and on Windows
`MiKTeX <https://miktex.org/>`_ or `TeX Live <https://tug.org/texlive/>`_;
all of them include ``latexmk``.

If you are developing, also install the git hooks. They run the same
checks as CI before your code leaves your machine: ruff and mypy on every
commit, and the test suite on every push. Only the documentation build is
left to CI.

.. code-block:: bash

   pre-commit install

Verify Installation
-------------------

Test that the package imports correctly:

.. code-block:: python

   import quantmathlab
   print(quantmathlab.__version__)

This prints |release| for the checkout these docs were built from.
``quantmathlab.__version__`` is the project's single source of truth for
the version: the distribution metadata and this documentation both derive
from it.

Run the test suite:

.. code-block:: bash

   pytest tests/

Build Documentation
--------------------

The documentation is hosted at https://quantmathlab.readthedocs.io/, with
a version for each of the ``main`` and ``develop`` branches. To build it
from the repository instead:

.. code-block:: bash

   pip install -e ".[docs]"
   cd docs
   make html
   # Open _build/html/index.html in a browser

This renders the API reference, the example gallery and the
:doc:`research/index` section. Compiling the research notes needs the
LaTeX installation from `Installation from Source`_. Without it the build
still completes, but warns that the notes could not be compiled, and so
fails under ``-W``.
