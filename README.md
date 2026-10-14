# quantmathlab

I figured that instead of waiting for someone to invite me onto a research
team, I might as well start doing research myself. I enjoy reading academic
papers, and at some point I decided to start turning ideas on paper into
experiments. I began implementing them, testing their assumptions, and
occasionally discovering that reproducing a paper is a lot harder than reading
one.That's how `quantmathlab` came about.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)"
            srcset="https://raw.githubusercontent.com/aleexarias/quantmathlab/main/docs/_static/logo_dark_full.svg">
    <img src="https://raw.githubusercontent.com/aleexarias/quantmathlab/main/docs/_static/logo_light_full.svg"
         alt="quantmathlab" width="200">
  </picture>
</p>

`quantmathlab` is a personal research lab for quantitative finance, built
one paper at a time. Each paper gets its mathematics worked through and
documented in LaTeX, while the methods are implemented as typed, tested
Python code. The goal is to gradually build a reusable library with a
consistent API, making it easier to combine and compare ideas from different
papers on the same data.

Curious about what I have been working on? Head over to the
[research folder](https://github.com/aleexarias/quantmathlab/tree/main/research):
every paper has its own folder with a short summary, my LaTeX notes working
through the mathematics, and a notebook with the experiments.

I'm always open to suggestions, and I'd especially love to hear about papers
you think I should take on next. Send them my way at
[aleexariasg@gmail.com](mailto:aleexariasg@gmail.com).

> [!NOTE]
> **Latest update:**
> [Placeholder Paper](https://github.com/aleexarias/quantmathlab/tree/main/research/placeholder),
> the testing paper used to set up the research workflow.

## Repository Layout

| Path | Contents |
| --- | --- |
| [src/quantmathlab/](src/quantmathlab/) | The Python package |
| [research/](research/) | One folder per paper: documentation page, LaTeX notes, notebook |
| [tests/](tests/) | Unit and property-based tests for the library |
| [examples/](examples/) | Gallery examples of the library's API |
| [docs/](docs/) | Sphinx documentation |

The library is organised in subpackages, each an extension point for one
family of methods:

| Subpackage | Role |
| --- | --- |
| `quantmathlab.models` | Analytic and semi-analytic pricers |
| `quantmathlab.datasets` | Data loading and generation |
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

Have your own conda environment (or any other virtual environment) with
Python 3.12+ ready and activated, then clone the repository and install it
in editable mode:

```bash
git clone https://github.com/aleexarias/quantmathlab.git
cd quantmathlab
pip install -e .
```

Installing compiles the package's C++ kernels, so you also need a C++17
compiler: GCC or Clang on Linux, the Xcode Command Line Tools on macOS, or
Visual Studio's MSVC on Windows. CMake and pybind11 are fetched
automatically during the build.

Install with development and documentation dependencies. Building the
documentation also compiles the LaTeX notes of the research papers, which
needs a TeX distribution with `latexmk`. It is a system package that pip
cannot install, so add it alongside:

```bash
pip install -e ".[dev,docs]"

# LaTeX for the research notes (Debian/Ubuntu)
sudo apt-get install latexmk texlive-latex-recommended \
    texlive-fonts-recommended
```

On macOS install [MacTeX](https://www.tug.org/mactex/), and on Windows
[MiKTeX](https://miktex.org/) or [TeX Live](https://tug.org/texlive/); all
of them include `latexmk`.

If you are developing, also install the git hooks. They run the same
checks as CI before your code leaves your machine: ruff and mypy on every
commit, and the test suite on every push. Only the documentation build is
left to CI.

```bash
pre-commit install
```

## Documentation

The documentation is hosted at
[quantmathlab.readthedocs.io](https://quantmathlab.readthedocs.io/), with a
version for each of the `main` and `develop` branches. To build it from this
repository instead:

```bash
pip install -e ".[docs]"
cd docs
make html
# Open _build/html/index.html in a browser
```

The build renders the API reference, the example gallery and the Research
section. Compiling the research notes needs the LaTeX installation from
[Installation](#installation). Without it the build still completes, but
warns that the notes could not be compiled, and so fails under `-W`.

## Scope

**quantmathlab is a research library.** It is intended for academic work,
method development, backtesting, and validating numerical implementations
against references.

**It is not a trading system.** It does not provide real-time pricing, order
management, or execution.

## Extending quantmathlab

Every new addition to the library must be:

1. Placed in the subpackage of `src/quantmathlab/` whose role it fits.
2. Documented, with docstrings and on its API page in `docs/modules/`.
3. Tested.
4. Preferably shown in an example in `examples/`.

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
