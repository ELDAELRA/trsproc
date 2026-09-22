import shutil
from pathlib import Path

from pytest import fixture

from tests.helpers import invoke

DATA_DIRECTORY = Path(__file__).parent.parent / "data" / "vsi"


@fixture(autouse=True)
def test_directory(tmp_path, monkeypatch) -> Path:
    """copies the fixtures into an isolated temporary folder.
    monkeypatch *temporarily* changes the cwd to this folder
    """
    shutil.copytree(DATA_DIRECTORY / "input", tmp_path, dirs_exist_ok=True)

    monkeypatch.chdir(tmp_path)
    return tmp_path


@fixture
def vsi_command_output_file(test_directory) -> Path:
    return test_directory / "summary_validation-vsi.tsv"


@fixture
def vsi_command_expected_output_file(test_directory) -> Path:
    return DATA_DIRECTORY / "output" / "summary_validation-vsi.tsv"


def test_vsi_command_with_cwd():
    result = invoke("vsi")
    assert result.exit_code == 0, result.stderr


def test_vsi_command_with_folder_arg(test_directory):
    result = invoke("vsi", test_directory)
    assert result.exit_code == 0, result.stderr


def test_vsi_command_output(
    vsi_command_output_file,
    vsi_command_expected_output_file,
):
    result = invoke("vsi")
    assert result.exit_code == 0, result.stderr
    assert vsi_command_output_file.exists()
    output_n_lines = len(vsi_command_output_file.read_text().strip().split("\n"))
    expected_output_n_lines = len(vsi_command_expected_output_file.read_text().strip().split("\n"))
    assert (
        output_n_lines == expected_output_n_lines
    )  # We can't compare the content since they contain
    # the folder path, so we only compare the line length
