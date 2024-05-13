import unittest

from MotivePosition import MotivePosition
from MotiveSequence import PositionSequence
from Origin import Origin
from PositionInWork import PositionInWork


class PositionSequenceTest(unittest.TestCase):

    def test_constructor_with_one_entry(self):
        some_position = MotivePosition(
            position=0,
            length=3,
            origin=Origin(
                piece_title="piece",
                part_id="partId",
                voice_id="0",
                measure_number=0,
                note_number=0,
            ),
            position_in_work=PositionInWork.ORIGINAL,
        )

        motive_sequence = PositionSequence(sequence=[some_position])

        self.assertEqual(len(motive_sequence.sequence), 1)

    def test_constructor_with_multiple_same_entries(self):
        some_position = MotivePosition(
            position=0,
            length=3,
            origin=Origin(
                piece_title="piece",
                part_id="partId",
                voice_id="0",
                measure_number=0,
                note_number=0,
            ),
            position_in_work=PositionInWork.ORIGINAL,
        )

        motive_sequence = PositionSequence(
            sequence=[some_position, some_position, some_position]
        )

        self.assertEqual(len(motive_sequence.sequence), 1)

    def test_merge_with_same_position(self):
        some_position = MotivePosition(
            position=0,
            length=3,
            origin=Origin(
                piece_title="piece",
                part_id="partId",
                voice_id="0",
                measure_number=0,
                note_number=0,
            ),
            position_in_work=PositionInWork.ORIGINAL,
        )

        motive_sequence = PositionSequence(sequence=[some_position])
        other_sequence = PositionSequence(sequence=[some_position])

        motive_sequence.merge(other_sequence)
        self.assertEqual(len(motive_sequence.sequence), 1)

    def test_merge_with_different_position(self):
        some_position = MotivePosition(
            position=0,
            length=3,
            origin=Origin(
                piece_title="piece",
                part_id="partId",
                voice_id="0",
                measure_number=0,
                note_number=0,
            ),
            position_in_work=PositionInWork.ORIGINAL,
        )

        other_position = MotivePosition(
            position=3,
            length=3,
            origin=Origin(
                piece_title="piece",
                part_id="partId",
                voice_id="0",
                measure_number=0,
                note_number=3,
            ),
            position_in_work=PositionInWork.ORIGINAL,
        )

        motive_sequence = PositionSequence(sequence=[some_position])
        other_sequence = PositionSequence(sequence=[some_position])

        motive_sequence.merge(other_sequence)
        self.assertEqual(len(motive_sequence.sequence), 1)


if __name__ == "__main__":
    unittest.main()
