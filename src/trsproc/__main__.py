# -*- coding: utf-8 -*-
#!/usr/bin/env python3
#
##
### trsproc ELDA-R&D-2023
#### A Python library to process Transcriber TRS files
#####

import re
from pathlib import Path
from typing import Annotated, Optional

import typer
from PyQt6.QtWidgets import QApplication

from trsproc import parser, utils
from trsproc.parser import TRSParser
from trsproc.validation.gui import TranscriptionValidatorGUI
from trsproc.validation.io import make_paths, is_validation_complete

app = typer.Typer()
crt_app = typer.Typer(help="Apply corrections to .trs files")
app.add_typer(crt_app, name="crt")


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


@crt_app.command("turn-differences")
def crt_turn_differences(
    folder: Annotated[
        Optional[Path],
        typer.Argument(
            help="The folder containing the .trs files", show_default=str(Path.cwd())
        ),
    ] = None,
    file: Annotated[
        Optional[Path], typer.Option(help="A single file to process")
    ] = None,
) -> None:
    """Search for differences in segmentation with twin files"""
    if folder is None:
        folder = Path.cwd()
    for filename in get_files(folder, file, "trs"):
        utils.turn_difference_trs(TRSParser(filename))


@crt_app.command("empty-space")
def crt_empty_space(
    folder: Annotated[
        Optional[Path],
        typer.Argument(
            help="The folder containing the .trs files", show_default=str(Path.cwd())
        ),
    ] = None,
    file: Annotated[
        Optional[Path], typer.Option(help="A single file to process")
    ] = None,
) -> None:
    """Add empty space before each NE annotation"""
    if folder is None:
        folder = Path.cwd()
    for filename in get_files(folder, file, "trs"):
        utils.trs_empty_space_before_ne(TRSParser(filename))


@crt_app.command("la")
def crt_la(
    folder: Annotated[
        Optional[Path],
        typer.Argument(
            help="The folder containing the .trs files", show_default=str(Path.cwd())
        ),
    ] = None,
    file: Annotated[
        Optional[Path], typer.Option(help="A single file to process")
    ] = None,
) -> None:
    """Correct sentences ending with 'là' to 'la'. Requires prior txt command"""
    if folder is None:
        folder = Path.cwd()
    for filename in get_files(folder, file, "trs"):
        utils.correction_la(TRSParser(filename))


@crt_app.command("maj")
def crt_maj(
    folder: Annotated[
        Optional[Path],
        typer.Argument(
            help="The folder containing the .trs files", show_default=str(Path.cwd())
        ),
    ] = None,
    file: Annotated[
        Optional[Path], typer.Option(help="A single file to process")
    ] = None,
) -> None:
    """Correct misplaced capital letters."""
    if folder is None:
        folder = Path.cwd()
    for filename in get_files(folder, file, "trs"):
        utils.correction_maj(TRSParser(filename))


@app.command(
    short_help="Extracts the text from .trs files into .txt files",
)
def txt(
    folder: Annotated[
        Optional[Path],
        typer.Argument(
            help="The folder containing the .trs files", show_default=str(Path.cwd())
        ),
    ] = None,
    file: Annotated[
        Optional[Path],
        typer.Option(help="A single file to process instead of a whole folder"),
    ] = None,
) -> None:
    """Extracts the text from .trs files into .txt files, and creates placeholder .trs files, to merge text back in.
    This is intended to be used for easily modifying the text from .trs files (e.g for fixing typos)"""
    if folder is None:
        folder = Path.cwd()
    for filename in get_files(folder, file, "trs"):
        trs_parser = TRSParser(filename)
        trs_parser.trs_to_txt()


@app.command(
    short_help="Rewrites trs files in the placeholder .trs files",
)
def trs(
    folder: Annotated[
        Optional[Path],
        typer.Argument(
            help="The folder containing the .txt files",
            show_default=str(Path.cwd() / "txt"),
        ),
    ] = None,
    file: Annotated[
        Optional[Path],
        typer.Option(help="A single file to process instead of a whole folder"),
    ] = None,
):
    """\brewrites a TRS file using the input txt file and a TRS-placeholder placed in a subfolder of the parent input folder.
    \bThe command NEEDS to be called from a folder that has a txt and a placeholder subfolder (presumably created by a previous txt command).
    \bThe rewritten TRS will have the content of the txt and the structure of the TRS-placeholder and will be written in the txt folder.
    """
    if folder is None:
        folder = Path.cwd() / "txt"
    for filename in get_files(folder, file, "txt"):
        parser.txt_to_trs(filename)


