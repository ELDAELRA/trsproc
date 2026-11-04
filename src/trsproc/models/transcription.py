"""Contains the high level models that represent the parsed TRS file in memory."""

from pathlib import Path

from pydantic import SerializeAsAny, model_validator, PrivateAttr

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
from typing import Optional
from trsproc.signal import wada_snr
from statistics import mean

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
    audio_file_path: Optional[Path] = None
    _snr_cache: Optional[float] = PrivateAttr(default=None)
    _cached_key: Optional[tuple] = PrivateAttr(default=None)

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

    @property
    def snr(self) -> Optional[float]:
        if self.audio_file_path is None:
            return None
        key = (self.audio_file_path, self.start, self.end)
        if self._cached_key != key:
            object.__setattr__(self, "_snr_cache", wada_snr(self.audio_file_path, self.start, self.end))
            object.__setattr__(self, "_cached_key", key)
        return self._snr_cache


class Transcription(TrsprocModel):
    trs_file_path: Path
    speakers: list[Speaker]
    topics: list[Topic]
    turns: list[SpeechTurn]
    trs_episode: TRSEpisode  # TODO: make optional when converting to TRS from other formats
    trs_trans: TRSTrans  # TODO: make optional when converting to TRS from other formats
    audio_file_path: Optional[Path] = None

    @model_validator(mode="after")
    def _init_audio_file_path(self) -> "Transcription":
        """Resolve the path when the model is initiated 
        And then inject it into any turn that doesn't have one yet"""
        object.__setattr__(self, "audio_file_path", self._resolve_audio_path())
        if self.audio_file_path is not None:
            object.__setattr__(self, "turns", [
                t.model_copy(update={"audio_file_path": self.audio_file_path})
                if t.audio_file_path is None else t
                for t in self.turns
            ])
        print("resolved:", self.audio_file_path, "| turns:", len(self.turns))
        return self

    def _resolve_audio_path(self) -> Optional[Path]:
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

    @property
    def mean_snr(self) -> float:
        """Mean Signal-to-Noise ratio of the SNRs computed from each segment"""
        if self.audio_file_path is None:
            return None
        return mean([t.snr for t in self.turns])
