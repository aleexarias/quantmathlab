#ifndef QUANTMATHLAB_BLACK_SCHOLES_HPP
#define QUANTMATHLAB_BLACK_SCHOLES_HPP

namespace quantmathlab {

double normal_cdf(double x);

double black_scholes_call(double spot, double strike, double maturity,
                          double rate, double volatility);

double black_scholes_put(double spot, double strike, double maturity,
                         double rate, double volatility);

}  // namespace quantmathlab

#endif
