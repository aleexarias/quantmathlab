"""
Black-Scholes prices
====================

Price European calls and puts with
:func:`~quantmathlab.models.bs_call_price` and
:func:`~quantmathlab.models.bs_put_price`, and see how the prices depend on
the strike and on the time to expiry.
"""

# %%
# Prices across strikes
# ---------------------
# The pricers broadcast over their arguments like NumPy arrays, so a whole
# grid of strikes is priced in a single call.

import matplotlib.pyplot as plt
import numpy as np

from quantmathlab.models import bs_call_price, bs_put_price

spot, maturity, rate, volatility = 100.0, 1.0, 0.05, 0.2
strikes = np.linspace(50.0, 150.0, 201)

calls = bs_call_price(spot, strikes, maturity, rate, volatility)
puts = bs_put_price(spot, strikes, maturity, rate, volatility)

fig, ax = plt.subplots()
ax.plot(strikes, calls, label="call")
ax.plot(strikes, puts, label="put")
ax.axvline(spot, color="grey", linestyle=":", label="spot")
ax.set_xlabel("strike $K$")
ax.set_ylabel("price")
ax.legend()
plt.show()

# %%
# Time to expiry
# --------------
# A column of maturities against a row of strikes prices every combination
# at once. The longer the time to expiry, the further the call price sits
# above its payoff at expiry, :math:`\max(S - K, 0)`.

maturities = np.array([[0.1], [1.0], [4.0]])
grid = bs_call_price(spot, strikes, maturities, rate, volatility)

fig, ax = plt.subplots()
for years, prices in zip(maturities[:, 0], grid, strict=True):
    ax.plot(strikes, prices, label=f"$T = {years:g}$ years")
ax.plot(strikes, np.maximum(spot - strikes, 0.0), "k--", label="payoff")
ax.set_xlabel("strike $K$")
ax.set_ylabel("call price")
ax.legend()
plt.show()

# %%
# Put-call parity
# ---------------
# Calls and puts with the same strike and expiry satisfy
# :math:`C - P = S - K e^{-rT}`, up to floating-point rounding.

gap = calls - puts - (spot - strikes * np.exp(-rate * maturity))
print(f"largest deviation from put-call parity: {np.abs(gap).max():.1e}")
