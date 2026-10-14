# C++ Backend (Future)

This directory contains the C++ implementation of performance-critical
kernels.

## Plan

Will use pybind

1. Identify hot paths via profiling.
2. Implement in C++17 using Eigen for linear algebra.
3. Wrap with pybind11.
4. Migrate build backend from `hatchling` to `scikit-build-core`.
5. Add conditional compilation: if MSVC/gcc/clang + optional C++ extension
   found, build the extension; otherwise fall back to pure Python via the
   `backend` dispatch layer.

## Structure (to be added)

```
cpp/
├── CMakeLists.txt
├── src/
│   ├── <kernel>/
│   └── pybind11_bindings.cpp
└── tests/
```

## Not Yet Implemented

- Do not add code to this directory until performance profiling indicates
  necessity.
- All numerical algorithms have pure-Python reference implementations in
  `quantmathlab/`.
