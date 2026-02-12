# -*- coding: utf-8 -*-
#!/usr/bin/env python3
#
##
### ELDA-R&D-2023
#### Gabriele CHIGNOLI
#####

from pathlib import Path
from typing import Annotated, Optional, Callable

import typer
from rich.console import Console

from trsproc import parser, utils
from trsproc.parser import TRSParser


app = typer.Typer()


def get_files(
    folder: Optional[Path],
    file: Optional[Path],
    extension: str,
) -> list[Path]:
    # TODO : handle cases where user gives both folder and file (without breaking the default folder behaviour)
    if file:
        if not file.exists():
            raise typer.BadParameter(f"File not found : {file}")
        return [file]

    if folder:
        if not folder.is_dir():
            raise typer.BadParameter(f"Not a directory : {folder}")
        return list(folder.glob(f"*.{extension}"))

    return list(Path.cwd().glob(f"*.{extension}"))


@app.command(short_help="Extracts the text from .trs files into .txt files")
def txt(
    folder: Annotated[
        Path,
        typer.Argument(help="The folder containing the .trs files"),
    ] = Path.cwd(),
    file: Annotated[
        Optional[Path],
        typer.Option(help="A single file to process instead of a whole folder"),
    ] = None,
) -> None:
    """Extracts the text from .trs files into .txt files, and creates placeholder .trs files, to merge text back in.
    This is intended to be used for easily modifying the text from .trs files (e.g for fixing typos)."""
    files: list[Path] = get_files(folder, file, "trs")
    for filename in files:
        trs_parser = TRSParser(filename)
        trs_parser.trs_to_txt()


@app.command(short_help="Rewrites trs files in the placeholder .trs files.")
def trs(
    folder: Annotated[
        Path,
        typer.Argument(help="The folder containing the .txt files"),
    ] = Path.cwd() / "txt",
    file: Annotated[
        Optional[Path],
        typer.Option(help="A single file to process instead of a whole folder"),
    ] = None,
):
    """rewrites a TRS file using the input txt file and a TRS-placeholder placed in a subfolder of the parent input folder.
    The rewritten TRS will have the content of the txt and the structure of the TRS-placeholder."""
    files: list[Path] = get_files(folder, file, "txt")
    for filename in files:
        parser.txt_to_trs(filename)


@app.command(
    short_help="Produces a tabular file with the structures and contents of the .trs files"
)
def tsv(
    folder: Annotated[
        Path,
        typer.Argument(help="The folder containing the .trs files"),
    ] = Path.cwd(),
    file: Annotated[
        Optional[Path],
        typer.Option(help="A single file to process instead of a whole folder"),
    ] = None,
):
    """Produces a tabular file with the structures and contents of the .trs files.
    The resulting .tsv file will be located in [folder]/[folder].tsv"""
    files: list[Path] = get_files(folder, file, "trs")
    for filename in files:
        trs_parser = TRSParser(filename)
        trs_parser.trs_to_tsv()


@app.command(
    short_help="Deletes the Named Entity annotations if any are present in the input TRS."
)
def cne(
    folder: Annotated[
        Path,
        typer.Argument(help="The folder containing the .trs files"),
    ] = Path.cwd(),
    file: Annotated[
        Optional[Path],
        typer.Option(help="A single file to process instead of a whole folder"),
    ] = None,
):
    """Deletes the Named Entity annotations if any are present in the input TRS.
    Writes the resulting .trs files in [folder]/clean"""
    files: list[Path] = get_files(folder, file, "trs")
    for filename in files:
        trs_parser = TRSParser(filename)
        trs_parser.clean_ne_from_trs()


@app.command(
    short_help="Extracts the Named Entity annotations if any are present in the input TRS files."
)
def ne(
    folder: Annotated[
        Path,
        typer.Argument(help="The folder containing the .trs files"),
    ] = Path.cwd(),
    file: Annotated[
        Optional[Path],
        typer.Option(help="A single file to process instead of a whole folder"),
    ] = None,
):
    """Extracts the Named Entity annotations if any are present in the input TRS.
    Saves them in a tabular file located in [folder]/folder_NE_extraction.tsv"""
    files: list[Path] = get_files(folder, file, "trs")
    for filename in files:
        trs_parser = TRSParser(filename)
        trs_parser.retrieve_ne_to_tsv()
console = Console()


def main():
    app()


if __name__ == "__main__":
    main()
