import shutil
from pathlib import Path

from pytest import fixture

from tests.helpers import invoke

DATA_DIRECTORY = Path(__file__).parent.parent / "data" / "ne"


@fixture(autouse=True)
def test_directory(tmp_path, monkeypatch) -> Path:
    """copies the fixtures into an isolated temporary folder.
    monkeypatch *temporarily* changes the cwd to this folder
    """
    shutil.copytree(DATA_DIRECTORY / "input", tmp_path, dirs_exist_ok=True)

    monkeypatch.chdir(tmp_path)
    return tmp_path


@fixture
def ne_command_output_file(test_directory) -> Path:
    return test_directory / (f"{test_directory.name}_NE_extraction.tsv")


@fixture
def ne_command_expected_output_file(test_directory) -> Path:
    return DATA_DIRECTORY / "output" / "expected_output.tsv"


def test_ne_command_with_cwd():
    result = invoke("ne")
    assert result.exit_code == 0, result.stderr


def test_ne_command_with_folder_arg(test_directory):
    result = invoke("ne", test_directory)
    assert result.exit_code == 0, result.stderr


def test_ne_command_output(
    ne_command_output_file,
    ne_command_expected_output_file,
):
    result = invoke("ne")
    assert result.exit_code == 0, result.stderr
    assert ne_command_output_file.exists()
    output_n_lines = len(ne_command_output_file.read_text().split("\n"))
    expected_output_n_lines = len(ne_command_expected_output_file.read_text().split("\n"))
    assert (
        output_n_lines == expected_output_n_lines
    )  # We can't compare the content since they contain
    # the folder path, so we only compare the line length
