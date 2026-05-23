"""Generate API reference pages and site navigation from source docstrings.

This script is executed by mkdocs-gen-files during the build process.
It traverses the API_MODULES list, generates a .md page for each module
containing a mkdocstrings ``:::`` directive, and produces the site-wide
``SUMMARY.md`` for literate-nav.

To add a new module to the API docs, simply append it to API_MODULES
and update the _API_NAV list.
"""

import mkdocs_gen_files

# ---------------------------------------------------------------------------
# Module registry — single source of truth for API pages
# ---------------------------------------------------------------------------
# (fully qualified module name, output filename under api/)
# Use None for the filename to merge into another page (e.g. validation.gui).

API_MODULES: list[tuple[str, str | None]] = [
    ("trsproc", "trsproc.md"),
    ("trsproc.parser", "parser.md"),
    ("trsproc.utils", "utils.md"),
    ("trsproc.validation.io", "validation.md"),
    ("trsproc.validation.gui", None),  # merged into validation.md
]

# Map of output filename → list of module names (for merged pages)
_PAGE_MODULES: dict[str, list[str]] = {}
for _mod, _fname in API_MODULES:
    if _fname is not None:
        _PAGE_MODULES.setdefault(_fname, []).append(_mod)

# ---------------------------------------------------------------------------
# Navigation — defines the order and labels of API pages in the sidebar
# ---------------------------------------------------------------------------
# (display label, output filename under api/)
_API_NAV: list[tuple[str, str]] = [
    ("trsproc", "trsproc.md"),
    ("parser", "parser.md"),
    ("utils", "utils.md"),
    ("validation", "validation.md"),
]

# ---------------------------------------------------------------------------
# Source file mapping for "Edit on GitHub" links
# ---------------------------------------------------------------------------
_SRC_ROOT = "src/"


def _src_path(module_name: str) -> str:
    """Convert a dotted module name to its source file path."""
    return _SRC_ROOT + module_name.replace(".", "/") + ".py"


# ---------------------------------------------------------------------------
# Generate API pages
# ---------------------------------------------------------------------------
for filename, modules in _PAGE_MODULES.items():
    full_path = f"api/{filename}"

    with mkdocs_gen_files.open(full_path, "w") as f:
        for mod in modules:
            f.write(f"::: {mod}\n\n")

    # Set edit path to the first module's source file
    mkdocs_gen_files.set_edit_path(full_path, _src_path(modules[0]))

# ---------------------------------------------------------------------------
# Generate SUMMARY.md for literate-nav
# ---------------------------------------------------------------------------
with mkdocs_gen_files.open("SUMMARY.md", "w") as f:
    f.write("* [Home](index.md)\n")
    f.write("* [Installation](installation.md)\n")
    f.write("* [CLI Reference](cli.md)\n")
    f.write("* [Deployment](deployment.md)\n")
    f.write("* API Reference\n")
    for label, filename in _API_NAV:
        f.write(f"    * [{label}](api/{filename})\n")
