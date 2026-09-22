from librosa import get_duration

from trsproc.models import TrsprocModel
from trsproc.models.transcription import Transcription
from trsproc.named_entities import extract_nes_from_transcription
from trsproc.parser import praat_snr_for_segment


class TranscriptionStats(TrsprocModel):
    file_name: str
    file_path: str
    nb_spk: int
    nb_lang: int
    dur_tot: float | None
    dur_trans: float
    dur_nontrans: float
    nb_seg: int
    nb_trans: int
    nb_nontrans: int
    nb_pronpi: int
    nb_tokens: int
    nb_ne: int
    mean_snr: float | None


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
        dur_trans=transcription.nb_transcribed_turns,
        dur_nontrans=transcription.duration_non_transcribed_turns,
        nb_seg=transcription.nb_turns,
        nb_trans=transcription.nb_transcribed_turns,
        nb_nontrans=transcription.nb_non_transcribed_turns,
        nb_pronpi=transcription.nb_pronpi,
        nb_tokens=transcription.nb_tokens,
        nb_ne=nb_ne,
        mean_snr=mean_snr,
    )
