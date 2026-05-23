# CLI Reference

`trsproc` is called directly from the terminal. By default it operates on the
current working directory.

```bash
trsproc <command> [options]
```

Use `trsproc <command> --help` for detailed usage of any command.

## Quick reference

| Command | Description |
|---------|-------------|
| `txt` | Extract transcription text from TRS into .txt files |
| `trs` | Rewrite a TRS from a corrected .txt and a placeholder |
| `tsv` | Produce a TSV file with TRS structure and contents |
| `tg` | Convert TRS files to Praat TextGrid |
| `tgrs` | Convert TextGrid files to TRS |
| `vad` | Convert VAD TextGrid files to TRS |
| `cne` | Remove Named Entity annotations from TRS |
| `ne` | Extract Named Entity annotations into a TSV |
| `pne` | Pre-annotate Named Entities using an NE dictionary |
| `lang` | Add language tags to transcription segments |
| `prt` | Print parsed TRS contents to the console |
| `vsi` | Produce validation statistics TSV |
| `vsi-lang` | Produce language tag information TSV |
| `tmp` | Extract report sections into temporary TRS files |
| `rpt` | Produce section validation report |
| `rs` | Random segment sampling + validation GUI |
| `rsne` | Random NE segment sampling |
| `crt turn-differences` | Compare segmentation with twin TRS files |
| `crt empty-space` | Insert spaces before NE annotations |
| `crt la` | Correct "là" → "la" at segment ends |
| `crt maj` | Fix misplaced capital letters |

---

## Main commands

### `txt` — Extract text

```bash
trsproc txt [--folder PATH] [--file PATH]
```

Extracts the transcription text from `.trs` files into `.txt` files and creates
placeholder `.trs` files for later rewriting.

### `trs` — Rewrite TRS from text

```bash
trsproc trs [--folder PATH] [--file PATH]
```

Rewrites a TRS file using the input `.txt` file and a TRS-placeholder. Requires
a `txt/` and `placeholder/` subfolder (created by the `txt` command).

### `tsv` — Produce TSV

```bash
trsproc tsv [--folder PATH] [--file PATH]
```

Produces a tab-separated file with the structure and contents of the TRS files.

### `tg` — Convert to TextGrid

```bash
trsproc tg [--folder PATH] [--file PATH]
```

Converts `.trs` files to Praat `.TextGrid` files with transcription, speaker,
sex, and NE tiers.

### `tgrs` — Convert TextGrid to TRS

```bash
trsproc tgrs [--folder PATH] [--file PATH]
```

Converts `.TextGrid` files to `.trs` files. The TextGrid must contain
`transcription`, `speaker`, and optionally `sex` tiers.

### `vad` — Convert VAD TextGrid to TRS

```bash
trsproc vad [--folder PATH] [--file PATH]
```

Converts TextGrid files from a Voice Activity Detection algorithm into TRS files.
The TextGrid must contain a `VAD` tier with `speech`/`non-speech` labels.

### `cne` — Clean Named Entities

```bash
trsproc cne [--folder PATH] [--file PATH]
```

Removes Named Entity annotations from the TRS files. Output is written to a
`clean/` subdirectory.

### `ne` — Extract Named Entities

```bash
trsproc ne [--folder PATH] [--file PATH]
```

Extracts Named Entity annotations into `<corpus>_NE_extraction.tsv`.

### `pne` — Pre-annotate Named Entities

```bash
trsproc pne [--folder PATH] [--file PATH]
```

Pre-annotates Named Entities using the table created by the `ne` command as a
custom annotation dictionary. Output is written to a `preannotated/` subdirectory.

### `lang` — Add language tags

```bash
trsproc lang [--language CODE] [--json-dict PATH] [--folder PATH] [--file PATH]
```

Adds a language tag to each transcription segment that does not already have one.
The language can be specified with `--language` or via a JSON dictionary
(`--json-dict`, defaults to `lang-tag.json`). Output is written to a `lang/`
subdirectory.

### `vsi` — Validation statistics

```bash
trsproc vsi [--folder PATH] [--file PATH]
```

Produces a TSV file (`summary_validation-<corpus>.tsv`) with lexical information
and statistics for each TRS file.

### `vsi-lang` — Language tag statistics

```bash
trsproc vsi-lang [--folder PATH] [--file PATH]
```

Produces a TSV file (`summary_languages-<corpus>.tsv`) with language tag
information for each TRS file.

### `tmp` — Extract sections

```bash
trsproc tmp [--folder PATH] [--file PATH]
```

Extracts report sections from TRS files into temporary files in a `tmp/`
subdirectory.

### `rpt` — Section validation report

```bash
trsproc rpt [--folder PATH] [--file PATH]
```

Produces a validation report for report sections, listing speech segments with
duration ≥ 11 s and pauses with duration ≥ 0.6 s.

### `rs` — Random segment sampling + validation GUI

```bash
trsproc rs [--folder PATH] [--file PATH]
```

Calculates the minimum sample size for transcription validation, extracts random
segments, and launches the interactive validation GUI. If a validated TSV already
exists, resumes or offers to re-run.

### `rsne` — Random NE sampling

```bash
trsproc rsne [--folder PATH] [--file PATH]
```

Calculates the minimum sample size for NE validation and extracts random NE
segments with corresponding audio files.

---

## Correction commands (`crt`)

Corrections are accessed via the `crt` sub-command group:

```bash
trsproc crt <subcommand> [--folder PATH] [--file PATH]
```

### `crt turn-differences`

Searches for segmentation differences between the input TRS and its twin file
(located in a `twins/` subdirectory).

### `crt empty-space`

Inserts a space before each Named Entity annotation. Output is written to
`corrections/NE/`.

### `crt la`

Corrects sentences ending with "là" to "la". Requires running the `txt` command
first. Output is written to `corrections/la/`.

### `crt maj`

Fixes misplaced capital letters in TRS files. Output is written to
`corrections/maj/`.