@app.command(
    short_help="Produces a tabular file with the structures and contents of the .trs files",
)
def tsv(
    folder: Annotated[
        Optional[Path],
        typer.Argument(
            help="The folder containing the .trs files", show_default=str(Path.cwd())
        ),
    ] = None,
    file: Annotated[
        Optional[Path],
        typer.Option(help="A single file to process instead of a whole folder"),
    ] = None,
):  # TODO : output filename as argument. When launched with --file, the file has no name (.tsv)
    """Produces a tabular file with the structures and contents of the .trs files.
    The resulting .tsv file will be located in [folder]/[folder].tsv"""
    if folder is None:
        folder = Path.cwd()
    for filename in get_files(folder, file, "trs"):
        trs_parser = TRSParser(filename)
        trs_parser.trs_to_tsv()


@app.command(
    short_help="Deletes Named Entity from .trs files",
)
def cne(
    folder: Annotated[
        Optional[Path],
        typer.Argument(
            help="The folder containing the .trs files", show_default=str(Path.cwd())
        ),
    ] = None,
    file: Annotated[
        Optional[Path],
        typer.Option(help="A single file to process instead of a whole folder"),
    ] = None,
):
    """Deletes the Named Entity annotations if any are present in the input TRS.
    Writes the resulting .trs files in [folder]/clean"""
    if folder is None:
        folder = Path.cwd()
    for filename in get_files(folder, file, "trs"):
        trs_parser = TRSParser(filename)
        trs_parser.clean_ne_from_trs()


@app.command(
    short_help="Extracts named entites from .trs files",
)
def ne(
    folder: Annotated[
        Optional[Path],
        typer.Argument(
            help="The folder containing the .trs files", show_default=str(Path.cwd())
        ),
    ] = None,
    file: Annotated[
        Optional[Path],
        typer.Option(help="A single file to process instead of a whole folder"),
    ] = None,
):  # TODO : output filename as argument. When launched with --file, the file has no name (.tsv)
    """Extracts the Named Entity annotations if any are present in the input TRS.
    Saves them in a tabular file located in [folder]/folder_NE_extraction.tsv"""
    if folder is None:
        folder = Path.cwd()
    for filename in get_files(folder, file, "trs"):
        trs_parser = TRSParser(filename)
        trs_parser.retrieve_ne_to_tsv()


@app.command(
    short_help="Adds language tags to transcriptions",
)
def lang(
    language: Annotated[
        Optional[str],
        typer.Option(help="The language to use for the tags."),
    ] = None,
    folder: Annotated[
        Optional[Path],
        typer.Argument(
            help="The folder containing the .trs files", show_default=str(Path.cwd())
        ),
    ] = None,
    file: Annotated[
        Optional[Path],
        typer.Option(help="A single file to process instead of a whole folder"),
    ] = None,
    json_dict: Annotated[
        Optional[Path],
        typer.Option(
            help="The json file containing the language tags to add.",
            show_default=str(Path.cwd() / "lang-tag.json"),
        ),  # TODO: describe the expected format
    ] = None,
):  # TODO: refactor utils.add_lang_tag. Right now, the language tag is required even if a json file is provided.
    """Adds a language tag to each transcription segment not having one in the input TRS files.
    The language can either be specified with the `--language` option, or within a json file, which can be specified with the --json-dict option (which defaults to [folder]/lang-tag.json)
    The resulting .trs files will be written in [folder]/lang"""
    if folder is None:
        folder = Path.cwd()
    if json_dict is None:
        json_dict = Path.cwd() / "lang-tag.json"

    if not json_dict.exists() and language is None:
        raise typer.BadParameter(
            f"Can't find {json_dict}. Consider setting --language or --json-dict",
        )

    for filename in get_files(folder, file, "trs"):
        trs_parser = TRSParser(filename)
        utils.add_lang_tag(trs_parser, json_dict, language)


@app.command()
def prt(
    folder: Annotated[
        Optional[Path],
        typer.Argument(
            help="The folder containing the .trs files", show_default=str(Path.cwd())
        ),
    ] = None,
    file: Annotated[
        Optional[Path],
        typer.Option(help="A single file to process instead of a whole folder"),
    ] = None,
) -> None:
    """Prints the parsed trs contents"""
    if folder is None:
        folder = Path.cwd()
    for filename in get_files(folder, file, "trs"):
        trs_parser = TRSParser(filename)
        trs_parser.print()


