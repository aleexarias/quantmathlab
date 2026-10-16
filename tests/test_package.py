"""Tests for the package skeleton: version and subpackage imports."""

import importlib
import re

import pytest

import quantmathlab

SUBPACKAGES = [
    "backend",
    "datasets",
    "features",
    "models",
    "validation",
    "viz",
]


def test_version_is_semver() -> None:
    """The version string has the MAJOR.MINOR.PATCH form."""
    assert re.fullmatch(r"\d+\.\d+\.\d+", quantmathlab.__version__)


@pytest.mark.parametrize("name", SUBPACKAGES)
def test_subpackage_imports(name: str) -> None:
    """Each subpackage imports and has a docstring describing it."""
    module = importlib.import_module(f"quantmathlab.{name}")
    assert module.__doc__
