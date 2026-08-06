from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, SerializeAsAny, ValidationInfo, field_validator

SectionType = Literal["report", "nontrans", "filler"]
SpeakerType = Literal[
    "male", "female", "child", "unknown"
]  # unknown is not in dtd, but still parseable by Transcriber
SpeakerDialect = Literal["native", "nonnative"]
SpeakerScope = Literal["local", "global"]
SpeakerCheck = Literal["yes", "no"]
EventType = Literal["noise", "lexical", "pronounce", "language", "entities"]
EventExtent = Literal["begin", "end", "previous", "next", "instantaneous"]
TurnMode = Literal["spontaneous", "planned"]
TurnFidelity = Literal["high", "medium", "low"]
TurnChannel = Literal["telephone", "studio"]


class StrictModel(BaseModel):
    """A BaseModel that also runs validation when overwritting a property"""

    model_config = ConfigDict(validate_assignment=True)


class TRSEpisode(StrictModel):
    program: str | None = None
    air_date: str | None = None


class TRSSection(StrictModel):
    """Only used to write trs back, we don't care about sections in the internal representation,
    we only focus on minimal SpeechTurns"""

    type: SectionType = "report"
    topics: list[Topic] = Field(validation_alias="topic", default=[])
    start: float = Field(alias="startTime")
    end: float = Field(alias="endTime")

    @field_validator("topics", mode="before")
    @classmethod
    def resolve_topic(cls, value: str | None, info: ValidationInfo) -> list[Topic]:
        if not value:
            return []
        topics_dict = (info.context or {}).get("topics_dict", {})
        try:
            return [topics_dict[tid] for tid in value.split()]
        except KeyError:
            raise ValueError(f"Undefined topic id: {value!r}") from None


class TRSTurn(StrictModel):
    """Same as TRSSection"""

    speakers: list[Speaker] = Field(validation_alias="speaker", default=[])
    start: float = Field(alias="startTime")
    end: float = Field(alias="endTime")
    mode: TurnMode | None = None
    fidelity: TurnFidelity | None = None
    channel: TurnChannel | None = None

    @field_validator("speakers", mode="before")
    @classmethod
    def resolve_speakers(cls, value: str | None, info: ValidationInfo) -> list[Speaker]:
        if not value:
            return []
        speakers_dict = (info.context or {}).get("speakers_dict", {})
        try:
            return [speakers_dict[sid] for sid in value.split()]
        except KeyError as e:
            raise ValueError(
                f"Undefined speaker id: {e.args[0]} in speakers dict {speakers_dict}"
            ) from None


class Speaker(StrictModel):
    id: str
    name: str
    type: SpeakerType | None = None
    dialect: SpeakerDialect | None = None
    accent: str | None = None
    check: SpeakerCheck | None = None
    scope: SpeakerScope | None = None


class Topic(StrictModel):
    id: str
    desc: str = ""


class SpeechTurnElement(StrictModel):
    pass


class Event(SpeechTurnElement):
    desc: str = ""
    type: EventType | None = None
    extent: EventExtent | None = None


class Background(SpeechTurnElement):
    time: float
    type: str
    level: str | None = None


class Utterance(SpeechTurnElement):
    text: str
    speaker: Speaker | None = None


class Comment(SpeechTurnElement):
    desc: str


class Vocal(SpeechTurnElement):
    desc: str


class SpeechTurn(StrictModel):
    start: float
    end: float
    speakers: list[Speaker]
    content: SerializeAsAny[
        list[SpeechTurnElement]
    ]  # Without SerializeAsAny, moodel_dump prints an empty object (because that's what SpeechTurnElement declares, but at runtime it can be any child instance)
    trs_turn: TRSTurn
    trs_section: TRSSection

    @property
    def text(self) -> str:
        return " ".join(
            utterance.text for utterance in self.content if isinstance(utterance, Utterance)
        )

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


class TRSTrans(StrictModel):
    audio_filename: str | None = None
    scribe: str | None = None
    xml_lang: str | None = Field(alias="xml:lang", default=None)
    version: str | None = None
    version_date: str | None = None
    elapsed_time: str | None = None


class Transcription(StrictModel):
    trs_file_path: Path
    speakers: list[Speaker]
    topics: list[Topic]
    turns: list[SpeechTurn]
    trs_episode: TRSEpisode
    trs_trans: TRSTrans


class NamedEntity(StrictModel):
    file_name: str
    file_path: str
    ne_rank: int
    ne_class: str
    ne_content: str
    segment_rank: int
    segment_content: str
    segment_start: float
    segment_end: float
    segment_duration: float
    speaker: str
    speaker_sex: SpeakerType
