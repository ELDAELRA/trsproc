from pathlib import Path

from trsproc.models import Speaker
from trsproc.new_parser import parse_trs_file

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
