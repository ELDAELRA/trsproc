"""
Contains the DTD-mirroring models.
These models are the exact representation of the xml elements dictated by the Transcriber DTD
"""

from typing import Literal

from pydantic import (
    Field,
    ValidationInfo,
    field_validator,
)

from trsproc.models.base import TrsprocModel

SectionType = Literal["report", "nontrans", "filler"]
SpeakerType = Literal["male", "female", "child", "unknown"]
SpeakerDialect = Literal["native", "nonnative"]
SpeakerScope = Literal["local", "global"]
SpeakerCheck = Literal["yes", "no"]
EventType = Literal["noise", "lexical", "pronounce", "language", "entities"]
EventExtent = Literal["begin", "end", "previous", "next", "instantaneous"]
TurnMode = Literal["spontaneous", "planned"]
TurnFidelity = Literal["high", "medium", "low"]
TurnChannel = Literal["telephone", "studio"]


class Speaker(TrsprocModel):
    id: str
    name: str
    type: SpeakerType | None = None
    dialect: SpeakerDialect | None = None
    accent: str | None = None
    check: SpeakerCheck | None = None
    scope: SpeakerScope | None = None


class Topic(TrsprocModel):
    id: str
    desc: str = ""


class SpeechTurnElement(TrsprocModel):
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


class TRSEpisode(TrsprocModel):
    program: str | None = None
    air_date: str | None = None


class TRSSection(TrsprocModel):
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


class TRSTurn(TrsprocModel):
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


class TRSTrans(TrsprocModel):
    audio_filename: str | None = None
    scribe: str | None = None
    xml_lang: str | None = Field(alias="xml:lang", default=None)
    version: str | None = None
    version_date: str | None = None
    elapsed_time: str | None = None
