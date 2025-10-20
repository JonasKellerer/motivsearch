import logging
from dataclasses import dataclass
from typing import List, Optional

from music21 import stream, chord
from music21.harmony import Harmony
from music21.note import Rest, GeneralNote

from ParseOptions import ParseOptions, ChordTreatment
from Voice import Voice
from music21.stream import Part as Part21

@dataclass
class Part:
    id: str
    voices: List[Voice]

    @classmethod
    def parse(cls, part: Part21, unique_id: str, options: Optional[ParseOptions] = None) -> "Part":
        if options is None:
            options = ParseOptions()

        id = str(part.id) + "_" + str(unique_id)
        logging.info(f"Extracting part with {id} from music21 part id {part.id}")
        part.stripTies(inPlace=True)

        voices = extract_voices(part, extrac_voice_ids(part), options=options)

        logging.debug(f"Removing rests from {id} which are shorter than {options.rest_treatment}")
        for voice in voices:
            voice.remove_rests(options.rest_treatment)

        return cls(id=id, voices=voices)


def extract_voices(part: Part21, voice_ids: List[str], options: Optional[ParseOptions] = None) -> List[Voice]:
    part_data = {voice_id: [] for voice_id in voice_ids}

    for i, measure in enumerate(part.getElementsByClass(stream.Measure)):
        if len(measure.voices) == 0:
            for note in measure.notesAndRests:
                if isinstance(note, Harmony):
                    continue
                part_data[voice_ids[0]].append(chord_treatment(note, options))
            for voice in voice_ids[1:]:
                part_data[voice].append(
                    Rest(quarterLength=measure.barDuration.quarterLength)
                )

        for voice in measure.voices:
            for note in voice.notesAndRests:
                part_data[voice.id].append(chord_treatment(note, options))

    return [Voice(voice_id, part_data[voice_id]) for voice_id in voice_ids]


def extrac_voice_ids(part: Part21) -> List[str]:
    voice_ids = []
    for measure in part.getElementsByClass(stream.Measure):
        for voice in measure.getElementsByClass(stream.Voice):
            if voice.id not in voice_ids:
                voice_ids.append(voice.id)
    if len(voice_ids) == 0:
        voice_ids.append("0")

    return voice_ids


def chord_treatment(note: GeneralNote, options: Optional[ParseOptions] = None) -> GeneralNote:
    if options is None:
        return use_only_highest_note(note)

    if options.chord_treatment is ChordTreatment.HIGHEST:
        return use_only_highest_note(note)
    elif options.chord_treatment is ChordTreatment.LOWEST:
        return use_only_lowest_note(note)
    elif options.chord_treatment is ChordTreatment.REMOVE:
        return replace_with_same_length_rest(note)

    return use_only_highest_note(note)

def use_only_highest_note(note: GeneralNote) -> GeneralNote:
    if isinstance(note, chord.Chord):
        return note.sortAscending()[-1]
    return note

def use_only_lowest_note(note: GeneralNote) -> GeneralNote:
    if isinstance(note, chord.Chord):
        return note.sortAscending()[0]
    return note

def replace_with_same_length_rest(note: GeneralNote) ->GeneralNote:
    if isinstance(note, chord.Chord):
        return Rest(quarterLength=note.quarterLength)
    return note

