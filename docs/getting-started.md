# Getting Started

## Requirements

- **Python 3.10** or higher
- An audio file (`.wav` by default) corresponding to each TRS file for SNR computation and segment extraction

## Installation

=== "pip"

    ```bash
    pip install trsproc
    ```

=== "uv"

    ```bash
    # Install into the current environment
    uv pip install trsproc

    # Or add to a managed project
    uv add trsproc
    ```

### From Source

=== "pip"

    ```bash
    git clone https://github.com/ELDAELRA/trsproc.git
    cd trsproc
    pip install -e .
    ```

=== "uv"

    ```bash
    git clone https://github.com/ELDAELRA/trsproc.git
    cd trsproc
    uv sync
    ```

### Optional Dependencies

=== "pip"

    | Task | Install command |
    |------|----------------|
    | Running tests & linting | `pip install trsproc[dev]` |
    | Building docs | `pip install trsproc[docs]` |

=== "uv"

    | Task | Install command |
    |------|----------------|
    | Running tests & linting | `uv sync --extra dev` |
    | Building docs | `uv sync --extra docs` |

### Verifying the Installation

```bash
trsproc --help
```

This should display the list of available commands.

## Basic Usage

### From the Command Line

*trsproc* can be called directly from the terminal. By default, it processes TRS files in the current directory.

```bash
trsproc <command> [folder] [--options]
```

For a full list of commands:

```bash
trsproc --help
```

### As a Python Module

Import the core parser class:

```python
from trsproc.parser import TRSParser
```

Create a parser instance for a TRS file:

```python
trs = TRSParser("my_transcription.trs")
```

The parser automatically:

1. Parses the XML tree
2. Extracts speaker information
3. Computes section and audio durations
4. Builds the `contents` dictionary with segment-level detail

#### Key Attributes

| Attribute | Description |
|-----------|-------------|
| `trs.tree` | Parsed XML tree |
| `trs.root` | Root element of the XML tree |
| `trs.input_trs` | Full path to the TRS file |
| `trs.filepath` | Directory containing the TRS file |
| `trs.filename` | TRS filename (without extension) |
| `trs.corpus` | Name of the folder containing the TRS |
| `trs.lang` | Language mode (`"eu"` for word count, `"jkz"` for character count) |
| `trs.section_duration` | Total duration of all sections |
| `trs.file_duration` | Duration of the corresponding audio file |
| `trs.speakers` | Dictionary mapping speaker IDs to `(name, sex)` tuples |
| `trs.contents` | Complete parsed contents (segments, NE, statistics) |

#### Quick Operations

```python
# Print all parsed contents
trs.print()

# Convert to TextGrid
trs.trs_to_textgrid()

# Extract text to .txt (creates placeholder .trs)
trs.trs_to_txt()

# Generate validation statistics
trs.validate_trs()

# Extract named entities to TSV
trs.retrieve_ne_to_tsv()

# Create a temporary TRS with only "report" sections
trs.trs_tmp(section_type="report")
```

## Common Workflows

### Editing Transcription Text

1. Extract text and create placeholder:
   ```bash
   trsproc txt
   ```
2. Edit the `.txt` file in `txt/` subfolder
3. Merge edited text back into TRS structure:
   ```bash
   trsproc trs
   ```

### Converting Formats

```bash
# TRS → TextGrid
trsproc tg

# TextGrid → TRS
trsproc tgrs

# VAD TextGrid → TRS
trsproc vad
```

See the [Conversion Guide](conversion-guide.md) for detailed format conversion instructions.

### Named Entity Workflow

```bash
# 1. Extract NE annotations to TSV
trsproc ne

# 2. Pre-annotate new TRS files using the extracted NE dictionary
trsproc pne

# 3. Clean NE annotations from TRS
trsproc cne
```

### Validation Workflow

```bash
# Random sampling + GUI validation
trsproc rs
```

See the [Validation](validation.md) page for more on validation features.

## Building the Documentation

To build and preview the documentation locally:

=== "pip"

    ```bash
    pip install trsproc[docs]
    mkdocs serve
    ```

=== "uv"

    ```bash
    uv sync --extra docs
    mkdocs serve
    ```

The site will be available at `http://127.0.0.1:8000`.
