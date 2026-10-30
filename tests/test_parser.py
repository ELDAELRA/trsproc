from pathlib import Path

import pytest

from trsproc.models import Speaker, Utterance, Vocal
from trsproc.new_parser import parse_trs_file
from trsproc.writing import write_trs

directory = Path(__file__).parent / "data" / "misc"
trs_test_file = directory / "transcriber_test.trs"
invalid_fields_file = directory / "invalid_speaker_fields.trs"


def test_parser_simple():
    parser = parse_trs_file(trs_test_file)
    assert len(parser.turns) == 11


def test_xml_lang_is_parsed():
    # lxml exposes xml:lang under its namespace uri, which used to never match the "xml:lang"
    # alias declared on TRSTrans, so the language was always parsed as None.
    parser = parse_trs_file(trs_test_file)
    assert parser.trs_trans.xml_lang == "fr"


def test_vocal_is_parsed():
    # Vocal was missing from the match in parse_inline_element and fell through to "case _",
    # so the annotation was silently dropped on every parse -> write round trip.
    parser = parse_trs_file(trs_test_file)
    vocals = [
        element for turn in parser.turns for element in turn.content if isinstance(element, Vocal)
    ]
    assert len(vocals) == 1
    assert vocals[0].desc == "laughs"


@pytest.mark.parametrize(
    ("nb", "expected_speaker"),
    [
        ("1", "spk1"),
        ("2", "spk2"),
        ("3", None),  # out of range
        ("0", None),  # used to resolve to speakers[-1], i.e. the last speaker
        ("abc", None),  # nb is a NMTOKEN, int() raises ValueError
    ],
)
def test_who_nb_attribution(tmp_path, nb, expected_speaker):
    # nb is 1-indexed and declared as a NMTOKEN in the dtd, so it is neither guaranteed to
    # hold a number nor to be in range. A dirty value used to raise an uncaught ValueError
    # and abort the parse, while nb="0" silently resolved to speakers[-1] and attributed
    # the text to the wrong speaker.
    trs_path = tmp_path / "who_nb.trs"
    trs_path.write_text(
        f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE Trans SYSTEM "trans-14.dtd">
<Trans>
  <Speakers>
    <Speaker id="spk1" name="spk1" />
    <Speaker id="spk2" name="spk2" />
  </Speakers>
  <Episode>
    <Section type="report" startTime="0" endTime="1">
      <Turn speaker="spk1 spk2" startTime="0" endTime="1">
        <Sync time="0" /> hello <Who nb="{nb}" /> world
      </Turn>
    </Section>
  </Episode>
</Trans>
""",
        encoding="utf-8",
    )
    parser = parse_trs_file(trs_path)
    utterances = [element for element in parser.turns[0].content if isinstance(element, Utterance)]
    assert [utterance.text for utterance in utterances] == ["hello", "world"]
    speaker_id = utterances[1].speaker.id if utterances[1].speaker else None
    assert speaker_id == expected_speaker


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


OVERLAP_TRS_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE Trans SYSTEM "trans-14.dtd">
<Trans>
  <Speakers>
    <Speaker id="spk1" name="spk1" />
    <Speaker id="spk2" name="spk2" />
  </Speakers>
  <Episode>
    <Section type="report" startTime="0" endTime="2">
      <Turn speaker="spk1 spk2" startTime="0" endTime="2">
        <Sync time="0" />{turn_content}
      </Turn>
    </Section>
  </Episode>
</Trans>
"""


def _write_and_reread_overlap_turn(tmp_path, turn_content):
    src = tmp_path / "overlap.trs"
    src.write_text(OVERLAP_TRS_TEMPLATE.format(turn_content=turn_content), encoding="utf-8")
    out_path = tmp_path / "written.trs"
    write_trs(parse_trs_file(src), out_path)
    return parse_trs_file(out_path)


def test_write_overlap_turn_without_who(tmp_path):
    # An overlap turn without <Who> leaves the speaker of its utterances unknown. Writing it
    # used to raise AttributeError on tag.speaker.id : the text is now written as is and the
    # speaker stays unknown, instead of making the whole file unwritable.
    reread = _write_and_reread_overlap_turn(tmp_path, " hello world")
    assert [turn.text for turn in reread.turns] == ["hello world"]
    assert reread.turns[0].content[0].speaker is None


def test_write_overlap_turn_keeps_who_when_speaker_is_known(tmp_path):
    # Guards the other branch : an explicit <Who> still has to be written back, otherwise
    # the attribution of every overlap turn would be lost on the next read.
    reread = _write_and_reread_overlap_turn(tmp_path, ' hello <Who nb="2" /> world')
    utterances = reread.turns[0].content
    assert [utterance.text for utterance in utterances] == ["hello", "world"]
    assert utterances[0].speaker is None
    assert utterances[1].speaker.id == "spk2"
