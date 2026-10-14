<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)"
            srcset="https://raw.githubusercontent.com/aleexarias/quantmathlab/main/docs/_static/logo_dark_full.svg">
    <img src="https://raw.githubusercontent.com/aleexarias/quantmathlab/main/docs/_static/logo_light_full.svg"
         alt="quantmathlab" width="200">
  </picture>
</p>

# quantmathlab

quantmathlab is a research library for quantitative finance, built paper by
paper. Each paper is read, its mathematics is developed in LaTeX notes, and
the methods it needs are implemented in the library as typed, tested code
behind a small and consistent API, so that methods from different papers can
be composed and compared on the same data.

Go to the research folder to check stuff.

Latest update: latest study

## Repository Layout

| Path | Contents |
| --- | --- |
| [src/quantmathlab/](src/quantmathlab/) | The library |
| [research/](research/) | One folder per paper: documentation page, LaTeX notes, notebook |
| [tests/](tests/) | Unit and property-based tests for the library |
| [examples/](examples/) | Gallery examples of the library's API |
| [docs/](docs/) | Sphinx documentation |

The library is organised in subpackages, each an extension point for one
family of methods:

| Subpackage | Role |
| --- | --- |
| `quantmathlab.models` | Analytic and semi-analytic pricers |
| `quantmathlab.datasets` | Chain generation and loading |
| `quantmathlab.validation` | Quality assessment |
| `quantmathlab.viz` | Plotting helpers |
| `quantmathlab.backend` | Kernel dispatch |

## Research Workflow

Every paper gets a folder `research/<slug>/` with a documentation page
(`README.rst`), notes with the derivations (`latex/main.tex`) and a notebook
with the numerical experiments (`<slug>.py`). The documentation lists the
papers in its Research section, where each one shows its page, the compiled
notes and the executed notebook. See [research/README.md](research/README.md)
for how to add a paper.

## Installation

Clone the repository and install in editable mode:

```bash
git clone https://github.com/aleexarias/quantmathlab.git
cd quantmathlab
pip install -e .
```

With development and documentation dependencies:

```bash
pip install -e ".[dev,docs]"
```

Requires Python 3.12 or newer.

## Documentation

The documentation is not hosted yet. Build it from this repository:

```bash
pip install -e ".[docs]"
cd docs
make html
# Open docs/_build/html/index.html in a browser
```

The build renders the API reference, the example gallery and the Research
section. Compiling the research notes needs a LaTeX installation with
`latexmk` (on Debian/Ubuntu: `latexmk texlive-latex-recommended
texlive-fonts-recommended`).

## Scope

**quantmathlab is a research library.** It is intended for academic work,
method development, backtesting, and validating numerical implementations
against references.

**It is not a trading system.** It does not provide real-time pricing, order
management, or execution.

## Extending quantmathlab

New model families are welcome. The pattern is:

1. Add or reuse a base class in `quantmathlab/<module>/base.py` defining the
   `fit`/`predict` contract for that family.
2. Implement the subclass in `quantmathlab/<module>/<name>.py` with
   complete type hints and a numpydoc docstring citing its source paper.
3. Add unit tests against a reference, property tests for its invariants,
   and an integration test in the end-to-end pipeline.
4. Add a gallery example, an API page under `docs/modules/`, and a CHANGELOG
   entry.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full workflow and project
conventions.

## Citation

If you use quantmathlab in published research, please cite:

```bibtex
@software{ariasgomez_2026_quantmathlab,
  author = {Arias Gomez, Alejandro},
  title = {quantmathlab: A research library for quantitative finance},
  year = {2026},
  url = {https://github.com/aleexarias/quantmathlab}
}
```

## License

BSD-3-Clause. See [LICENSE](LICENSE).

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for
guidelines.
