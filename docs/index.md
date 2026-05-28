# trsproc

A Python library for processing [Transcriber](https://sourceforge.net/projects/trans/) TRS files — the XML format used for speech transcription, speaker annotation, named entity labeling, and language tagging.

## Features

- **Parse & Inspect** — Convert TRS files into structured Python objects with segment-level detail
- **Format Conversion** — Convert between TRS ↔ Praat TextGrid, generate TRS from VAD output
- **Named Entity Annotation** — Extract, pre-annotate, and clean NE labels
- **Language Tagging** — Add or modify language tags on transcription segments
- **Transcription Validation** — Random sampling, audio extraction, and a PyQt6 validation GUI
- **Text Editing Workflow** — Extract text to `.txt`, edit, and merge back into TRS structure
- **Statistics & Reports** — Generate TSV reports with lexical stats, SNR, and quality checks
- **Custom Corrections** — Fix segmentation differences, misplaced capitals, spacing, and more

## Quick Start

Install:

```bash
pip install trsproc
```

Parse a TRS file:

```python
from trsproc.parser import TRSParser

trs = TRSParser("interview.trs")

# Speaker information
print(trs.speakers)
# {'spk1': ('Alice', 'female'), 'spk2': ('Bob', 'male')}

# Overall statistics
stats = trs.contents[0]
print(f"Segments: {stats['totalSegments']}, Words: {stats['totalWords']}")
```

Use the CLI:

```bash
trsproc txt          # Extract text from TRS
trsproc tg           # Convert TRS to TextGrid
trsproc lang -l fr   # Add language tags
trsproc rs           # Validate transcriptions (with GUI)
```

See [Getting Started](getting-started.md) for detailed installation and usage instructions, or [CLI Reference](cli-reference.md) for the full command list.

## License

[MIT License](https://github.com/ELDAELRA/trsproc/blob/main/LICENSE)
