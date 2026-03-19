from typer.testing import CliRunner
from trsproc.__main__ import app
from pytest import fixture
from pathlib import Path
import shutil

DATA_DIRECTORY = Path(__file__).parent / "data" / "tsv"


def invoke(*args):
    runner = CliRunner()
    """Small helper to reduce boilerplate (path objects need to be converted to strings)"""
    return runner.invoke(
        app,
        [str(arg) for arg in args],
    )


@fixture(autouse=True)
def test_directory(tmp_path, monkeypatch) -> Path:
    """copies the fixtures into an isolated temporary folder.
    monkeypatch *temporarily* changes the cwd to this folder
    """
    shutil.copytree(DATA_DIRECTORY / "input", tmp_path, dirs_exist_ok=True)
    monkeypatch.chdir(tmp_path)
    return tmp_path


@fixture
def tsv_command_output_file(test_directory) -> Path:
    return test_directory / (test_directory.name + ".tsv")


@fixture
def expected_tsv_output_file() -> Path:
    return DATA_DIRECTORY / "output" / "tsv_output.tsv"


def test_tsv_command_with_cwd():
    result = invoke("tsv")
    assert result.exit_code == 0, result.stderr


def test_tsv_command_with_folder_arg(test_directory):
    result = invoke("tsv", test_directory)
    assert result.exit_code == 0, result.stderr


def test_tsv_command_output(
    tsv_command_output_file,
    expected_tsv_output_file,
):
    result = invoke("tsv")
    assert result.exit_code == 0, result.stderr
    assert tsv_command_output_file.exists()
    output_n_lines = len(tsv_command_output_file.read_text().split("\n"))
    expected_n_lines = len(expected_tsv_output_file.read_text().split("\n"))
    assert (
        output_n_lines == expected_n_lines
    )  # We can't compare the content since they contain the folder path, so we only compare the line length
