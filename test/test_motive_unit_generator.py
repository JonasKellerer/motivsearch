import unittest

from music21.note import Rest

from MotiveUnit import Origin, MotiveUnitBreak, RestIntervalType
from MotiveUnitGenerator import MotiveUnitGenerator
from Voice import Voice


class OriginalFromVoice(unittest.TestCase):
    voice_id = "voiceId"

    def create_test_origin(self, position: int) -> Origin:
        return Origin(
            piece_title="testTitle",
            part_id="testPartId",
            voice_id=self.voice_id,
            measure_number=None,
            note_number=position,
        )

    def test_only_rests(self):
        voice = Voice(
            id=self.voice_id,
            notes=[
                Rest(),
                Rest(),
                Rest(),
            ],
        )

        motive_unit_generator = MotiveUnitGenerator(options=[], max_gap=0)

        motive_units = motive_unit_generator.original_from_voice(
            voice=voice, piece_title="testTitle", part_id="testPartId"
        )

        expected = [
            MotiveUnitBreak(RestIntervalType.REST_BEFORE, self.create_test_origin(0)),
            MotiveUnitBreak(RestIntervalType.REST_BEFORE, self.create_test_origin(1)),
        ]

        self.assertListEqual(expected, motive_units)
