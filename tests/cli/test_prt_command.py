import shutil
from pathlib import Path

from pytest import fixture

from tests.helpers import invoke

DATA_DIRECTORY = Path(__file__).parent.parent / "data" / "prt"


@fixture(autouse=True)
def test_directory(tmp_path, monkeypatch) -> Path:
    """copies the fixtures into an isolated temporary folder.
    monkeypatch *temporarily* changes the cwd to this folder
    """
    shutil.copytree(DATA_DIRECTORY / "input", tmp_path, dirs_exist_ok=True)

    monkeypatch.chdir(tmp_path)
    return tmp_path


@fixture
def test_file(test_directory) -> Path:
    return test_directory / "en_test.trs"


def test_prt_command_with_cwd():
    result = invoke("prt")
    assert result.exit_code == 0, result.stderr
    assert result.stdout  # Check something was printed


def test_prt_command_with_folder_arg(test_directory):
    result = invoke("prt", test_directory)
    assert result.exit_code == 0, result.stderr
    assert result.stdout  # Check something was printed


def test_prt_command_with_file_arg(test_file):
    result = invoke("prt", "--file", test_file)
    assert result.exit_code == 0, result.stderr
    assert result.stdout  # Check something was printed
