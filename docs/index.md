# trsproc

*A Python library to process Transcriber TRS files.*

trsproc provides tools for parsing, converting, validating, and pre-annotating
[Transcriber](https://sourceforge.net/projects/trans/) TRS files used in speech
transcription workflows.

## Features

- **Parse TRS files** — Extract segments, speakers, language tags, named entities,
  and audio metadata via the [`TRSParser`](api/parser.md#trsproc.parser.TRSParser) class.
- **Convert formats** — TRS ↔ TextGrid, TRS → TXT/TSV, VAD TextGrid → TRS.
- **Validate transcriptions** — Statistical reports and an interactive
  [validation GUI](api/validation.md#trsproc.validation.gui.TranscriptionValidatorGUI) with audio playback.
- **Pre-annotate Named Entities** — Build and apply NE dictionaries to annotate TRS files.
- **Language tagging** — Add or remap language tags across segments.
- **Corrections** — Fix common issues (capitalisation, spacing, accented words,
  twin segmentation differences).
- **Random sampling** — Statistically sound segment and NE sampling for quality control.

## Quick start

Install with pip:

```bash
pip install trsproc
```

Process TRS files from the command line:

```bash
# Extract text from TRS files
trsproc txt

# Produce validation statistics
trsproc vsi

# Convert to TextGrid
trsproc tg

# Launch the validation GUI with random sampling
trsproc rs
```

Or use as a Python library:

```python
from trsproc.parser import TRSParser

trs = TRSParser("path/to/file.trs")
print(trs.contents[0]["totalWords"])
trs.trs_to_textgrid()
```

## Next steps

- :material-download: [Installation guide](installation.md)
- :material-console: [CLI reference](cli.md)
- :material-api: [API reference](api/trsproc.md)
