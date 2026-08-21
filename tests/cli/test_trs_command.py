import shutil
from pathlib import Path

from pytest import fixture

from tests.helpers import invoke
from trsproc.new_parser import parse_trs_file

DATA_DIRECTORY = Path(__file__).parent.parent / "data" / "trs"


@fixture(autouse=True)
def test_directory(tmp_path, monkeypatch) -> Path:
    """copies the fixtures into an isolated temporary folder.
    monkeypatch *temporarily* changes the cwd to this folder
    """
    shutil.copytree(DATA_DIRECTORY / "input", tmp_path, dirs_exist_ok=True)

    monkeypatch.chdir(tmp_path)
    return tmp_path


@fixture
def simple_txt_test_file(test_directory) -> Path:
    return test_directory / "txt" / "en_test.txt"


@fixture
def expected_output_dir() -> Path:
    return DATA_DIRECTORY / "output"


def test_trs_command_with_cwd(test_directory):
    result = invoke("trs")
    assert result.exit_code == 0, result.stderr


def test_trs_command_with_folder_arg(test_directory):
    result = invoke("trs", test_directory)
    assert result.exit_code == 0, result.stderr


def test_trs_command_output(
    test_directory,
    expected_output_dir,
):
    result = invoke("trs")
    assert result.exit_code == 0, result.stderr
    for expected_output_file in expected_output_dir.glob(".trs"):
        generated_file = test_directory / "txt" / expected_output_file.name
        assert generated_file.exists()
        gold = parse_trs_file(expected_output_file)
        pred = parse_trs_file(generated_file)
        assert pred == gold
