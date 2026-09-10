import shutil
from pathlib import Path

from pytest import fixture
from typer.testing import CliRunner

from trsproc.__main__ import app

DATA_DIRECTORY = Path(__file__).parent / "data" / "tgrs"
runner = CliRunner()


def invoke(*args):
    """Small helper to reduce boilerplate (path objects need to be converted to strings)"""
    return runner.invoke(app, [str(arg) for arg in args])


@fixture(autouse=True)
def test_directory(tmp_path, monkeypatch) -> Path:
    """copies the fixtures into an isolated temporary folder.
    monkeypatch *temporarily* changes the cwd to this folder
    """
    shutil.copytree(DATA_DIRECTORY / "input", tmp_path, dirs_exist_ok=True)

    monkeypatch.chdir(tmp_path)
    return tmp_path


@fixture
def simple_test_file(test_directory) -> Path:
    return test_directory / "en_test.TextGrid"


@fixture
def expected_output_dir() -> Path:
    return DATA_DIRECTORY / "output"


def test_tgrs_command_with_cwd():
    result = invoke("tgrs")
    assert result.exit_code == 0, result.stderr


def test_tgrs_command_with_folder_arg(test_directory):
    result = invoke("tgrs", test_directory)
    assert result.exit_code == 0, result.stderr


def test_tgrs_command_with_file_arg(simple_test_file):
    result = invoke("tgrs", "--file", simple_test_file)
    assert result.exit_code == 0, result.stderr


def test_tgrs_command_output(
    test_directory,
    expected_output_dir,
):
    result = invoke("tgrs")
    assert result.exit_code == 0, result.stderr
    for output_file in test_directory.glob("*.trs"):
        expected_output_file = expected_output_dir / output_file.name
        output_file_n_lines = len(output_file.read_text().strip().split("\n"))
        expected_output_file_n_lines = len(expected_output_file.read_text().strip().split("\n"))
        assert output_file_n_lines == expected_output_file_n_lines
