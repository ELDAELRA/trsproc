"""Contains the high level models that represent the parsed TRS file in memory."""

from functools import cached_property
from pathlib import Path
from statistics import mean

from pydantic import SerializeAsAny, model_validator

from trsproc.models.base import TrsprocModel
from trsproc.models.trs import (
    Event,
    Speaker,
    SpeechTurnElement,
    Topic,
    TRSEpisode,
    TRSSection,
    TRSTrans,
    TRSTurn,
    Utterance,
)
from trsproc.signal import wada_snr


class SpeechTurn(TrsprocModel):
    start: float
    end: float
    speakers: list[Speaker]
    content: SerializeAsAny[
        list[SpeechTurnElement]
    ]  # Without SerializeAsAny, moodel_dump prints an empty object
    # (because that's what SpeechTurnElement declares, but at runtime it can be any child instance)
    trs_turn: TRSTurn
    trs_section: TRSSection
    audio_file_path: Path | None = None

    @property
    def text(self) -> str:
        return " ".join(
            utterance.text for utterance in self.content if isinstance(utterance, Utterance)
        )

    @property
    def duration(self) -> float:
        return self.end - self.start

    @property
    def has_overlap(self) -> bool:
        return len(self.speakers) > 1

    def get_speaker_idx(self, id: str) -> str:
        """Helper method to get the index of a speaker with a given id.
        Used to write .trs for turns with overlap (Who tag)"""
        for i, speaker in enumerate(self.speakers):
            if speaker.id == id:
                return str(i + 1)

        raise ValueError(f"Unknown speaker ID {id}, can't determine who is speaking in the overlap")

    @cached_property
    def snr(self) -> float | None:
        """Compute the mean Signal-to-Noise Ratio (SNR) which tells how much stronger
        the desired signal (speech) is compared to the background noise.

        SNR is a decibel value on a logarithmic scale, higher is always better.
        Each +3 dB doubles the SNR; +10 dB means 10× more signal relative to noise;
        +20 dB means 100×.

        Context defines "acceptable" SNR levels: analog voice needs ~30 dB,
        digital communications can work down to ~10 dB or lower with error correction,
        audio engineering aims for 60-96 dB.

        In summary when SNR equals:
        0 dB - signal equals noise, essentially undetectable;
        < 10 dB - poor, signal barely distinguishable from noise;
        10-20 dB - usable but noisy, errors likely;
        20-40 dB - good quality, reliable for most applications;
        > 40 dB - excellent, noise is negligible;
        > 60 dB - near-perfect, often limited by instrumentation.
        """
        if self.audio_file_path is None:
            return None
        return wada_snr(self.audio_file_path, self.start, self.end)


class Transcription(TrsprocModel):
    trs_file_path: Path
    speakers: list[Speaker]
    topics: list[Topic]
    turns: list[SpeechTurn]
    trs_episode: TRSEpisode  # TODO: make optional when converting to TRS from other formats
    trs_trans: TRSTrans  # TODO: make optional when converting to TRS from other formats
    audio_file_path: Path | None = None

    @model_validator(mode="after")
    def _init_audio_file_path(self) -> "Transcription":
        """Resolve the path when the model is initiated
        And then inject it into any turn that doesn't have one yet"""
        object.__setattr__(self, "audio_file_path", self._resolve_audio_path())
        if self.audio_file_path is not None:
            object.__setattr__(
                self,
                "turns",
                [
                    t.model_copy(update={"audio_file_path": self.audio_file_path})
                    if t.audio_file_path is None
                    else t
                    for t in self.turns
                ],
            )
        return self

    def _resolve_audio_path(self) -> Path | None:
        """Returns the audio file path as defined in the trs file, as an absolute path.
        If that path doesn't exist, tries to guess the audio path based on the trs path.
        If none exist, returns None
        """
        candidates = (
            self.trs_trans.audio_filename,
            self.trs_file_path,
        )
        for candidate in candidates:
            if candidate and (path := Path(candidate).with_suffix(".wav")).exists():
                return path.absolute()
        return None

    @property
    def text(self) -> str:
        return " ".join([turn.text for turn in self.turns])

    @property
    def nb_tokens(self) -> int:
        return len(self.text)  # TODO : adapt for jkz alphabets

    @property
    def utterances(self) -> list[Utterance]:
        return [
            utterance
            for turn in self.turns
            for utterance in turn.content
            if isinstance(utterance, Utterance)
        ]

    @property
    def nb_turns(self) -> int:
        return len(self.turns)

    @property
    def nb_speakers(self) -> int:
        return len(self.speakers)

    @property
    def languages(self) -> set[str]:
        return {
            event.desc
            for turn in self.turns
            for event in turn.content
            if isinstance(event, Event)
            if event.type == "language" and event.extent != "end"
        }

    @property
    def nb_languages(self) -> int:
        if not self.languages:
            return 1
        return len(self.languages)

    @property
    def duration_transcribed_turns(self) -> float:
        return sum(turn.duration for turn in self.turns if turn.text)

    @property
    def nb_transcribed_turns(self) -> int:
        return len([turn for turn in self.turns if turn.text])

    @property
    def duration_non_transcribed_turns(self) -> float:
        return sum(turn.duration for turn in self.turns if not turn.text)

    @property
    def nb_non_transcribed_turns(self) -> int:
        return len([turn for turn in self.turns if not turn.text])

    @property
    def nb_pronpi(self) -> int:
        return len(
            [
                event
                for turn in self.turns
                for event in turn.content
                if isinstance(event, Event)
                and (
                    event.desc == "pi"
                    or (event.type == "pronounce" and event.extent == "instantaneous")
                )
            ]
        )

    @property
    def duration(self) -> float:
        """Duration according to the trs file (elapsed time - last segment time)"""
        try:
            elapsed_time = float(self.trs_trans.elapsed_time)  # type: ignore
        except (ValueError, TypeError):
            elapsed_time = 0.0
        end = self.turns[-1].end if self.turns else 0.0
        return end - elapsed_time

    @cached_property
    def mean_snr(self) -> float | None:
        """Mean Signal-to-Noise ratio of the SNRs computed from the SNR of each segment.

        In summary when SNR equals:
        0 dB - signal equals noise, essentially undetectable;
        < 10 dB - poor, signal barely distinguishable from noise;
        10-20 dB - usable but noisy, errors likely;
        20-40 dB - good quality, reliable for most applications;
        > 40 dB - excellent, noise is negligible;
        > 60 dB - near-perfect, often limited by instrumentation.
        """
        if self.audio_file_path is None:
            return None
        return round(mean(t.snr for t in self.turns if t.snr is not None), 3)
