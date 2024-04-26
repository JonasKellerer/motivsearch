import unittest
from pathlib import Path

from MainParser import ParseOption
from Motive import Motive
from MotiveGenerator import MotiveGenerator
from MotivePosition import MotivePosition
from MotiveUnit import MotiveUnitInterval
from Origin import Origin
from PositionInWork import PositionInWork


class MotiveGeneratorTest_DiscoverMotives(unittest.TestCase):
    options = [
        ParseOption.WITH_INVERTED,
        ParseOption.WITH_MIRRORED,
        ParseOption.USE_DIATONIC,
    ]

    def test_single_file_without_min_frequency(self):
        file_path = Path("testData/single_file/input")

        motive_generator = MotiveGenerator(
            min_frequency=1,
            max_gap=0,
            max_length=3,
            min_num_sequences=3,
            max_num_sequences=3,
        )

        motives = motive_generator.discover_motives(
            file_path=file_path, options=self.options
        )

        self.assertEqual(len(motives), 8)

        self.assertEqual(motives[0].frequency, 6)
        self.assertEqual(motives[0].sequence[0].name, "2")
        self.assertEqual(motives[0].sequence[1].name, "2")
        self.assertEqual(motives[0].sequence[2].name, "2")
        self.assertEqual(motives[0].positions[0].origin.note_number, 0)
        self.assertEqual(motives[0].positions[1].origin.note_number, 1)
        self.assertEqual(motives[0].positions[2].origin.note_number, 2)
        self.assertEqual(motives[0].positions[3].origin.note_number, 3)
        self.assertEqual(motives[0].positions[4].origin.note_number, 8)
        self.assertEqual(motives[0].positions[5].origin.note_number, 17)

        self.assertEqual(
            motives[0].positions[0].position_in_work, PositionInWork.ORIGINAL
        )
        self.assertEqual(
            motives[0].positions[5].position_in_work, PositionInWork.INVERTED
        )

        self.assertEqual(motives[1].frequency, 2)
        self.assertEqual(str(motives[1].sequence), "[2, 2, -3]")
        self.assertEqual(motives[2].frequency, 1)
        self.assertEqual(str(motives[2].sequence), "[2, -3, -4]")
        self.assertEqual(motives[3].frequency, 1)
        self.assertEqual(str(motives[3].sequence), "[2, -3, 1]")
        self.assertEqual(motives[4].frequency, 1)
        self.assertEqual(str(motives[4].sequence), "[-3, 1, -2]")
        self.assertEqual(motives[5].frequency, 1)
        self.assertEqual(str(motives[5].sequence), "[-3, -4, 2]")
        self.assertEqual(motives[6].frequency, 1)
        self.assertEqual(str(motives[6].sequence), "[-4, 2, 2]")
        self.assertEqual(motives[7].frequency, 1)
        self.assertEqual(str(motives[7].sequence), "[1, -2, -2]")

    def test_single_file_with_min_frequency(self):
        file_path = Path("testData/single_file/input")

        motive_generator = MotiveGenerator(
            min_frequency=2,
            max_gap=0,
            max_length=3,
            min_num_sequences=3,
            max_num_sequences=3,
        )

        motives = motive_generator.discover_motives(
            file_path=file_path, options=self.options
        )

        self.assertEqual(len(motives), 2)

    def test_chromatic_variation(self):
        file_path = Path("testData/chromatic_variation/input")

        motive_generator = MotiveGenerator(
            min_frequency=1,
            max_gap=0,
            max_length=3,
            min_num_sequences=3,
            max_num_sequences=3,
        )

        motives = motive_generator.discover_motives(
            file_path=file_path, options=self.options
        )

        self.assertEqual(len(motives), 15)

    def test_mirrored(self):
        file_path = Path("testData/mirrored")

        motive_generator = MotiveGenerator(
            min_frequency=1,
            max_gap=0,
            max_length=3,
            min_num_sequences=3,
            max_num_sequences=3,
        )

        motives = motive_generator.discover_motives(
            file_path=file_path, options=self.options
        )

        self.assertEqual(len(motives), 1)

        self.assertEqual(motives[0].frequency, 2)
        self.assertEqual(str(motives[0].sequence), "[1, 2, 4]")

    def test_mirror_and_inverted_variation(self):
        file_path = Path("testData/mirror_and_inverted/input")

        motive_generator = MotiveGenerator(
            min_frequency=1,
            max_gap=0,
            max_length=3,
            min_num_sequences=3,
            max_num_sequences=3,
        )

        motives = motive_generator.discover_motives(
            file_path=file_path, options=self.options
        )

        self.assertEqual(len(motives), 13)

        expected_motives = [
            {"frequency": 2, "sequence": "[5, -3, -3]"},
            {"frequency": 1, "sequence": "[2, 2, -5]"},
            {"frequency": 1, "sequence": "[2, -5, 3]"},
            {"frequency": 1, "sequence": "[-3, -3, 3]"},
            {"frequency": 1, "sequence": "[3, 3, 4]"},
            {"frequency": 1, "sequence": "[-3, 3, -2]"},
            {"frequency": 4, "sequence": "[-3, 2, 2]"},
            {"frequency": 1, "sequence": "[3, 4, 1]"},
            {"frequency": 1, "sequence": "[-2, -2, -2]"},
            {"frequency": 1, "sequence": "[-2, -2, 7]"},
            {"frequency": 1, "sequence": "[-2, 7, -8]"},
            {"frequency": 1, "sequence": "[4, 1, 2]"},
            {"frequency": 1, "sequence": "[1, 2, 2]"},
        ]

        for i, expected_motive in enumerate(expected_motives):
            self.assertEqual(motives[i].frequency, expected_motive["frequency"])
            self.assertEqual(str(motives[i].sequence), expected_motive["sequence"])

    def test_rhythm_variation(self):
        file_path = Path("testData/rythm_variation/input")

        motive_generator = MotiveGenerator(
            min_frequency=1,
            max_gap=0,
            max_length=3,
            min_num_sequences=3,
            max_num_sequences=3,
        )

        motives = motive_generator.discover_motives(
            file_path=file_path, options=self.options
        )

        self.assertEqual(len(motives), 11)

        self.assertEqual(motives[0].frequency, 2)
        self.assertEqual(motives[3].frequency, 2)
        self.assertEqual(motives[5].frequency, 2)

    def test_basic(self):
        file_path = Path("testData/basic/input")

        motive_generator = MotiveGenerator(
            min_frequency=1,
            max_gap=0,
            max_length=3,
            min_num_sequences=3,
            max_num_sequences=3,
        )

        motives = motive_generator.discover_motives(
            file_path=file_path, options=self.options
        )

        self.assertEqual(len(motives), 2)

        self.assertEqual(motives[0].frequency, 1)
        self.assertEqual(motives[1].frequency, 1)

    def test_chromatic(self):
        file_path = Path("testData/chromatic/input")

        motive_generator = MotiveGenerator(
            min_frequency=1,
            max_gap=0,
            max_length=3,
            min_num_sequences=3,
            max_num_sequences=3,
        )

        motives = motive_generator.discover_motives(
            file_path=file_path, options=self.options
        )

        self.assertEqual(len(motives), 1)

        self.assertEqual(motives[0].frequency, 2)

    def test_breaks(self):
        file_path = Path("testData/breaks/input")

        motive_generator = MotiveGenerator(
            min_frequency=1,
            max_gap=0,
            max_length=3,
            min_num_sequences=3,
            max_num_sequences=3,
        )

        motives = motive_generator.discover_motives(
            file_path=file_path, options=self.options
        )

        self.assertEqual(len(motives), 0)

    def test_multiple_parts(self):
        file_path = Path("testData/multiple_parts/input")

        motive_generator = MotiveGenerator(
            min_frequency=1,
            max_gap=0,
            max_length=3,
            min_num_sequences=3,
            max_num_sequences=3,
        )

        motives = motive_generator.discover_motives(
            file_path=file_path, options=self.options
        )

        self.assertEqual(len(motives), 4)

        expected_motives = [
            {"frequency": 1, "sequence": "[1, 2, 4]"},
            {"frequency": 1, "sequence": "[-3, -2, 1]"},
            {"frequency": 1, "sequence": "[-3, 3, 1]"},
            {"frequency": 1, "sequence": "[3, -3, 3]"},
        ]

        for i, expected_motive in enumerate(expected_motives):
            self.assertEqual(motives[i].frequency, expected_motive["frequency"])
            self.assertEqual(str(motives[i].sequence), expected_motive["sequence"])

    def test_multiple_voices_in_one_part(self):
        file_path = Path("testData/multiple_voices_in_one_part")

        motive_generator = MotiveGenerator(
            min_frequency=1,
            max_gap=0,
            max_length=3,
            min_num_sequences=3,
            max_num_sequences=3,
        )

        motives = motive_generator.discover_motives(
            file_path=file_path, options=self.options
        )

        self.assertEqual(len(motives), 4)

        expected_motives = [
            {"frequency": 1, "sequence": "[1, 1, 1]"},
            {"frequency": 1, "sequence": "[1, 1, 2]"},
            {"frequency": 1, "sequence": "[1, 2, 4]"},
            {"frequency": 1, "sequence": "[-3, -2, 1]"},
        ]

        for i, expected_motive in enumerate(expected_motives):
            self.assertEqual(motives[i].frequency, expected_motive["frequency"])
            self.assertEqual(str(motives[i].sequence), expected_motive["sequence"])

    def test_multiple_parts_multiple_voices(self):
        file_path = Path("testData/multiple_parts_multiple_voices")

        motive_generator = MotiveGenerator(
            min_frequency=1,
            max_gap=0,
            max_length=3,
            min_num_sequences=3,
            max_num_sequences=3,
        )

        motives = motive_generator.discover_motives(
            file_path=file_path, options=self.options
        )

        self.assertEqual(len(motives), 6)

        expected_motives = [
            {"frequency": 1, "sequence": "[1, 1, 1]"},
            {"frequency": 1, "sequence": "[1, 1, 2]"},
            {"frequency": 1, "sequence": "[1, 2, 4]"},
            {"frequency": 1, "sequence": "[-3, -2, 1]"},
            {"frequency": 1, "sequence": "[-3, 3, 1]"},
            {"frequency": 1, "sequence": "[3, -3, 3]"},
        ]

        for i, expected_motive in enumerate(expected_motives):
            self.assertEqual(motives[i].frequency, expected_motive["frequency"])
            self.assertEqual(str(motives[i].sequence), expected_motive["sequence"])

    def test_one_accord_per_note(self):
        file_path = Path("testData/one_accord_per_note")

        motive_generator = MotiveGenerator(
            min_frequency=1,
            max_gap=0,
            max_length=3,
            min_num_sequences=3,
            max_num_sequences=3,
        )

        motives = motive_generator.discover_motives(
            file_path=file_path, options=self.options
        )

        self.assertEqual(len(motives), 2)

        expected_motives = [
            {"frequency": 1, "sequence": "[1, 2, 4]"},
            {"frequency": 1, "sequence": "[-3, -2, 1]"},
        ]

        for i, expected_motive in enumerate(expected_motives):
            self.assertEqual(motives[i].frequency, expected_motive["frequency"])
            self.assertEqual(str(motives[i].sequence), expected_motive["sequence"])

    def test_ties(self):
        file_path = Path("testData/ties")

        motive_generator = MotiveGenerator(
            min_frequency=1,
            max_gap=0,
            max_length=3,
            min_num_sequences=3,
            max_num_sequences=3,
        )

        motives = motive_generator.discover_motives(
            file_path=file_path, options=self.options
        )

        self.assertEqual(len(motives), 1)

        expected_motives = [
            {"frequency": 1, "sequence": "[1, 2, 4]"},
        ]

        for i, expected_motive in enumerate(expected_motives):
            self.assertEqual(motives[i].frequency, expected_motive["frequency"])
            self.assertEqual(str(motives[i].sequence), expected_motive["sequence"])

    def test_multiple_pieces_same_motives(self):
        file_path = Path("testData/multiple_pieces/same_motives")

        motive_generator = MotiveGenerator(
            min_frequency=1,
            max_gap=0,
            max_length=3,
            min_num_sequences=3,
            max_num_sequences=3,
        )

        motives = motive_generator.discover_motives(
            file_path=file_path, options=self.options
        )

        self.assertEqual(len(motives), 2)

        expected_motives = [
            {"frequency": 2, "sequence": "[1, 2, 4]"},
            {"frequency": 2, "sequence": "[-3, -2, 1]"},
        ]

        for i, expected_motive in enumerate(expected_motives):
            self.assertEqual(motives[i].frequency, expected_motive["frequency"])
            self.assertEqual(str(motives[i].sequence), expected_motive["sequence"])

    def test_multiple_pieces_different_motives(self):
        file_path = Path("testData/multiple_pieces/different_motives")

        motive_generator = MotiveGenerator(
            min_frequency=1,
            max_gap=0,
            max_length=3,
            min_num_sequences=3,
            max_num_sequences=3,
        )

        motives = motive_generator.discover_motives(
            file_path=file_path, options=self.options
        )

        self.assertEqual(len(motives), 4)

        expected_motives = [
            {"frequency": 1, "sequence": "[4, -3, 4]"},
            {"frequency": 1, "sequence": "[-3, -2, 1]"},
            {"frequency": 1, "sequence": "[7, -10, 1]"},
            {"frequency": 1, "sequence": "[1, 2, 4]"},
        ]

        for i, expected_motive in enumerate(expected_motives):
            self.assertEqual(motives[i].frequency, expected_motive["frequency"])
            self.assertEqual(str(motives[i].sequence), expected_motive["sequence"])

    def test_multiple_pieces_same_motive_in_inverted(self):
        file_path = Path("testData/multiple_pieces/same_motive_in_inverted")

        motive_generator = MotiveGenerator(
            min_frequency=1,
            max_gap=0,
            max_length=3,
            min_num_sequences=3,
            max_num_sequences=3,
        )

        motives = motive_generator.discover_motives(
            file_path=file_path, options=self.options
        )

        self.assertEqual(len(motives), 2)

        # welches stück auch immer zu erst eingelesen wird, das wird als original genommen?
        expected_motives = [
            {"frequency": 2, "sequence": "[1, 2, 4]"},
            {"frequency": 2, "sequence": "[3, 2, 1]"},
        ]

        for i, expected_motive in enumerate(expected_motives):
            self.assertEqual(motives[i].frequency, expected_motive["frequency"])
            self.assertEqual(str(motives[i].sequence), expected_motive["sequence"])

    def test_multiple_pieces_same_motive_in_mirrored(self):
        file_path = Path("testData/multiple_pieces/same_motive_in_mirrored")

        motive_generator = MotiveGenerator(
            min_frequency=1,
            max_gap=0,
            max_length=3,
            min_num_sequences=3,
            max_num_sequences=3,
        )

        motives = motive_generator.discover_motives(
            file_path=file_path, options=self.options
        )

        self.assertEqual(len(motives), 2)

        # welches stück auch immer zu erst eingelesen wird, das wird als original genommen?
        expected_motives = [
            {"frequency": 2, "sequence": "[1, 2, 4]"},
            {"frequency": 2, "sequence": "[1, -2, -3]"},
        ]

        for i, expected_motive in enumerate(expected_motives):
            self.assertEqual(motives[i].frequency, expected_motive["frequency"])
            self.assertEqual(str(motives[i].sequence), expected_motive["sequence"])