@app.command(
    short_help="Pre-annotates named entities in .trs files",
)
def pne(
    folder: Annotated[
        Optional[Path],
        typer.Argument(
            help="The folder containing the .trs files", show_default=str(Path.cwd())
        ),
    ] = None,
    file: Annotated[
        Optional[Path],
        typer.Option(help="A single file to process instead of a whole folder"),
    ] = None,
) -> None:  # TODO: Get a pre-annotation json file to understand and test the utils.pre_annotate function, and add the required tsv and json files as arguments.
    """Pre-annotates the input TRS using the table created in the `-ne` flag as a custom annotation dictionnary"""
    if folder is None:
        folder = Path.cwd()
    files: list[Path] = get_files(folder, file, "trs")
    for filename in files:
        trs_parser = TRSParser(filename)
        utils.trs_preannotation(trs_parser)


@app.command(
    short_help="Extracts report sections from .trs files",
)
def tmp(
    folder: Annotated[
        Optional[Path],
        typer.Argument(
            help="The folder containing the .trs files", show_default=str(Path.cwd())
        ),
    ] = None,
    file: Annotated[
        Optional[Path],
        typer.Option(help="A single file to process instead of a whole folder"),
    ] = None,
) -> None:  # FIXME: The tmp command was broken in commit 30c7b1f777280dd461bd25ce0d67e5bd41830c91, which changed the retrieve_contents method. This method will have to be carefuly refactored, too.
    """Extracts report sections from .trs files.
    Saves the extractions in a folder [folder]/tmp"""
    if folder is None:
        folder = Path.cwd()
    for filename in get_files(folder, file, "trs"):
        trs_parser = TRSParser(filename)
        trs_parser.trs_tmp()


@app.command(
    short_help="Extracts random segments from .trs files and launches validation GUI",
)
def rs(
    folder: Annotated[
        Optional[Path],
        typer.Argument(
            help="The folder containing the .trs files", show_default=str(Path.cwd())
        ),
    ] = None,
    file: Annotated[
        Optional[Path],
        typer.Option(help="A single file to process instead of a whole folder"),
    ] = None,
) -> None:
    """Calculates the minimum sample needed for the validation of the input TRS transcription
    and extracts random segments (audio and text, the latter in a tabular file) according to a given quantity.
    Launches the validation GUI after extraction.

    If a validated TSV already exists:
    - resumes validation if incomplete
    - prompts for re-running the sampling if complete
    If not:
    - runs sampling and extraction before launching the GUI"""
    if folder is None:
        folder = Path.cwd()
    if file:
        save_folder = file.parent.absolute()
    else:
        save_folder = folder.absolute()
    files: list[Path] = get_files(folder, file, "trs")

    sample_tsv = next(save_folder.glob("sample_segments_*.tsv"), None)
    validated_tsv = next(save_folder.glob("sample_segments_*_validated.tsv"), None)

    if validated_tsv:
        if is_validation_complete(validated_tsv):
            typer.echo(f"Validation already completed: {validated_tsv}")
            redo = input("Re-run sampling? (y/n)\t")
            if not re.search("y", redo.lower()):
                return
            sample_tsv = utils.random_sampling(files, save_folder)
            if sample_tsv:
                utils.extract_segments(sample_tsv)
        else:
            typer.echo(f"Resuming validation: {validated_tsv}")
            sample_tsv = validated_tsv
    else:
        if sample_tsv:
            if not (save_folder / "validation").exists():
                utils.extract_segments(sample_tsv)
        else:
            sample_tsv = utils.random_sampling(files, save_folder)
            if sample_tsv:
                utils.extract_segments(sample_tsv)

    if sample_tsv:
        app = QApplication([])
        w = TranscriptionValidatorGUI(paths=make_paths(str(sample_tsv)))
        w.show()
        app.exec()


@app.command(
    short_help="Extracts random Named Entity segments from .trs files",
)
def rsne(
    folder: Annotated[
        Optional[Path],
        typer.Argument(
            help="The folder containing the .trs files", show_default=str(Path.cwd())
        ),
    ] = None,
    file: Annotated[
        Optional[Path],
        typer.Option(help="A single file to process instead of a whole folder"),
    ] = None,
) -> None:
    """calculates the minimum sample needed for the validation of Named Entities of the input TRS
    and extracts them (audio segments and text, the latter in a tabular file) randomly by a given amount."""
    if folder is None:
        folder = Path.cwd()
    if file:
        save_folder = file.parent.absolute()
    else:
        save_folder = folder.absolute()
    files: list[Path] = get_files(folder, file, "trs")
    utils.random_sampling_ne(files, save_folder)


