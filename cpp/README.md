# C++ Backend

Kernels written in C++17 and bound to Python with pybind11. Installing the
package (scikit-build-core and CMake, configured in `pyproject.toml`)
compiles them into the extension module `quantmathlab.backend._cpp`.

## Layout

```
cpp/
├── CMakeLists.txt        # builds src/ into quantmathlab/backend/_cpp
└── src/
    ├── bindings.cpp      # pybind11 module exposing the kernels
    ├── black_scholes.hpp
    └── black_scholes.cpp
```

## How kernels are used

Kernels compute; they do not validate. Each is a plain C++ function on
scalars, exposed with `py::vectorize` so that it broadcasts over NumPy
arrays. The public function in its subpackage of `src/quantmathlab/`
checks the inputs and then calls the kernel, as
`quantmathlab.models.bs_call_price` does with `black_scholes_call`.

Every kernel also has a readable NumPy version with the same signature in
`src/quantmathlab/backend/_python.py`, and the tests check that both agree.

## Adding a kernel

1. Write the function in `src/<name>.cpp`, declare it in `src/<name>.hpp`,
   and add the `.cpp` file to `pybind11_add_module` in `CMakeLists.txt`.
2. Expose it in `src/bindings.cpp`.
3. Declare its signature in `src/quantmathlab/backend/_cpp.pyi`, so that
   `mypy --strict` can check the code calling it.
4. Write the NumPy version in `src/quantmathlab/backend/_python.py`.
5. Call it from the public function, and test that the C++ and NumPy
   versions agree.

## Rebuilding

The editable install picks up changes to Python files immediately, but
changes to C++ files only take effect after rebuilding:

```bash
pip install -e ".[dev,docs]"
```

Build files are cached in `build/`, so rebuilds only recompile what
changed.
