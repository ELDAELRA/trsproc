from librosa import get_duration

from trsproc.models import TrsprocModel
from trsproc.models.transcription import Transcription
from trsproc.named_entities import extract_nes_from_transcription
from trsproc.parser import praat_snr_for_segment


class TranscriptionStats(TrsprocModel):
    file_name: str
    file_path: str
    nb_spk: int
    """number of speakers defined in the file"""
    nb_lang: int
    """number of Event tags with type=language. If none found, defaults to 1"""
    dur_tot: float | None
    """waf file duration in seconds, if any"""
    dur_trans: float
    """duration in seconds of segments that contain text"""
    dur_nontrans: float
    """duration in seconds of segments that don't contain text"""
    nb_seg: int
    """number of segments"""
    nb_trans: int
    """number of segments that contain text"""
    nb_nontrans: int
    """number of segments that don't contain text"""
    nb_pronpi: int
    """number of 'pi' events, that is of not understandable speech"""
    nb_tokens: int
    """number of tokens. For latin alphabet, number of space-delimited sequences of characters"""
    nb_ne: int
    """number of named entity annotations."""
    mean_snr: float | None
    """mean signal-to-noise ratio"""


def get_transcription_stats(transcription: Transcription) -> TranscriptionStats:
    af = transcription.audio_file_path
    duration = get_duration(path=af) if af is not None else None
    nb_ne = len(extract_nes_from_transcription(transcription))
    mean_snr = praat_snr_for_segment(str(af)) if af is not None else None

    return TranscriptionStats(
        file_name=str(transcription.trs_file_path.name),
        file_path=str(transcription.trs_file_path.absolute()),
        nb_spk=transcription.nb_speakers,
        nb_lang=transcription.nb_languages,
        dur_tot=duration,
        dur_trans=transcription.duration_transcribed_turns,
        dur_nontrans=transcription.duration_non_transcribed_turns,
        nb_seg=transcription.nb_turns,
        nb_trans=transcription.nb_transcribed_turns,
        nb_nontrans=transcription.nb_non_transcribed_turns,
        nb_pronpi=transcription.nb_pronpi,
        nb_tokens=transcription.nb_tokens,
        nb_ne=nb_ne,
        mean_snr=mean_snr,
    )
