# Research

One folder per paper studied for the project. Reading a paper produces
three things, and the documentation publishes all of them under its
Research section:

```
research/<slug>/
├── README.rst       # documentation page summarising the paper
├── <slug>.py        # notebook with the numerical experiments
└── latex/
    └── main.tex     # notes with the derivations
```

Methods a paper needs are implemented in `src/quantmathlab/`, with tests,
and used from its notebook. Results quoted in the notes come from the
notebook, never typed in by hand.

## Adding a paper

1. Copy `placeholder/` to `research/<slug>/`, where `<slug>` is the paper's
   BibTeX key (`<surnames>_<year>_<word>`, e.g. `heston_1993_closed`).
2. Rename the notebook to `<slug>.py`. Notebook names must be unique across
   papers, or the documentation build fails.
3. Add the paper to `docs/references.bib` so the documentation page can cite
   it with `` :footcite:t:`<slug>` ``.
4. Build the documentation (`cd docs && make html`) and open the paper under
   Research.

Once the first real paper exists, delete `placeholder/`.

## The three parts

**Documentation page (`README.rst`).** reStructuredText, rendered as the
paper's page. Its title is the paper's entry in the navigation. Math uses
`:math:` and `.. math::`, and library objects are cross-referenced as in the
rest of the documentation.

**Notebook (`<slug>.py`).** A Python script in
[sphinx-gallery](https://sphinx-gallery.github.io/) format: a docstring with
a title, then cells separated by `# %%`, with text cells written as
comments. VS Code and Jupytext open it as a notebook, and the documentation
build executes it and shows its output and figures, with a download as
`.ipynb`. Every `.py` file directly inside the paper's folder is treated as
a notebook, so reusable code belongs in the library instead.

**Notes (`latex/main.tex`).** Compiled with `latexmk -pdf` during the
documentation build and embedded in the paper's Notes page. Keep any
`.bib`, figures and a `latexmkrc` (e.g. to switch to LuaLaTeX) inside
`latex/`. To compile on your own:

```bash
cd research/<slug>/latex
latexmk -pdf main.tex
```

Build artifacts and the PDF are gitignored.
