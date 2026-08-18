from pathlib import Path

from trsproc.models import Speaker
from trsproc.new_parser import parse_trs_file, write_trs

directory = Path(__file__).parent / "data" / "misc"
trs_test_file = directory / "transcriber_test.trs"
invalid_fields_file = directory / "invalid_speaker_fields.trs"


def test_parser_simple():
    parser = parse_trs_file(trs_test_file)
    assert len(parser.turns) == 11


def test_invalid_optional_fields_fallback_to_none():
    parser = parse_trs_file(invalid_fields_file)
    assert parser.speakers[0] == Speaker(
        id="spk1", name="fs1", type=None, dialect=None, accent=None, check=None, scope=None
    )


def test_write_trs(tmp_path):
    out_path = tmp_path / "from_python.trs"
    parser = parse_trs_file(trs_test_file)
    write_trs(parser, out_path)
    parser.trs_file_path = out_path  # otherwise the objects will obviously be different
    assert parser == parse_trs_file(out_path)

