# -*- coding: utf-8 -*-
#!/usr/bin/env python3
#
##

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

COL_FILE = "file_name"
COL_SEG = "segment_id"
COL_TRANS = "transcription"
COL_ERR_SEG = "nb_erreur_seg"
COL_ERR_TRANS = "nb_erreur_trans"
COL_VALIDATED = "validated"          # 0/1 completed marker
SUMMARY_MARKER = "TOTAL_SUM"


@dataclass(frozen=True)
class ValidationPaths:
    input_path: Path
    audio_dir: Path
    output_path: Path


def make_paths(tsv_path):
    """
    >_ TSV file path
    >>> ValidationPaths with input, audio and output paths
    """
    input_path = Path(tsv_path)
    if not input_path.exists():
        raise FileNotFoundError(f"TSV not found: {input_path}")

    audio_dir = input_path.parent / "validation"

    if input_path.stem.endswith("_validated"):
        output_path = input_path
    else:
        output_path = input_path.with_name(input_path.stem + "_validated" + input_path.suffix)

    return ValidationPaths(
        input_path=input_path,
        audio_dir=audio_dir,
        output_path=output_path,
    )


def load_validation_tsv(input_path):
    """
    >_ validation TSV file
    >>> normalized dataframe with segment data
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

    df[COL_ERR_SEG] = pd.to_numeric(df[COL_ERR_SEG], errors="coerce").fillna(0).astype(int)
    df[COL_ERR_TRANS] = pd.to_numeric(df[COL_ERR_TRANS], errors="coerce").fillna(0).astype(int)

    if COL_VALIDATED not in df.columns:
        df[COL_VALIDATED] = 0
    df[COL_VALIDATED] = pd.to_numeric(df[COL_VALIDATED], errors="coerce").fillna(0).astype(int)
    df[COL_VALIDATED] = (df[COL_VALIDATED] != 0).astype(int)

    return df.reset_index(drop=True)


def compute_totals(df):
    """
    >_ validated dataframe
    >>> total segment and transcript error counts
    """
    
    return int(df[COL_ERR_SEG].sum()), int(df[COL_ERR_TRANS].sum())


def build_output_df_with_summary(df):
    """
    >_ validated dataframe
    >>> dataframe with TOTAL_SUM summary row appended
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
    """
    >_ validated dataframe and output path
    >>>  TSV file saved atomically to disk (write to tmp, then replace)
    """
    tmp_path = output_path.with_suffix(output_path.suffix + ".tmp")
    output_df = build_output_df_with_summary(df)
    output_df.to_csv(tmp_path, sep="\t", index=False)
    tmp_path.replace(output_path)

    return


def is_validation_complete(tsv_path):
    """
    >_ validated TSV file path
    >>> True if all segments have been validated
    """
    df = pd.read_csv(tsv_path, sep="\t")
    if COL_VALIDATED not in df.columns:
        return False
    
    return df[COL_VALIDATED].all()