from pathlib import Path

from trsproc.named_entities import extract_nes_from_transcription
from trsproc.new_parser import parse_trs_file

TRS_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE Trans SYSTEM "trans-14.dtd">
<Trans>
  <Speakers>
    <Speaker id="spk1" name="spk1" type="male" />
  </Speakers>
  <Episode>
{episode}
  </Episode>
</Trans>
"""


def _write_trs(tmp_path: Path, name: str, episode: str) -> Path:
    trs_path = tmp_path / name
    trs_path.write_text(TRS_TEMPLATE.format(episode=episode), encoding="utf-8")
    return trs_path


def test_ne_extraction_without_any_turn(tmp_path):
    # An Episode with no Section is valid, but turns[0] used to raise IndexError.
    trs_path = _write_trs(tmp_path, "empty_episode.trs", "")
    assert extract_nes_from_transcription(parse_trs_file(trs_path)) == []


def test_ne_begin_and_end_in_different_speech_turns_is_ignored(tmp_path):
    # start_idx indexes speechturn.content, so a begin left open in one speech turn used to
    # slice the content of the next one with a stale index, yielding an empty entity.
    episode = """    <Section type="report" startTime="0" endTime="2">
      <Turn speaker="spk1" startTime="0" endTime="2">
        <Sync time="0" /> hello <Event desc="pers" type="entities" extent="begin" /> world
        <Sync time="1" /> second segment <Event desc="pers" type="entities" extent="end" /> tail
      </Turn>
    </Section>"""
    trs_path = _write_trs(tmp_path, "split_ne.trs", episode)
    assert extract_nes_from_transcription(parse_trs_file(trs_path)) == []
