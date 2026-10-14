"""
Notebook
========

Numerical experiments for the placeholder paper.
"""

# %%
# Setup
# -----

import matplotlib.pyplot as plt
import numpy as np

import quantmathlab

print(f"quantmathlab {quantmathlab.__version__}")

# %%
# A first figure
# --------------
# The standard normal density, standing in for the paper's first result.

x = np.linspace(-4.0, 4.0, 401)
density = np.exp(-0.5 * x**2) / np.sqrt(2.0 * np.pi)

fig, ax = plt.subplots()
ax.plot(x, density)
ax.set_xlabel(r"$x$")
ax.set_ylabel(r"$\varphi(x)$")
plt.show()
