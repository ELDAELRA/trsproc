from pathlib import Path

from trsproc.new_parser import parse_trs_file
from trsproc.stats import TranscriptionStats, get_transcription_stats

test_file = Path(__file__).parent / "data" / "vsi" / "input" / "vsi_test.trs"


def test_stats():
    # Paths are removed because pytest generates a unique name for each test folder
    expected_stats = TranscriptionStats(
        file_name="vsi_test.trs",
        file_path="",
        audio_file_path="",
        nb_spk=3,
        nb_lang=2,
        dur_audio="120.49",
        dur_trs="120.49",
        dur_trans="110.05",
        dur_nontrans="10.44",
        nb_seg=22,
        nb_trans=20,
        nb_nontrans=2,
        nb_pronpi=3,
        nb_tokens=1481,
        nb_ne=1,
        mean_snr=13.17,
    )
    transcription = parse_trs_file(test_file)
    stats = get_transcription_stats(transcription)
    stats.file_path = ""
    stats.audio_file_path = ""
    assert stats == expected_stats
