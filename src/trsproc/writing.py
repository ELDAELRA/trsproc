import csv
from pathlib import Path

from lxml import etree

from trsproc.dtd import _load_dtd
from trsproc.models import Transcription, TrsprocModel, Utterance


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


def write_trs(transcription: Transcription, file_name: str | Path) -> None:
    dtd = _load_dtd()
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
        dtd.assertValid(root)
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

    dtd.assertValid(root)
    xml = etree.tostring(
        root,
        pretty_print=True,
        xml_declaration=True,
        encoding="utf-8",
        doctype='<!DOCTYPE Trans SYSTEM "trans-14.dtd">',
    )
    with open(file_name, "wb") as out_stream:
        out_stream.write(xml)


def write_nes_to_tsv(entities: list, file_path: Path) -> None:
    with open(file_path, "w") as file:
        writer = csv.writer(file, delimiter="\t")
        if entities:
            writer.writerow(entities[0].model_dump().keys())
        for i, ent in enumerate(entities):
            ent.ne_rank = i + 1
            writer.writerow(ent.model_dump().values())
