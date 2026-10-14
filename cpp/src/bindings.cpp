#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>

#include "black_scholes.hpp"

namespace py = pybind11;

PYBIND11_MODULE(_cpp, module) {
    module.doc() = "Compiled C++ kernels of quantmathlab.";

    module.def("black_scholes_call",
               py::vectorize(quantmathlab::black_scholes_call),
               py::arg("spot"), py::arg("strike"), py::arg("maturity"),
               py::arg("rate"), py::arg("volatility"),
               "Black-Scholes call prices, broadcast over the inputs.");

    module.def("black_scholes_put",
               py::vectorize(quantmathlab::black_scholes_put),
               py::arg("spot"), py::arg("strike"), py::arg("maturity"),
               py::arg("rate"), py::arg("volatility"),
               "Black-Scholes put prices, broadcast over the inputs.");
}
