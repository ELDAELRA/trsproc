from pathlib import Path

import pytest

from trsproc.new_parser import parse_trs_file
from trsproc.signal import get_duration, wada_snr

test_file = Path(__file__).parent / "data" / "snr" / "input" / "en_test.trs"


def test_duration():
    expected_duration = 120.49
    transcription = parse_trs_file(test_file)
    assert get_duration(transcription.audio_file_path) == expected_duration


def test_snr():
    expected_snr = 26.172
    transcription = parse_trs_file(test_file)
    snr = wada_snr(transcription.audio_file_path)
    assert snr == pytest.approx(expected_snr)
