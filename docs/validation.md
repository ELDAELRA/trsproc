# Validation

*trsproc* provides tools for transcription quality validation through random sampling, audio segment extraction, and an interactive validation GUI.

## Overview

The validation workflow ensures transcription quality by:

1. **Sampling** — Selecting a statistically representative subset of segments
2. **Extracting** — Creating audio files for each sampled segment
3. **Validating** — Listening to audio and marking errors via the GUI
4. **Reporting** — Producing a validated TSV with error counts

## Random Sampling

### Transcription Validation (`rs` command)

```bash
trsproc rs
```

This command:

1. Prompts for the **population size** (total number of transcribed segments)
2. Calculates the **minimum sample size** using the formula:

$$n_0 = \frac{1.96^2 \times p(1-p)}{e^2} \div \left(1 + \frac{1.96^2 \times p(1-p)}{e^2 \times N}\right)$$

   Where: p = 0.5, e = 0.05 (95% confidence, 5% margin of error)

3. Prompts to confirm or adjust the sample size
4. Randomly samples segments and writes to a TSV file
5. Extracts corresponding audio segments
6. Launches the **Validation GUI**

### Named Entity Validation (`rsne` command)

```bash
trsproc rsne
```

Similar to `rs`, but samples named entities instead of raw transcription segments.

### Resuming Validation

If you run `rs` and a validated TSV already exists:

- **Incomplete validation**: The GUI resumes from where you left off
- **Complete validation**: You are prompted to re-run sampling or exit

## Validation GUI

The validation GUI is a PyQt6 desktop application for interactive audio transcription review.

### Launching

```bash
trsproc rs
```

The GUI launches automatically after sampling.

### Interface Layout
Add Image

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` | Play / Pause audio |
| `R` | Replay from start |
| `Enter` | Save current and move to next |
| `←` / `→` | Decrease / Increase segment error count |
| `↓` / `↑` | Decrease / Increase transcript error count |

### Workflow

1. Select a segment from the list (or use auto-navigation)
2. Listen to the audio
3. Count **segment errors** (e.g., wrong boundaries, missing speech)
4. Count **transcript errors** (e.g., typos, wrong words)
5. Press **Enter** to save and advance

### Unsaved Changes

If you navigate away from a segment with unsaved changes, the GUI prompts:

- **Yes** — Save changes before navigating
- **No** — Discard changes
- **Cancel** — Stay on the current segment

### Completion

When all segments are validated:

- A summary dialog shows total error counts
- You are offered the option to **clean up** (delete the extracted audio segments)
- The validated TSV is saved with a `_validated` suffix

## Output Files

### Sample TSV (`sample_segments_<N>.tsv`)

| Column | Description |
|--------|-------------|
| `file_name` | TRS filename |
| `segment_start` | Segment start time |
| `transcription` | Transcription text |
| `segment_end` | Segment end time |
| `segment_duration` | Duration |
| `segment_id` | Segment number |
| `nb_tokens` | Token count |
| `speaker_name` | Speaker name |
| `speaker_sex` | Speaker gender |
| `SNR` | Signal-to-noise ratio |

### Validated TSV (`sample_segments_<N>_validated.tsv`)

Includes all sample TSV columns plus:

| Column | Description |
|--------|-------------|
| `nb_erreur_seg` | Number of segment errors |
| `nb_erreur_trans` | Number of transcript errors |
| `validated` | Validation status (0 or 1) |

A summary row with `file_name = "TOTAL_SUM"` is appended with total error counts.

### Audio Segments (`validation/` folder)

Individual WAV files named `<filename>_<segment_id>.wav`, one per sampled segment.

## Statistics & Reports

### Validation Statistics (`vsi` command)

```bash
trsproc vsi
```

Produces `summary_validation-<corpus>.tsv` with:

| Column | Description |
|--------|-------------|
| `file_name` | TRS filename |
| `file_path` | Directory path |
| `nb_spk` | Number of speakers |
| `nb_lang` | Number of languages |
| `dur_tot` | Total duration |
| `dur_trans` | Transcribed duration |
| `dur_nontrans` | Non-transcribed duration |
| `nb_seg` | Total segments |
| `nb_trans` | Transcribed segments |
| `nb_nontrans` | Non-transcribed segments |
| `nb_pronpi` | Pronunciation uncertainty marks |
| `nb_words` | Total word count |
| `nb_NE` | Named entity count |
| `mean_SNR` | Mean signal-to-noise ratio |

### Report (`rpt` command)

```bash
trsproc rpt
```

Combines `tmp` and `vsi` operations, plus identifies quality issues:

- **Pause segments** longer than 0.5s
- **Speech segments** shorter than 10s

Output: `tmp/summary_report-<corpus>.tsv`

### Language Statistics (`vsi-lang` command)

```bash
trsproc vsi-lang
```

Produces `summary_languages-<corpus>.tsv` with language tag information per segment.
