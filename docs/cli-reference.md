# CLI Reference

*trsproc* provides a command-line interface with multiple commands for processing TRS files.

## General Usage

```bash
trsproc <command> [folder] [--options]
```

By default, commands process all `.trs` files in the current directory. Use the `--file` option to process a single file, or provide a folder path as a positional argument.

To display help:

```bash
trsproc --help
trsproc <command> --help
```

To check the installed version:

```bash
trsproc --version
```

## Common Options

Most commands share these arguments:

| Option | Description |
|--------|-------------|
| `[folder]` | Target directory (defaults to current directory) |
| `--file <path>` | Process a single file instead of a whole folder |

## Format Conversion

### `tg` — Convert to TextGrid

Convert TRS files to Praat TextGrid files.

```bash
trsproc tg [folder] [--file path]
```

The resulting TextGrid has four tiers: `transcription`, `speaker`, `sex`, and `NE`.

**Output**: `.TextGrid` files in the input folder.

See [Conversion Guide → TRS → TextGrid](conversion-guide.md#trs-textgrid) for details.

### `tgrs` — Convert TextGrid to TRS

Convert Praat TextGrid files to TRS files.

```bash
trsproc tgrs [folder] [--file path]
```

The TextGrid must contain `speaker`, `transcription`, and `sex` tiers.

**Output**: `.trs` files in the input folder.

See [Conversion Guide → TextGrid → TRS](conversion-guide.md#textgrid-trs) for details.

### `vad` — Convert VAD TextGrid to TRS

Convert TextGrid files produced by a Voice Activity Detection (VAD) algorithm into TRS files.

```bash
trsproc vad [folder] [--file path]
```

The TextGrid must have a single tier named `"VAD"` with intervals labeled `"speech"` or `"non-speech"`.

**Output**: `.trs` files in the input folder with empty transcriptions for speech segments and `[nontrans]` for non-speech segments.

See [Conversion Guide → VAD TextGrid → TRS](conversion-guide.md#vad-textgrid-trs) for details.

### `tsv` — Export to TSV

Produce a tab-separated file with the structure and contents of TRS files.

```bash
trsproc tsv [folder] [--file path]
```

**Output**: `<corpus>.tsv` in the input folder, with columns for file name, path, segment, start/end times, duration, transcription, speaker, and speaker sex.

See [Conversion Guide → TRS → TSV](conversion-guide.md#trs-tsv) for output column details.

## Text Editing

### `txt` — Extract Text

Extract transcription text from TRS files into `.txt` files and create placeholder `.trs` files.

```bash
trsproc txt [folder] [--file path]
```

**Output**:

- `txt/<filename>.txt` — Plain text transcription (one segment per line)
- `placeholder/<filename>_placeholder.trs` — TRS structure with `[placeholder N]` replacing text

Use this command together with [`trs`](#trs-rewrite-trs) for a text-editing workflow: extract → edit → rewrite.

See [Conversion Guide → TRS → TXT](conversion-guide.md#trs-txt-text-editing-workflow) for details.

### `trs` — Rewrite TRS

Rewrite a TRS file using the content of a `.txt` file and the structure of a placeholder `.trs` file.

```bash
trsproc trs [folder] [--file path]
```

**Prerequisites**: Run `trsproc txt` first to generate the `.txt` and placeholder files. The command must be called from a folder that has `txt/` and `placeholder/` subfolders.

**Output**: Rewritten `.trs` file in the `txt/` folder.

### `prt` — Print Contents

Print the parsed TRS contents directly in the console.

```bash
trsproc prt [folder] [--file path]
```

Useful for quick inspection of a TRS file's parsed structure.

## Named Entity Operations

### `ne` — Extract Named Entities

Extract Named Entity annotations from TRS files into a tabular file.

```bash
trsproc ne [folder] [--file path]
```

**Output**: `<corpus>_NE_extraction.tsv` with columns for file name, path, NE rank, class, content, segment info, and speaker details.

See [Conversion Guide → Extract NE → TSV](conversion-guide.md#extract-ne-tsv) for output column details.

### `pne` — Pre-Annotate Named Entities

Pre-annotate TRS files using a previously created NE extraction table as a custom annotation dictionary.

```bash
trsproc pne [folder] [--file path]
```

The command looks for `<corpus>_NE-extraction.tsv` in the input folder to build or update an NE dictionary (`<corpus>_NE-reference.json`), then applies it to annotate the TRS files.

**Output**: Pre-annotated `.trs` files in a `preannotated/` subfolder.

### `cne` — Clean Named Entities

Delete Named Entity annotations from TRS files.

```bash
trsproc cne [folder] [--file path]
```

**Output**: Cleaned `.trs` files in a `clean/` subfolder, with all `<Event type="entities">` tags removed and resulting whitespace corrected.

See [Conversion Guide → Clean NE](conversion-guide.md#clean-ne) for details.

### `lang` — Add Language Tags

Add a language tag to each transcription segment that does not have one. Also modifies existing language tags using a JSON dictionary.

```bash
trsproc lang [folder] [--language code] [--json-dict path] [--file path]
```

| Option | Description |
|--------|-------------|
| `--language` | Language code to add (e.g., `fr`, `en`) |
| `--json-dict` | Path to a JSON file mapping old language codes to new ones (default: `lang-tag.json` in the current directory) |

Either `--language` or a valid `--json-dict` file must be provided.

**Output**: `.trs` files with language tags in a `lang/` subfolder.

See [Conversion Guide → Language Tagging](conversion-guide.md#language-tagging) for details.

## Validation & Statistics

### `vsi` — Validation Statistics

Produce a tabular file containing basic lexical information and statistics about the input TRS files.

```bash
trsproc vsi [folder] [--file path]
```

**Output**: `summary_validation-<corpus>.tsv` with columns for file name, path, speaker count, language count, durations, segment counts, word count, NE count, and mean SNR.

See [Validation](validation.md) for more details.

### `vsi-lang` — Language Statistics

Produce a tabular file containing information about the language tags present in the input TRS files.

```bash
trsproc vsi-lang [folder] [--file path]
```

**Output**: `summary_languages-<corpus>.tsv` with language tag details per segment.


### `rpt` — Report

Perform the operations of the `tmp` and `vsi` commands to obtain basic elements for data validation. An additional report is produced with pause segments longer than 0.5s and speech segments shorter than 10s.

```bash
trsproc rpt [folder] [--file path]
```

**Output**: Validation report TSV in the `tmp/` subfolder.

### `rs` — Random Sampling (Transcription)

Calculate the minimum sample needed for transcription validation and extract random segments (audio and text).

```bash
trsproc rs [folder] [--file path]
```

The command:

1. Prompts for population size
2. Calculates the minimum sample size (95% confidence, 5% margin of error)
3. Extracts random segments to a TSV file
4. Extracts corresponding audio segments
5. Launches the **Validation GUI** for interactive review

If a validated TSV already exists:

- **Incomplete validation** — automatically resumes from where you left off
- **Complete validation** — prompts whether to re-run the sampling

**Output**:

- `sample_segments_<N>.tsv` — Sampled segments
- `validation/` — Audio segment files
- `sample_segments_<N>_validated.tsv` — Validated results

See [Validation](validation.md) for more on the validation workflow.

### `rsne` — Random Sampling (Named Entities)

Calculate the minimum sample needed for Named Entity validation and extract random NE segments.

```bash
trsproc rsne [folder] [--file path]
```

**Output**: `sample_ne_<N>.tsv` with sampled named entities and corresponding audio segments.

### `tmp` — Extract Report Sections

Create temporary TRS files retaining only the target section content.

```bash
trsproc tmp [folder] [--file path]
```

By default, extracts only `"report"` sections.

**Output**: Partial TRS files in a `tmp/` subfolder.

See [Conversion Guide → Section Extraction](conversion-guide.md#section-extraction) for the intended usage.

## Correction Commands (`crt`)

The `crt` sub-command group provides specific correction operations.

```bash
trsproc crt <subcommand> [folder] [--file path]
```

### `crt turn-differences`

Search for differences in segmentation between the input TRS and its twin file (located in a `twins/` subfolder).

```bash
trsproc crt turn-differences [folder] [--file path]
```

Prints segment start/end time differences to the console.

### `crt empty-space`

Add an empty space before each NE annotation in the TRS file.

```bash
trsproc crt empty-space [folder] [--file path]
```

**Output**: Corrected `.trs` files in `corrections/NE/` subfolder.

### `crt la`

Correct sentences ending with `"là"` to `"la"`. Requires running the `txt` command first.

```bash
trsproc crt la [folder] [--file path]
```

**Output**: Corrected `.txt` files in `corrections/la/` subfolder.

### `crt maj`

Correct misplaced capital letters in TRS files.

```bash
trsproc crt maj [folder] [--file path]
```

NE entity text is capitalized; other text is lowercased at the start of lines.

**Output**: Corrected `.trs` files in `corrections/maj/` subfolder.
