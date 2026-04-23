from typer.testing import CliRunner
from trsproc.__main__ import app
from pytest import fixture
from pathlib import Path
import shutil

DATA_DIRECTORY = Path(__file__).parent / "data" / "txt"
runner = CliRunner()


def invoke(*args):
    """Small helper to reduce boilerplate (path objects need to be converted to strings)"""
    return runner.invoke(app, [str(arg) for arg in args])


@fixture(autouse=True)
def test_directory(tmp_path, monkeypatch) -> Path:
    """copies the fixtures into an isolated temporary folder.
    monkeypatch *temporarily* changes the cwd to this folder
    """
    for _file in (DATA_DIRECTORY / "input").glob("*.trs"):
        shutil.copy(_file, tmp_path)

    monkeypatch.chdir(tmp_path)
    return tmp_path


@fixture
def simple_test_file(test_directory) -> Path:
    return test_directory / "en_test.trs"


@fixture
def expected_placeholder_directory() -> Path:
    return DATA_DIRECTORY / "output" / "placeholder"


@fixture
def expected_txt_directory() -> Path:
    return DATA_DIRECTORY / "output" / "txt"


def test_txt_command_with_cwd():
    result = invoke("txt")
    assert result.exit_code == 0, result.stderr


def test_txt_command_with_folder_arg(test_directory):
    result = invoke("txt", test_directory)
    assert result.exit_code == 0, result.stderr


def test_txt_command_with_file_arg(simple_test_file):
    result = invoke("txt", "--file", simple_test_file)
    assert result.exit_code == 0, result.stderr


def test_txt_command_output(
    test_directory,
    expected_placeholder_directory,
    expected_txt_directory,
):
    result = invoke("txt")
    assert result.exit_code == 0
    for expected_placeholder_file in expected_placeholder_directory.glob(
        "*placeholder.trs"
    ):
        generated_placeholder = (
            test_directory / "placeholder" / expected_placeholder_file.name
        )
        assert generated_placeholder.exists()
        assert (
            generated_placeholder.read_text().strip()
            == expected_placeholder_file.read_text().strip()
        )
    for expected_txt_file in expected_txt_directory.glob("*.txt"):
        generated_txt = test_directory / "txt" / expected_txt_file.name
        assert generated_txt.exists()
        assert (
            generated_txt.read_text().strip() == expected_txt_file.read_text().strip()
        )
