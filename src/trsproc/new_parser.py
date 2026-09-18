from pathlib import Path

from lxml import etree
from lxml.etree import _Attrib, _Element, _ElementTree

from trsproc.dtd import _load_lenient_dtd
from trsproc.models import (
    Background,
    Comment,
    Event,
    Speaker,
    SpeechTurn,
    SpeechTurnElement,
    Topic,
    Transcription,
    TRSEpisode,
    TRSSection,
    TRSTrans,
    TRSTurn,
    Utterance,
)


def format_text(text: str) -> str:
    return " ".join(text.strip().split())


def clean_attrib(attribs: _Attrib) -> dict[str, str]:
    """Ommit empty xml attributes"""
    return {k: v for k, v in attribs.items() if v != ""}


def extract_turn_speakers(turn_elem: _Element, speakers_dict: dict[str, Speaker]) -> list[Speaker]:
    speakers_str = turn_elem.get("speaker")
    if speakers_str is None:
        return []

    speakers_ids = speakers_str.split()
    return [speakers_dict[speaker_id] for speaker_id in speakers_ids]


def parse_inline_element(element: _Element, speakers: list[Speaker]) -> list[SpeechTurnElement]:
    elems = []
    speaker = speakers[0] if len(speakers) == 1 else None

    match element.tag:
        case "Event":
            elems.append(Event.model_validate(clean_attrib(element.attrib)))
        case "Comment":
            elems.append(Comment.model_validate(clean_attrib(element.attrib)))
        case "Background":
            elems.append(Background.model_validate(clean_attrib(element.attrib)))
        case "Who":
            idx = element.get("nb")
            try:
                speaker = None if idx is None else speakers[int(idx) - 1]  # speakers are 1-indexed
            except IndexError:
                speaker = None

        case _:
            pass

    if element.tail is not None and element.tail.strip():
        elems.append(Utterance(text=format_text(element.tail), speaker=speaker))

    return elems


def parse_turn(
    element: _Element, speakers_dict: dict[str, Speaker], trs_section: TRSSection
) -> list[SpeechTurn]:
    speech_turns = []
    trs_turn = TRSTurn.model_validate(
        clean_attrib(element.attrib), context={"speakers_dict": speakers_dict}
    )
    speaker = trs_turn.speakers[0] if len(trs_turn.speakers) == 1 else None
    rolling_speech_turn = SpeechTurn(
        speakers=trs_turn.speakers,
        start=trs_turn.start,
        end=trs_turn.end,
        content=[],
        trs_turn=trs_turn,
        trs_section=trs_section,
    )

    # First bit of text before any element
    if element.text is not None and element.text.strip():
        rolling_speech_turn.content.append(
            Utterance(text=format_text(element.text), speaker=speaker)
        )

    # Process elements and text following them
    for child in element:
        if child.tag != "Sync":
            rolling_speech_turn.content.extend(
                parse_inline_element(child, rolling_speech_turn.speakers)
            )
            continue

        # Once we find a sync tag, we create a new SpeechTurn object
        sync_time = float(child.get("time"))  # type: ignore (if sync had no time tag, validation would have failed before here)
        rolling_speech_turn.end = sync_time
        if rolling_speech_turn.content:  # ignore empty turns (most Turns start with a Sync)
            speech_turns.append(rolling_speech_turn)

        rolling_speech_turn = SpeechTurn(
            speakers=trs_turn.speakers,
            start=sync_time,
            end=trs_turn.end,
            content=[],
            trs_turn=trs_turn,
            trs_section=trs_section,
        )

        # Last bit of text after the last Sync
        if child.tail is not None and child.tail.strip():
            rolling_speech_turn.content.append(
                Utterance(text=format_text(child.tail.strip()), speaker=speaker)
            )

    if rolling_speech_turn.content:
        speech_turns.append(rolling_speech_turn)

    return speech_turns


def parse_speakers(tree: _ElementTree) -> dict[str, Speaker]:
    speakers = tree.findall(".//Speaker")
    return {  # type: ignore (if speaker had no id, validation would have failed before here)
        speaker.get("id"): Speaker.model_validate(clean_attrib(speaker.attrib))
        for speaker in speakers
    }


def parse_topics(tree: _ElementTree) -> dict[str, Topic]:
    topics = tree.findall(".//Topic")
    return {  # type: ignore (if topic had no id, validation would have failed before here)
        topic.get("id"): Topic.model_validate(clean_attrib(topic.attrib)) for topic in topics
    }


def parse_trs_file(file_path: str | Path) -> Transcription:
    dtd = _load_lenient_dtd()
    tree = etree.parse(file_path)
    dtd.assertValid(tree)
    root = tree.getroot()
    speakers_dict = parse_speakers(tree)
    speakers = list(speakers_dict.values())
    topics_dict = parse_topics(tree)
    topics = list(topics_dict.values())
    episode = root.find("Episode")
    trs_episode = TRSEpisode.model_validate(clean_attrib(episode.attrib))  # type: ignore (if there were no episode, lxml would have thrown an error)
    trs_trans = TRSTrans.model_validate(clean_attrib(root.attrib))

    transcription = Transcription(
        trs_file_path=Path(file_path),
        speakers=speakers,
        topics=topics,
        turns=[],
        trs_episode=trs_episode,
        trs_trans=trs_trans,
    )

    for section in root.findall(".//Section"):
        trs_section = TRSSection.model_validate(
            clean_attrib(section.attrib), context={"topics_dict": topics_dict}
        )
        for turn in section.findall(".//Turn"):
            transcription.turns.extend(parse_turn(turn, speakers_dict, trs_section))

    return transcription
