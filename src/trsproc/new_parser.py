import csv
from functools import lru_cache
from importlib.resources import files
from pathlib import Path

from lxml import etree
from lxml.etree import _Attrib, _Element, _ElementTree

from trsproc.models import (
    Background,
    Comment,
    Event,
    NamedEntity,
    Speaker,
    SpeechTurn,
    SpeechTurnElement,
    Topic,
    Transcription,
    TRSEpisode,
    TrsprocModel,
    TRSSection,
    TRSTrans,
    TRSTurn,
    Utterance,
)


@lru_cache
def _load_dtd() -> etree.DTD:
    dtd_path = files("trsproc").joinpath("trans-14.dtd")
    with dtd_path.open() as f:
        return etree.DTD(f)


@lru_cache
def _load_lenient_dtd() -> etree.DTD:
    """This is a more lenient version of the dtd, that only cares about the order of the elements.
    All closed value sets for attribs are turned into plain CDATA,
    because optional invalid attribs fallback to None
    (see [`TrsprocModel._drop_invalid_if_optional`][trsproc.models.TrsprocModel._drop_invalid_if_optional])
    """
    dtd_path = files("trsproc").joinpath("lenient.dtd")
    with dtd_path.open() as f:
        return etree.DTD(f)


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
                speaker = speakers[int(idx) - 1]  # Speakers are 1-indexed
            except (ValueError, IndexError):
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
        sync_time = float(child.get("time"))
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
    return {
        speaker.get("id"): Speaker.model_validate(clean_attrib(speaker.attrib))
        for speaker in speakers
    }


def parse_topics(tree: _ElementTree) -> dict[str, Topic]:
    topics = tree.findall(".//Topic")
    return {topic.get("id"): Topic.model_validate(clean_attrib(topic.attrib)) for topic in topics}


def extract_nes_from_transcription(transcription: Transcription) -> list[NamedEntity]:
    entities = []
    start_idx = None
    ne_rank = 0
    trs_turn_idx = 1
    current_trs_turn = transcription.turns[0].trs_turn

    for speechturn in transcription.turns:
        if speechturn.trs_turn != current_trs_turn:
            current_trs_turn = speechturn.trs_turn
            trs_turn_idx += 1
        for i, element in enumerate(speechturn.content):
            if not (isinstance(element, Event) and element.type == "entities"):
                continue

            if element.extent == "begin":
                start_idx = i
            elif element.extent == "end" and start_idx is not None:
                ne_rank += 1
                ne_text = " ".join(
                    [
                        utterance.text
                        for utterance in speechturn.content[start_idx:i]
                        if isinstance(utterance, Utterance)
                    ]
                )
                segment_text = " ".join(
                    [
                        utterance.text
                        for utterance in speechturn.content
                        if isinstance(utterance, Utterance)
                    ]
                )
                speaker = speechturn.speakers[0].name if speechturn.speakers else ""
                speaker_sex = (
                    speechturn.speakers[0].type
                    if (speechturn.speakers and speechturn.speakers[0].type is not None)
                    else "unknown"
                )
                entity = NamedEntity(
                    file_name=str(transcription.trs_file_path.name),
                    file_path=str(transcription.trs_file_path.absolute()),
                    ne_rank=ne_rank,
                    ne_class=element.desc,
                    ne_content=ne_text,
                    segment_rank=trs_turn_idx,
                    segment_content=segment_text,
                    segment_start=speechturn.start,
                    segment_end=speechturn.end,
                    segment_duration=round(speechturn.end - speechturn.start, 2),
                    speaker=speaker,
                    speaker_sex=speaker_sex,
                )
                entities.append(entity)

                start_idx = None

    return entities


def write_nes_to_tsv(entities: list, file_path: Path) -> None:
    with open(file_path, "w") as file:
        writer = csv.writer(file, delimiter="\t")
        if entities:
            writer.writerow(entities[0].model_dump().keys())
        for i, ent in enumerate(entities):
            ent.ne_rank = i + 1
            writer.writerow(ent.model_dump().values())


def to_xml_attribs(model: TrsprocModel, exclude: set[str] | None = None) -> dict[str, str]:
    """Helper function to convert supported types to str for xml serialization"""
    dump = model.model_dump(exclude_none=True, exclude=exclude, by_alias=True)
    attribs = {}
    for key, value in dump.items():
        if isinstance(value, float):
            attribs[key] = str(value)
        elif isinstance(value, str):
            attribs[key] = value
        else:
            raise TypeError(f"Unknow type for xml attribute : {key} : {type(value)} : {dump}")
    return attribs


def write_xml(transcription: Transcription, file_name: str) -> None:
    root = etree.Element("Trans", to_xml_attribs(transcription.trs_trans))
    if transcription.speakers:
        speakers_elem = etree.SubElement(root, "Speakers")
        for speaker in transcription.speakers:
            etree.SubElement(speakers_elem, "Speaker", to_xml_attribs(speaker))
    if transcription.topics:
        topics_elem = etree.SubElement(root, "Topics")
        for topic in transcription.topics:
            etree.SubElement(topics_elem, "Topic", to_xml_attribs(topic))

    episode_elem = etree.SubElement(root, "Episode", to_xml_attribs(transcription.trs_episode))

    if not transcription.turns:
        xml = etree.tostring(
            root,
            pretty_print=True,
            xml_declaration=True,
            encoding="utf-8",
            doctype='<!DOCTYPE Trans SYSTEM "trans-14.dtd">',
        )
        with open(file_name, "wb") as out_stream:
            out_stream.write(xml)
        return

    rolling_trs_section = transcription.turns[0].trs_section
    rolling_trs_turn = transcription.turns[0].trs_turn
    section_elem = None
    turn_elem = None
    for speech_turn in transcription.turns:
        if section_elem is None or speech_turn.trs_section is not rolling_trs_section:
            rolling_trs_section = speech_turn.trs_section
            section_attribs = to_xml_attribs(rolling_trs_section, exclude={"topics"})
            if rolling_trs_section.topics:
                section_attribs["topic"] = " ".join(
                    topic.id for topic in rolling_trs_section.topics
                )
            section_elem = etree.SubElement(episode_elem, "Section", section_attribs)
        if turn_elem is None or speech_turn.trs_turn is not rolling_trs_turn:
            rolling_trs_turn = speech_turn.trs_turn
            turn_attribs = to_xml_attribs(rolling_trs_turn, exclude={"speakers"})
            if rolling_trs_turn.speakers:
                turn_attribs["speaker"] = " ".join(
                    speaker.id for speaker in rolling_trs_turn.speakers
                )
            turn_elem = etree.SubElement(section_elem, "Turn", turn_attribs)

        last_tag = etree.SubElement(turn_elem, "Sync", time=str(speech_turn.start))
        for tag in speech_turn.content:
            if isinstance(tag, Utterance):
                if speech_turn.has_overlap:
                    last_tag = etree.SubElement(
                        turn_elem,
                        "Who",
                        nb=speech_turn.get_speaker_idx(tag.speaker.id),  # type: ignore
                    )
                last_tag.tail = tag.text
            else:
                last_tag = etree.SubElement(turn_elem, tag.__class__.__name__, to_xml_attribs(tag))

    xml = etree.tostring(
        root,
        pretty_print=True,
        xml_declaration=True,
        encoding="utf-8",
        doctype='<!DOCTYPE Trans SYSTEM "trans-14.dtd">',
    )
    with open(file_name, "wb") as out_stream:
        out_stream.write(xml)


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
