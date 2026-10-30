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
    ne_rank = 0
    trs_turn_idx = 1
    # A trs file with an empty Episode is valid, but indexing turns[0] used to raise
    # IndexError before anything could be extracted.
    if not transcription.turns:
        return entities
    current_trs_turn = transcription.turns[0].trs_turn

    for speechturn in transcription.turns:
        if speechturn.trs_turn != current_trs_turn:
            current_trs_turn = speechturn.trs_turn
            trs_turn_idx += 1
        # start_idx indexes speechturn.content, so it only means something inside the
        # current speech turn. It used to leak across turns : a begin left open in one turn
        # made the next turn slice its own content with a stale index, which silently
        # produced an empty or wrong entity instead of being ignored.
        start_idx = None
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
