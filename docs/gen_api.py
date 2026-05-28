"""Generate API reference pages and site navigation from source docstrings.

This script is executed by mkdocs-gen-files during the build process.
It traverses the API_MODULES list, generates a .md page for each module
containing a mkdocstrings ``:::`` directive, and produces the site-wide
``SUMMARY.md`` for literate-nav.

To add a new module to the API docs, simply append it to API_MODULES.
The navigation entry in _API_NAV is derived automatically.
"""

import mkdocs_gen_files

# ---------------------------------------------------------------------------
# Module registry — single source of truth for AUTO-GENERATED API pages
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
# Navigation — defines the order and labels of ALL pages in the sidebar
# ---------------------------------------------------------------------------
# (display label, output filename or path relative to docs/)

_NAV_PAGES: list[tuple[str, str]] = [
    ("Home", "index.md"),
]

_NAV_SECTIONS: list[tuple[str, list[tuple[str, str]]]] = [
    (
        "Guide",
        [
            ("Getting Started", "getting-started.md"),
            ("CLI Reference", "cli-reference.md"),
            ("Conversion Guide", "conversion-guide.md"),
            ("Validation", "validation.md"),
        ],
    ),
    (
        "Reference",
        [
            ("TRS Format", "trs-format.md"),
        ],
    ),
    (
        "Development",
        [
            ("Architecture", "architecture.md"),
            ("Architecture Suggestion", "architecture-suggestion.md"),
            ("Deployment", "deployment.md"),
        ],
    ),
]

_API_NAV: list[tuple[str, str]] = [
    ("trsproc", "api/trsproc.md"),
    ("parser", "api/parser.md"),
    ("utils", "api/utils.md"),
    ("validation", "api/validation.md"),
]

# NOTE: _API_NAV labels and order are maintained manually so that the sidebar
# can use user-friendly names that differ from the module path.

# ---------------------------------------------------------------------------
# Source file mapping for "Edit on GitHub" links
# ---------------------------------------------------------------------------
_SRC_ROOT = "src/"


def _src_path(module_name: str) -> str:
    """Convert a dotted module name to its source file path."""
    return _SRC_ROOT + module_name.replace(".", "/") + ".py"


# ---------------------------------------------------------------------------
# Generate API pages (only for modules in API_MODULES)
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
    for label, path in _NAV_PAGES:
        f.write(f"* [{label}]({path})\n")
    for section_label, pages in _NAV_SECTIONS:
        f.write(f"* {section_label}\n")
        for label, path in pages:
            f.write(f"    * [{label}]({path})\n")
    f.write("* API\n")
    for label, path in _API_NAV:
        f.write(f"    * [{label}]({path})\n")
