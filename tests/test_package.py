"""Tests for the package skeleton: version and subpackage imports."""

import importlib
import re

import pytest

import quantmathlab

SUBPACKAGES = [
    "backend",
    "datasets",
    "models",
    "validation",
    "viz",
]


def test_version_is_semver() -> None:
    assert re.fullmatch(r"\d+\.\d+\.\d+", quantmathlab.__version__)


@pytest.mark.parametrize("name", SUBPACKAGES)
def test_subpackage_imports(name: str) -> None:
    module = importlib.import_module(f"quantmathlab.{name}")
    assert module.__doc__