@app.command()
def rttm(
    folder: Annotated[
        Path | None,
        typer.Argument(help="The folder containing the .trs files", show_default=str(Path.cwd())),
    ] = None,
    file: Annotated[
        Path | None,
        typer.Option(help="A single file to process instead of a whole folder"),
    ] = None,
) -> None:
    """Converts .trs files to .rttm (Rich Transcription Time Marked) files."""
    if folder is None:
        folder = Path.cwd()
    for filename in get_files(folder, file, "trs"):
        trs_parser = TRSParser(filename)
        trs_parser.trs_to_rttm()


@app.command()
def tg(
    folder: Annotated[
        Optional[Path],
        typer.Argument(
            help="The folder containing the .trs files", show_default=str(Path.cwd())
        ),
    ] = None,
    file: Annotated[
        Optional[Path],
        typer.Option(help="A single file to process instead of a whole folder"),
    ] = None,
) -> None:
    # TODO : pass the audio file as an argument
    # TODO : make sure the audio file exists, as the TextGrid cannot be turned back to .trs without audio
    """Converts .trs files to .TextGrid files."""
    if folder is None:
        folder = Path.cwd()
    for filename in get_files(folder, file, "trs"):
        trs_parser = TRSParser(filename)
        trs_parser.trs_to_textgrid()


@app.command()
def tgrs(
    folder: Annotated[
        Optional[Path],
        typer.Argument(
            help="The folder containing the TextGrid files",
            show_default=str(Path.cwd()),
        ),
    ] = None,
    file: Annotated[
        Optional[Path],
        typer.Option(help="A single file to process instead of a whole folder"),
    ] = None,
) -> None:
    # TODO : pass the audio file as an argument
    # TODO : make sure the audio file exists, as the TextGrid cannot be turned back to .trs without audio
    """Converts .TextGrid files to .trs files."""
    if folder is None:
        folder = Path.cwd()
    for filename in get_files(folder, file, "TextGrid"):
        parser.textgrid_to_trs(filename)


@app.command(
    short_help="Converts VAD TextGrid files into .trs files",
)
def vad(
    folder: Annotated[
        Optional[Path],
        typer.Argument(
            help="The folder containing the TextGrid files",
            show_default=str(Path.cwd()),
        ),
    ] = None,
    file: Annotated[
        Optional[Path],
        typer.Option(help="A single file to process instead of a whole folder"),
    ] = None,
) -> None:
    # TODO: Get one of those TextGrid file for testing.
    """converts TextGrid files resulting from the use of a voice activity detection algorithm (VAD) into TRS files."""
    if folder is None:
        folder = Path.cwd()
    for filename in get_files(folder, file, "TextGrid"):
        parser.vad_to_trs(filename)


@app.command(
    short_help="Extracts statistics from .trs files",
)
def vsi(
    folder: Annotated[
        Optional[Path],
        typer.Argument(
            help="The folder containing the .trs files", show_default=str(Path.cwd())
        ),
    ] = None,
    file: Annotated[
        Optional[Path],
        typer.Option(help="A single file to process instead of a whole folder"),
    ] = None,
) -> None:
    """Produces a tabular file containing basic lexical information and statistics concerning the input TRS"""
    if folder is None:
        folder = Path.cwd()
    for filename in get_files(folder, file, "trs"):
        trs_parser = TRSParser(filename)
        trs_parser.validate_trs()


@app.command(
    short_help="Extracts language informations from .trs files",
)
def vsi_lang(
    folder: Annotated[
        Optional[Path],
        typer.Argument(
            help="The folder containing the .trs files", show_default=str(Path.cwd())
        ),
    ] = None,
    file: Annotated[
        Optional[Path],
        typer.Option(help="A single file to process instead of a whole folder"),
    ] = None,
) -> None:
    # FIXME: command seems to be broken, don't know since when
    """Produces a tabular file containing basic information abouth the language tags present in the input TRS"""
    if folder is None:
        folder = Path.cwd()
    for filename in get_files(folder, file, "trs"):
        trs_parser = TRSParser(filename)
        trs_parser.summary_lang_trs()


@app.command(
    short_help="Extracts language informations from .trs files in a temporary folder",
)
def rpt(
    folder: Annotated[
        Optional[Path],
        typer.Argument(
            help="The folder containing the .trs files", show_default=str(Path.cwd())
        ),
    ] = None,
    file: Annotated[
        Optional[Path],
        typer.Option(help="A single file to process instead of a whole folder"),
    ] = None,
) -> None:
    """Produces a tabular file containing basic information abouth the language tags present in the input TRS"""
    if folder is None:
        folder = Path.cwd()
    for filename in get_files(folder, file, "trs"):
        trs_parser = TRSParser(filename)
        utils.tmp_report(trs_parser)


def main():
    app()


if __name__ == "__main__":
    main()
