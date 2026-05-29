import shutil
from pathlib import Path

from pytest import fixture
from typer.testing import CliRunner

from trsproc.__main__ import app
from trsproc.parser import trs_to_rttm, TRSParser

DATA_DIRECTORY = Path(__file__).parent / "data" / "rttm"
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
    return test_directory / "en_test.trs"


@fixture
def expected_output_dir() -> Path:
    return DATA_DIRECTORY / "output"


def test_rttm_command_with_cwd():
    result = invoke("rttm")
    assert result.exit_code == 0, result.stderr


def test_rttm_command_with_folder_arg(test_directory):
    result = invoke("rttm", test_directory)
    assert result.exit_code == 0, result.stderr


def test_rttm_command_with_file_arg(simple_test_file):
    result = invoke("rttm", "--file", simple_test_file)
    assert result.exit_code == 0, result.stderr


def test_rttm_command_output(
    test_directory,
    expected_output_dir,
):
    result = invoke("rttm")
    assert result.exit_code == 0, result.stderr
    for output_file in test_directory.glob("*.rttm"):
        expected_output_file = expected_output_dir / output_file.name
        assert output_file.read_text().strip() == expected_output_file.read_text().strip()


def test_module_level_trs_to_rttm(test_directory):
    """The module-level trs_to_rttm() convenience function works."""
    trs_file = test_directory / "en_test.trs"
    trs_to_rttm(trs_file)
    rttm_file = test_directory / "en_test.rttm"
    assert rttm_file.exists()
    lines = rttm_file.read_text().strip().split("\n")
    assert len(lines) > 0
    # Every line must be a valid 10-field SPEAKER entry
    for line in lines:
        fields = line.split()
        assert len(fields) == 10
        assert fields[0] == "SPEAKER"


def test_rttm_speaker_name_spaces_replaced(test_directory, monkeypatch):
    """Whitespace in speaker names is replaced to preserve RTTM columns."""
    trs_file = test_directory / "en_test.trs"
    parser = TRSParser(trs_file)

    # Simulate a speaker with a multi-word name
    parser.speakers["spk1"] = ("John Doe", "male")

    rttm_out = test_directory / "en_test.rttm"
    parser.trs_to_rttm()

    for line in rttm_out.read_text().strip().split("\n"):
        fields = line.split()
        assert len(fields) == 10, f"Line has wrong number of fields: {line}"
        # The speaker name field should not contain a space
        assert fields[6] == "John_Doe", f"Speaker name not sanitized: {fields[6]}"


def test_rttm_unknown_speaker_fallback(test_directory, monkeypatch):
    """When a speaker ID is not in self.speakers, fall back gracefully."""
    trs_file = test_directory / "en_test.trs"
    parser = TRSParser(trs_file)

    # Remove the speaker entry to trigger the fallback path
    parser.speakers = {}

    rttm_out = test_directory / "en_test.rttm"
    parser.trs_to_rttm()

    for line in rttm_out.read_text().strip().split("\n"):
        fields = line.split()
        assert len(fields) == 10
        # Speaker name falls back to the id, type to <NA>
        assert fields[6] == "spk1"
        assert fields[8] == "<NA>"
