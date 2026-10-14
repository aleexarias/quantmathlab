cmake_minimum_required(VERSION 3.15...3.31)

project(quantmathlab_kernels LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)
find_package(pybind11 CONFIG REQUIRED)

pybind11_add_module(_cpp src/bindings.cpp src/black_scholes.cpp)
target_include_directories(_cpp PRIVATE src)

install(TARGETS _cpp DESTINATION quantmathlab/backend)
