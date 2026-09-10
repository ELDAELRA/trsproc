import shutil
from pathlib import Path

from pytest import fixture

from tests.helpers import invoke

DATA_DIRECTORY = Path(__file__).parent.parent / "data" / "cne"


@fixture(autouse=True)
def test_directory(tmp_path, monkeypatch) -> Path:
    """copies the fixtures into an isolated temporary folder.
    monkeypatch *temporarily* changes the cwd to this folder
    """
    shutil.copytree(DATA_DIRECTORY / "input", tmp_path, dirs_exist_ok=True)

    monkeypatch.chdir(tmp_path)
    return tmp_path


@fixture
def cne_command_output_dir(test_directory) -> Path:
    return test_directory / "clean"


@fixture
def cne_command_expected_output_dir(test_directory) -> Path:
    return DATA_DIRECTORY / "output"


def test_cne_command_with_cwd():
    result = invoke("cne")
    assert result.exit_code == 0, result.stderr


def test_cne_command_with_folder_arg(test_directory):
    result = invoke("cne", test_directory)
    assert result.exit_code == 0, result.stderr


def test_cne_command_output(
    cne_command_output_dir,
    cne_command_expected_output_dir,
):
    result = invoke("cne")
    assert result.exit_code == 0, result.stderr
    assert cne_command_output_dir.exists()
    for output_file in cne_command_output_dir.glob("*"):
        expected_output_file = cne_command_expected_output_dir / output_file.name
        assert output_file.read_text().strip() == expected_output_file.read_text().strip()
