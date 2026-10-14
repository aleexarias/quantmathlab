API Reference
=============

Complete API documentation for quantmathlab.

The subpackages are independent extension points:

- :mod:`~quantmathlab.models` holds pricers, and defines the base class
  that new pricers implement
- :mod:`~quantmathlab.datasets` and :mod:`~quantmathlab.validation` are the
  shared infrastructure that models build on.

Every public name is re-exported from its subpackage, so
``from quantmathlab.<subpackage> import <name>`` is the supported import
path.

.. toctree::
   :maxdepth: 2

   datasets
   models
   validation
