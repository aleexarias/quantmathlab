#include "black_scholes.hpp"

#include <cmath>

namespace quantmathlab {

namespace {

struct D1D2 {
    double d1;
    double d2;
};

D1D2 d1_d2(double spot, double strike, double maturity,
           double rate, double volatility) {
    const double spread = volatility * std::sqrt(maturity);
    const double d1 = (std::log(spot / strike) +
                       (rate + 0.5 * volatility * volatility) * maturity) /
                      spread;
    return {d1, d1 - spread};
}

}  // namespace

double normal_cdf(double x) {
    // erfc keeps full precision in the lower tail, where 1 + erf(x)
    // would cancel to zero.
    return 0.5 * std::erfc(-x / std::sqrt(2.0));
}

double black_scholes_call(double spot, double strike, double maturity,
                          double rate, double volatility) {
    const auto [d1, d2] = d1_d2(spot, strike, maturity, rate, volatility);
    return spot * normal_cdf(d1) -
           strike * std::exp(-rate * maturity) * normal_cdf(d2);
}

double black_scholes_put(double spot, double strike, double maturity,
                         double rate, double volatility) {
    const auto [d1, d2] = d1_d2(spot, strike, maturity, rate, volatility);
    return strike * std::exp(-rate * maturity) * normal_cdf(-d2) -
           spot * normal_cdf(-d1);
}

}  // namespace quantmathlab
