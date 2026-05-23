# Installation

## Requirements

- **Python** 3.6 or higher
- An audio backend compatible with [Praat](https://www.fon.hum.uva.nl/praat/) (via
  `praat-parselmouth`) for SNR computation and segment extraction.

## Install

```bash
pip install trsproc
```

## Optional dependencies

All runtime dependencies are installed automatically. The following are only
needed for specific development tasks:

| Task | Install command |
|------|----------------|
| Running tests | `pip install trsproc[dev]` |
| Building docs | `pip install -r docs/requirements.txt` |

!!! note "Documentation build requires Python >= 3.8"

    The documentation toolchain (mkdocs-material 9.x) requires Python 3.8+.
    This does **not** affect the package itself, which supports Python 3.6+.

## Verifying the installation

```bash
trsproc --help
```

This should display the list of available commands.
