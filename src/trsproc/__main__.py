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


@app.command(
    short_help="Adds a language tag to each transcription segment not having one in the input TRS files"
)
def lang(
    language: Annotated[
        str,
        typer.Option(help="The language to use for the tags."),
    ],
    folder: Annotated[
        Path,
        typer.Argument(help="The folder containing the .trs files"),
    ] = Path.cwd(),
    file: Annotated[
        Optional[Path],
        typer.Option(help="A single file to process instead of a whole folder"),
    ] = None,
    json_dict: Annotated[
        Path,
        typer.Option(
            help="The json file containing the language tags to add."
        ),  # TODO: describe the expected format
    ] = Path.cwd() / "lang-tag.json",
):  # TODO: refactor utils.add_lang_tag. Right now, the language tag is required even if a json file is provided.
    """Adds a language tag to each transcription segment not having one in the input TRS files.
    The language can either be specified with the `--language` option, or within a json file, which can be specified with the --json-dict option (which defaults to [folder]/lang-tag.json)
    The resulting .trs files will be written in [folder]/lang"""
    files: list[Path] = get_files(folder, file, "trs")
    for filename in files:
        trs_parser = TRSParser(filename)
        utils.add_lang_tag(trs_parser, json_dict, language)


@app.command()
def prt(
    folder: Annotated[
        Path,
        typer.Argument(help="The folder containing the .trs files"),
    ] = Path.cwd(),
    file: Annotated[
        Optional[Path],
        typer.Option(help="A single file to process instead of a whole folder"),
    ] = None,
) -> None:
    """Prints the parsed trs contents directly in the console"""
    files: list[Path] = get_files(folder, file, "trs")
    for filename in files:
        trs_parser = TRSParser(filename)
        trs_parser.print()


@app.command()
def pne(
    folder: Annotated[
        Path,
        typer.Argument(help="The folder containing the .trs files"),
    ] = Path.cwd(),
    file: Annotated[
        Optional[Path],
        typer.Option(help="A single file to process instead of a whole folder"),
    ] = None,
) -> None:  # TODO: Get a pre-annotation json file to understand and test the utils.pre_annotate function, and add the required tsv and json files as arguments.
    """Pre-annotates the input TRS using the table created in the `-ne` flag as a custom annotation dictionnary"""
    files: list[Path] = get_files(folder, file, "trs")
    for filename in files:
        trs_parser = TRSParser(filename)
        utils.trs_preannotation(trs_parser)


@app.command(short_help="Extracts report sections from .trs files")
def tmp(
    folder: Annotated[
        Path,
        typer.Argument(help="The folder containing the .trs files"),
    ] = Path.cwd(),
    file: Annotated[
        Optional[Path],
        typer.Option(help="A single file to process instead of a whole folder"),
    ] = None,
) -> None:  # FIXME: The tmp command was broken in commit 30c7b1f777280dd461bd25ce0d67e5bd41830c91, which changed the retrieve_contents method. This method will have to be carefuly refactored, too.
    """Extracts report sections from .trs files.
    Saves the extractions in a folder [folder]/tmp"""
    files: list[Path] = get_files(folder, file, "trs")
    for filename in files:
        trs_parser = TRSParser(filename)
        trs_parser.trs_tmp()


@app.command(short_help="Extracts random segments from .trs files")
def rs(
    folder: Annotated[
        Path,
        typer.Argument(help="The folder containing the .trs files"),
    ] = Path.cwd(),
    file: Annotated[
        Optional[Path],
        typer.Option(help="A single file to process instead of a whole folder"),
    ] = None,
) -> None:      
    """Calculates the minimum sample needed for the validation of the input TRS transcription 
    and extracts random segments (audio and text, the latter in a tabular file) according to a given quantity."""
    if file:
        save_folder = file.parent.absolute()
    else:
        save_folder = folder.absolute()
    files: list[Path] = get_files(folder, file, "trs")
    utils.random_sampling(files, save_folder)


console = Console()


def main():
    app()


if __name__ == "__main__":
    main()
