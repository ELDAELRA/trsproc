"""Contains the high level models that represent the parsed TRS file in memory."""

from pathlib import Path

from pydantic import SerializeAsAny

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


class Transcription(TrsprocModel):
    trs_file_path: Path
    speakers: list[Speaker]
    topics: list[Topic]
    turns: list[SpeechTurn]
    trs_episode: TRSEpisode  # TODO: make optional when converting to TRS from other formats
    trs_trans: TRSTrans  # TODO: make optional when converting to TRS from other formats

    @property
    def audio_file_path(self) -> Path | None:
        file_path = self.trs_file_path.with_suffix(".wav")
        if not file_path.exists():
            return
        return file_path.absolute()

    @property
    def all_text(self) -> str:
        return " ".join([turn.text for turn in self.turns])

    @property
    def nb_tokens(self) -> int:
        return len(self.all_text)  # TODO : adapt for jkz alphabets

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
    def languages(self) -> list[str]:
        return [
            event.desc
            for turn in self.turns
            for event in turn.content
            if isinstance(event, Event)
            if event.type == "language" and event.extent != "end"
        ]

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
                if isinstance(event, Event) and event.desc == "pi"
            ]
        )
