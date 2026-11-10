from trsproc.models import Event, SpeakerType, Transcription, TrsprocModel, Utterance


class NamedEntity(TrsprocModel):
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


def clean_ne_from_trs(transcription: Transcription) -> Transcription:
    """Remove Named Entity annotations from the Transcription.

    Args:
        transcription: A :class:`Transcription` instance from the TRS file.

    Returns:
        transcription: A new :class:`Transcription` instance with deleted entities `Event`.
    """
    ne_rank = 0
    trs_turn_idx = 1
    current_trs_turn = transcription.turns[0].trs_turn

    for speechturn in transcription.turns:
        if speechturn.trs_turn != current_trs_turn:
            current_trs_turn = speechturn.trs_turn
            trs_turn_idx += 1

        start_idx = None
        for i, element in enumerate(speechturn.content):
            if not (isinstance(element, Event) and element.type == "entities"):
                continue

            if element.extent == "begin":
                start_idx = i
            elif element.extent == "end" and start_idx is not None:
                ne_rank += 1
                segment_text = " ".join(
                    [
                        utterance.text
                        for utterance in speechturn.content
                        if isinstance(utterance, Utterance)
                    ]
                )
                speechturn.content = [
                    Utterance(text=segment_text, speaker=speechturn.speakers[0])
                ]  # override the speechturn content
                break

    return transcription


def create_trs_from_ne_table(
    trs_filename: str, transcription: Transcription, table_info: list
) -> Transcription:
    """Pre-annotates the input TRS using the table created with the
    `ne` command as a custom annotation dictionary.
    Any named entity present in the input TRS but no longer in the annotation
    custom annotation dictionary is removed from the TRS.

    Args:
        trs_filename: A string trs filename.
        table_info: A list of dictionaries with entities information.
        transcription: A :class:`Transcription` instance from the TRS file.

    Returns:
        transcription: A new :class:`Transcription` instance with pre-annotated entities.
    """
    transcription_without_entities = clean_ne_from_trs(transcription)
    transcription = transcription_without_entities

    for name_entity in table_info:
        if trs_filename == name_entity["file_name"]:
            segment_start = name_entity["segment_start"]
            segment_end = name_entity["segment_end"]
            ne_content = name_entity["ne_content"]
            ne_class = name_entity["ne_class"]

            try:
                _, speechturn = transcription.get_turn_with_index(segment_start, segment_end)
            except KeyError:
                continue

            content = speechturn.content
            for i, element in enumerate(content):
                if not isinstance(element, Utterance):
                    continue

                previous_content = content[i - 1] if i > 0 else None
                if (
                    isinstance(previous_content, Event)
                    and previous_content.type == "entities"
                    and previous_content.extent == "begin"
                ):
                    continue

                before_text, found_ne, after_text = element.text.partition(ne_content)
                if not found_ne:
                    continue

                entity_elements = [
                    Utterance(text=before_text, speaker=element.speaker),
                    Event(desc=ne_class, type="entities", extent="begin"),
                    Utterance(text=ne_content, speaker=element.speaker),
                    Event(desc=ne_class, type="entities", extent="end"),
                    Utterance(text=after_text, speaker=element.speaker),
                ]

                content[i : i + 1] = [
                    e for e in entity_elements if not (isinstance(e, Utterance) and not e.text)
                ]

                speechturn.content = content
                break
    return transcription
