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

console = Console()


def main():
    app()


if __name__ == "__main__":
    main()