class MotiveGeneratorTest_MergeInvertedAndMirrored(unittest.TestCase):
    motive_generator = MotiveGenerator(
        min_frequency=1,
        max_gap=0,
        max_length=3,
        min_num_sequences=3,
        max_num_sequences=3,
    )

    def test_merge_inverted_and_mirrored(self):

        basic_motive = Motive(
            positions=[
                MotivePosition(
                    position=0,
                    position_in_work=PositionInWork.ORIGINAL,
                    origin=Origin(
                        piece_title="piece",
                        part_id="partId",
                        voice_id="0",
                        measure_number=0,
                        note_number=0,
                    ),
                    length=3,
                )
            ],
            sequence=[
                MotiveUnitInterval(
                    interval=2,
                    origin=Origin(
                        piece_title="piece",
                        part_id="partId",
                        voice_id="0",
                        measure_number=0,
                        note_number=0,
                    ),
                    position_in_work=PositionInWork.ORIGINAL,
                ),
                MotiveUnitInterval(
                    interval=2,
                    origin=Origin(
                        piece_title="piece",
                        part_id="partId",
                        voice_id="0",
                        measure_number=0,
                        note_number=1,
                    ),
                    position_in_work=PositionInWork.ORIGINAL,
                ),
                MotiveUnitInterval(
                    interval=2,
                    origin=Origin(
                        piece_title="piece",
                        part_id="partId",
                        voice_id="0",
                        measure_number=0,
                        note_number=2,
                    ),
                    position_in_work=PositionInWork.ORIGINAL,
                ),
            ],
            frequency=1,
        )

        inverted_motive = Motive(
            positions=[
                MotivePosition(
                    position=3,
                    position_in_work=PositionInWork.ORIGINAL,
                    origin=Origin(
                        piece_title="piece",
                        part_id="partId",
                        voice_id="0",
                        measure_number=1,
                        note_number=3,
                    ),
                    length=3,
                )
            ],
            sequence=[
                MotiveUnitInterval(
                    interval=-2,
                    origin=Origin(
                        piece_title="piece",
                        part_id="partId",
                        voice_id="0",
                        measure_number=1,
                        note_number=3,
                    ),
                    position_in_work=PositionInWork.ORIGINAL,
                ),
                MotiveUnitInterval(
                    interval=-2,
                    origin=Origin(
                        piece_title="piece",
                        part_id="partId",
                        voice_id="0",
                        measure_number=1,
                        note_number=4,
                    ),
                    position_in_work=PositionInWork.ORIGINAL,
                ),
                MotiveUnitInterval(
                    interval=-2,
                    origin=Origin(
                        piece_title="piece",
                        part_id="partId",
                        voice_id="0",
                        measure_number=1,
                        note_number=5,
                    ),
                    position_in_work=PositionInWork.ORIGINAL,
                ),
            ],
            frequency=1,
        )

        merged_motives = self.motive_generator.merge_inverted_and_mirrored(
            [basic_motive, inverted_motive]
        )

        self.assertEqual(len(merged_motives), 1)
        self.assertEqual(merged_motives[0].frequency, 2)
