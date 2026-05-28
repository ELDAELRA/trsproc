import shutil
from pathlib import Path

from pytest import fixture
from typer.testing import CliRunner

from trsproc.__main__ import app

DATA_DIRECTORY = Path(__file__).parent / "data" / "lang"


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
def lang_command_output_dir(test_directory) -> Path:
    return test_directory / "lang"


@fixture
def lang_command_expected_output_dir(test_directory) -> Path:
    return DATA_DIRECTORY / "output"


def test_lang_command_with_cwd():
    result = invoke("lang", "--language", "fr")
    assert result.exit_code == 0, result.stderr


def test_lang_command_with_folder_arg(test_directory):
    result = invoke("lang", test_directory, "--language", "fr")
    assert result.exit_code == 0, result.stderr


def test_lang_command_output(
    lang_command_output_dir,
    lang_command_expected_output_dir,
):
    result = invoke("lang", "--language", "fr")
    assert result.exit_code == 0, result.stderr
    assert lang_command_output_dir.exists()
    for output_file in lang_command_output_dir.glob("*"):
        expected_output_file = lang_command_expected_output_dir / output_file.name
        assert output_file.read_text().strip() == expected_output_file.read_text().strip()
