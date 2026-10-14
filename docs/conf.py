"""Sphinx configuration for quantmathlab documentation."""

import os
import sys

# Add source directory and local extensions to path
sys.path.insert(0, os.path.abspath("../src"))
sys.path.insert(0, os.path.abspath("_ext"))

from quantmathlab import __version__  # noqa: E402

project = "quantmathlab"
copyright = "2026, Alejandro Arias Gomez"
author = "Alejandro Arias Gomez"

# Derived from quantmathlab.__version__; do not hardcode. Sphinx exposes
# these as the |release| and |version| substitutions, usable in any page.
release = __version__
version = ".".join(release.split(".")[:2])

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx_gallery.gen_gallery",
    "sphinxcontrib.bibtex",
    "research",
]

autosummary_generate = True
autosummary_generate_overwrite = False
autodoc_typehints = "description"
autodoc_member_order = "bysource"

# Numpydoc configuration
napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_use_param = True
napoleon_use_rtype = True

# sphinx-gallery configuration. The research extension appends one gallery
# per paper in ../research, rendered under docs/research/<slug>/; every
# notebook there is executed, alongside the plot_* scripts in ../examples.
sphinx_gallery_conf = {
    "examples_dirs": ["../examples"],
    "gallery_dirs": ["auto_examples"],
    "filename_pattern": r"[\\/](plot_|research[\\/])",
    "plot_gallery": True,
    "download_all_examples": False,
    "abort_on_example_error": False,
    "backreferences_dir": None,
    "doc_module": ("quantmathlab",),
    "reference_url": {"quantmathlab": None},
    "show_memory": False,
    "junit": "",
    "reset_modules": ("matplotlib", "seaborn"),
    "first_notebook_cell": None,
    "last_notebook_cell": None,
    "notebook_images": False,
}

# BibTeX configuration
bibtex_bibfiles = ["references.bib"]

# Theme
html_theme = "pydata_sphinx_theme"
html_theme_options = {
    "github_url": "https://github.com/aleexarias/quantmathlab",
    "logo": {
        "image_light": "_static/logo_light.svg",
        "image_dark": "_static/logo_dark.svg",
        "alt_text": "quantmathlab - Home",
    },
    "show_nav_level": 2,
    # _templates/version.html renders `release` into the footer of every page.
    "footer_start": ["version", "copyright"],
    "footer_end": ["last-updated"],
}

html_static_path = ["_static"]
# Follows the browser's colour scheme, so it stays visible on light and dark
# tab bars; keep its paths in sync with the logo_*.svg files.
html_favicon = "_static/favicon.svg"

templates_path = ["_templates"]
source_suffix = ".rst"
master_doc = "index"

exclude_patterns = ["_build", ".ipynb_checkpoints"]

# Output
html_use_smartypants = True
html_last_updated_fmt = "%b %d, %Y"
html_show_sourcelink = True
html_show_sphinx = False

# Warnings
suppress_warnings = ["app.add_config_value"]
