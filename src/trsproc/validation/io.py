#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validation I/O utilities for the trsproc GUI.

Provides dataclasses and helper functions for loading, manipulating, and
saving validation TSV files used by the :class:`TranscriptionValidatorGUI`.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

COL_FILE = "file_name"
COL_SEG = "segment_id"
COL_TRANS = "transcription"
COL_ERR_SEG = "nb_erreur_seg"
COL_ERR_TRANS = "nb_erreur_trans"
COL_VALIDATED = "validated"  # 0/1 completed marker
SUMMARY_MARKER = "TOTAL_SUM"


@dataclass(frozen=True)
class ValidationPaths:
    """Structured container for validation file paths.

    Attributes:
        input_path: Path to the input TSV file.
        audio_dir: Directory containing audio segment WAV files.
        output_path: Path where the validated TSV will be saved.
    """

    input_path: Path
    audio_dir: Path
    output_path: Path


def make_paths(tsv_path):
    """Resolve the input, audio, and output paths for a validation TSV.

    Args:
        tsv_path: Path to the sample segments TSV file.

    Returns:
        A :class:`ValidationPaths` instance with resolved paths.

    Raises:
        FileNotFoundError: If the TSV file does not exist.
    """
    input_path = Path(tsv_path)
    if not input_path.exists():
        raise FileNotFoundError(f"TSV not found: {input_path}")

    audio_dir = input_path.parent / "validation"

    if input_path.stem.endswith("_validated"):
        output_path = input_path
    else:
        output_path = input_path.with_name(
            input_path.stem + "_validated" + input_path.suffix
        )

    return ValidationPaths(
        input_path=input_path,
        audio_dir=audio_dir,
        output_path=output_path,
    )


def load_validation_tsv(input_path):
    """Load and normalize a validation TSV file into a DataFrame.

    Adds missing columns (``nb_erreur_seg``, ``nb_erreur_trans``, ``validated``)
    with default values and filters out the summary row.

    Args:
        input_path: Path to the validation TSV file.

    Returns:
        A normalized pandas DataFrame with segment data.

    Raises:
        KeyError: If any required column is missing from the TSV.
    """
    df = pd.read_csv(
        input_path,
        sep="\t",
        dtype={COL_FILE: str, COL_SEG: str},
    )

    if COL_TRANS not in df.columns and "transcript" in df.columns:
        df = df.rename(columns={"transcript": COL_TRANS})

    for col in (COL_FILE, COL_SEG, COL_TRANS):
        if col not in df.columns:
            raise KeyError(f"Missing required column: {col}")

    df = df[df[COL_FILE].astype(str) != SUMMARY_MARKER].copy()
    for col in (COL_ERR_SEG, COL_ERR_TRANS):
        if col not in df.columns:
            df[col] = 0

    df[COL_ERR_SEG] = (
        pd.to_numeric(df[COL_ERR_SEG], errors="coerce").fillna(0).astype(int)
    )
    df[COL_ERR_TRANS] = (
        pd.to_numeric(df[COL_ERR_TRANS], errors="coerce").fillna(0).astype(int)
    )

    if COL_VALIDATED not in df.columns:
        df[COL_VALIDATED] = 0
    df[COL_VALIDATED] = (
        pd.to_numeric(df[COL_VALIDATED], errors="coerce").fillna(0).astype(int)
    )
    df[COL_VALIDATED] = (df[COL_VALIDATED] != 0).astype(int)

    return df.reset_index(drop=True)


def compute_totals(df):
    """Compute the total segment and transcript error counts from a validated DataFrame.

    Args:
        df: The validated pandas DataFrame.

    Returns:
        A tuple of ``(total_segment_errors, total_transcript_errors)``.
    """

    return int(df[COL_ERR_SEG].sum()), int(df[COL_ERR_TRANS].sum())


def build_output_df_with_summary(df):
    """Append a ``TOTAL_SUM`` summary row to the validated DataFrame.

    Args:
        df: The validated pandas DataFrame.

    Returns:
        A new DataFrame with the summary row appended.
    """
    total_seg, total_trans = compute_totals(df)

    out = df.copy()
    summary = {col: "" for col in out.columns}
    summary[COL_FILE] = SUMMARY_MARKER
    summary[COL_SEG] = ""
    summary[COL_ERR_SEG] = total_seg
    summary[COL_ERR_TRANS] = total_trans

    return pd.concat([out, pd.DataFrame([summary])], ignore_index=True)


def save_validated_tsv_atomic(df, output_path):
    """Save the validated DataFrame to a TSV file atomically.

    Writes to a temporary file first, then replaces the original to avoid
    data corruption from partial writes.

    Args:
        df: The validated pandas DataFrame (without the summary row).
        output_path: Path where the validated TSV will be saved.
    """
    tmp_path = output_path.with_suffix(output_path.suffix + ".tmp")
    output_df = build_output_df_with_summary(df)
    output_df.to_csv(tmp_path, sep="\t", index=False)
    tmp_path.replace(output_path)

    return


def is_validation_complete(tsv_path):
    """Check whether all segments in the validation TSV have been validated.

    Args:
        tsv_path: Path to the validated TSV file.

    Returns:
        ``True`` if all segments have ``validated == 1``, ``False`` otherwise.
    """
    df = pd.read_csv(tsv_path, sep="\t")
    if COL_VALIDATED not in df.columns:
        return False

    return df[COL_VALIDATED].all()
