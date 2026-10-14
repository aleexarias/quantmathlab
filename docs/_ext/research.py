"""Publish the papers under ``research/`` in the Research section.

Every folder ``research/<slug>/`` that holds a ``README.rst`` is a paper.
Each paper becomes its own sphinx-gallery gallery, so the README is rendered
as the paper's page and the notebook ``<slug>.py`` is executed below it. The
LaTeX notes in ``latex/main.tex`` are compiled with latexmk and embedded in
a generated ``notes`` page that sits next to the notebook in the navigation.
"""

import os
import re
import shutil
import subprocess
from pathlib import Path

from sphinx.application import Sphinx
from sphinx.config import Config
from sphinx.util import logging

logger = logging.getLogger(__name__)

SECTION_TITLE = re.compile(
    r"^(?:([=\-~^\"'`#*+])\1+\n)?[^\n]+\n([=\-~^\"'`#*+])\2+\n", re.MULTILINE
)

# Error lines as printed by TeX with -file-line-error: "./main.tex:31: ..."
LATEX_ERROR = re.compile(r"^\S+:\d+: .*$", re.MULTILINE)

NOTES_TEMPLATE = """\
Notes
=====

.. raw:: html

   <iframe src="{slug}.pdf" title="Notes" style="width: 100%; height: 80vh;
   border: 1px solid var(--pst-color-border);"></iframe>

`Download the PDF <{slug}.pdf>`__, compiled from
``research/{slug}/latex/main.tex``.
"""

NOTES_FAILED_TEMPLATE = """\
Notes
=====

.. warning::

   ``research/{slug}/latex/main.tex`` could not be compiled. The
   documentation build log has the details.
"""


def _papers(app: Sphinx) -> list[Path]:
    root = Path(app.confdir, app.config.research_dir).resolve()
    if not root.is_dir():
        return []
    return sorted(
        path
        for path in root.iterdir()
        if path.is_dir() and (path / "README.rst").is_file()
    )


def _latex_dir(app: Sphinx, slug: str) -> Path:
    return Path(app.doctreedir, "research-latex", slug)


def _register_galleries(app: Sphinx, config: Config) -> None:
    gallery = config.sphinx_gallery_conf
    for paper in _papers(app):
        gallery["examples_dirs"].append(os.path.relpath(paper, app.confdir))
        gallery["gallery_dirs"].append(f"research/{paper.name}")


def _compile(tex: Path, outdir: Path) -> bool:
    latexmk = shutil.which("latexmk")
    if latexmk is None:
        logger.warning("latexmk not found, cannot compile %s", tex)
        return False
    outdir.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [
            latexmk,
            "-pdf",
            "-interaction=nonstopmode",
            "-halt-on-error",
            "-file-line-error",
            f"-outdir={outdir}",
            tex.name,
        ],
        cwd=tex.parent,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        errors = LATEX_ERROR.findall(result.stdout) or [result.stderr.strip()]
        logger.warning(
            "latexmk failed on %s:\n%s\nFull log: %s",
            tex,
            "\n".join(errors),
            outdir / f"{tex.stem}.log",
        )
        return False
    return True


def _write_if_changed(path: Path, content: str) -> None:
    if not path.is_file() or path.read_text() != content:
        path.write_text(content)


def _build_notes(app: Sphinx) -> None:
    for paper in _papers(app):
        slug = paper.name
        tex = paper / "latex" / "main.tex"
        if not tex.is_file():
            logger.warning("research paper %s has no latex/main.tex", slug)
            compiled = False
        else:
            compiled = _compile(tex, _latex_dir(app, slug))
        template = NOTES_TEMPLATE if compiled else NOTES_FAILED_TEMPLATE
        notes = Path(app.srcdir, "research", slug, "notes.rst")
        notes.parent.mkdir(parents=True, exist_ok=True)
        _write_if_changed(notes, template.format(slug=slug))


def _link_notes(app: Sphinx, docname: str, source: list[str]) -> None:
    parts = docname.split("/")
    is_paper_index = (
        len(parts) == 3 and parts[0] == "research" and parts[2] == "index"
    )
    if not (
        is_paper_index and Path(app.srcdir, *parts[:2], "notes.rst").is_file()
    ):
        return
    # Inserted right below the page title: a toctree above it would make
    # the notes a sibling of the paper in the navigation, and one at the end
    # would list them after the notebook.
    title = SECTION_TITLE.search(source[0])
    position = title.end() if title else len(source[0])
    toctree = "\n.. toctree::\n   :hidden:\n\n   notes\n\n"
    source[0] = source[0][:position] + toctree + source[0][position:]


def _copy_pdfs(app: Sphinx, exception: Exception | None) -> None:
    if exception is not None or app.builder.format != "html":
        return
    for paper in _papers(app):
        slug = paper.name
        pdf = _latex_dir(app, slug) / "main.pdf"
        if pdf.is_file():
            target = Path(app.outdir, "research", slug, f"{slug}.pdf")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(pdf, target)


def setup(app: Sphinx) -> dict[str, bool]:
    app.add_config_value("research_dir", "../research", "env")
    # sphinx-gallery fills in its configuration at priority 10 and builds
    # the galleries at the default 500; these hooks run before and after.
    app.connect("config-inited", _register_galleries, priority=5)
    app.connect("builder-inited", _build_notes, priority=600)
    app.connect("source-read", _link_notes)
    app.connect("build-finished", _copy_pdfs)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
