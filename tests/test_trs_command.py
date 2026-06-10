import shutil
from pathlib import Path

from pytest import fixture
from typer.testing import CliRunner

from trsproc.__main__ import app

DATA_DIRECTORY = Path(__file__).parent / "data" / "trs"


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
    shutil.copytree(DATA_DIRECTORY / "input" / "placeholder", tmp_path / "placeholder")
    shutil.copytree(DATA_DIRECTORY / "input" / "txt", tmp_path / "txt")

    monkeypatch.chdir(tmp_path)
    return tmp_path


@fixture
def expected_output_dir() -> Path:
    return DATA_DIRECTORY / "output"


@fixture
def simple_txt_test_file() -> Path:
    return DATA_DIRECTORY / "input" / "txt" / "en_test.txt"


def test_trs_command_with_cwd(test_directory):
    result = invoke("trs")
    assert result.exit_code == 0, result.stderr


def test_trs_command_with_folder_arg(test_directory):
    result = invoke("trs", test_directory)
    assert result.exit_code == 0, result.stderr


def test_trs_command_with_file_arg(simple_txt_test_file):
    result = invoke("trs", "--file", simple_txt_test_file)
    assert result.exit_code == 0, result.stderr


def test_trs_command_output(
    test_directory,
    expected_output_dir,
):
    result = invoke("trs")
    assert result.exit_code == 0, result.stderr
    for expected_output_file in expected_output_dir.glob("*corrected.trs"):
        generated_file = test_directory / "txt" / expected_output_file.name
        assert generated_file.exists()
