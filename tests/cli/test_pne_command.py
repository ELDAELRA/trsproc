import shutil
from pathlib import Path

from pytest import fixture

from tests.helpers import invoke

DATA_DIRECTORY = Path(__file__).parent.parent / "data" / "pne"


@fixture(autouse=True)
def test_directory(tmp_path, monkeypatch) -> Path:
    """Copies the fixtures into an isolated temporary folder.
    monkeypatch *temporarily* changes the cwd to this folder.
    """
    shutil.copytree(DATA_DIRECTORY / "input", tmp_path, dirs_exist_ok=True)

    monkeypatch.chdir(tmp_path)
    return tmp_path


@fixture
def pne_command_output_dir(test_directory) -> Path:
    return test_directory / "pne"


@fixture
def pne_command_expected_output_dir(test_directory) -> Path:
    return DATA_DIRECTORY / "output"


def test_pne_command_with_cwd():
    result = invoke("pne")
    assert result.exit_code == 0, result.stderr


def test_pne_command_with_folder_arg(test_directory):
    result = invoke("pne", test_directory)
    assert result.exit_code == 0, result.stderr


def test_pne_command_output(
    pne_command_output_dir,
    pne_command_expected_output_dir,
):
    result = invoke("pne")
    assert result.exit_code == 0, result.stderr
    assert pne_command_output_dir.exists()

    for output_file, expected_output_file in zip(
        pne_command_output_dir.glob("*"),
        pne_command_expected_output_dir.glob("*.trs"),
        strict=False,
    ):
        expected_output_file = pne_command_expected_output_dir / output_file.name
        assert output_file.read_text().strip() == expected_output_file.read_text().strip()
