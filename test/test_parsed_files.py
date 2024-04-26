import unittest
from pathlib import Path

from parameterized import parameterized

from src.MainParser import ParseOption
from src.ParsedFiles import ParsedFile


test_data = [
    (
        "testData/parsing/basic/basic.musicxml",
        ["1", "2", "4", "BreakTo", "BreakFrom", "-3", "-2", "1"],
        ["1", "-2", "-4", "BreakTo", "BreakFrom", "3", "2", "1"],
        ["1", "2", "3", "BreakFrom", "BreakTo", "-4", "-2", "1"],
    ),
    (
        "testData/parsing/basic/breaks.musicxml",
        [
            "BreakTo",
            "BreakFrom",
            "BreakTo",
            "BreakFrom",
            "BreakFrom",
            "BreakTo",
            "BreakFrom",
            "BreakTo",
        ],
        [
            "BreakTo",
            "BreakFrom",
            "BreakTo",
            "BreakFrom",
            "BreakFrom",
            "BreakTo",
            "BreakFrom",
            "BreakTo",
        ],
        [
            "BreakTo",
            "BreakFrom",
            "BreakTo",
            "BreakFrom",
            "BreakFrom",
            "BreakTo",
            "BreakFrom",
            "BreakTo",
        ],
    ),
    (
        "testData/parsing/basic/chromatic.musicxml",
        ["2", "5", "-3", "BreakTo", "BreakFrom", "2", "5", "-3"],
        ["-2", "-5", "3", "BreakTo", "BreakFrom", "-2", "-5", "3"],
        ["3", "-5", "-2", "BreakFrom", "BreakTo", "3", "-5", "-2"],
    ),
    (
        "testData/parsing/basic/with_accord_per_note.musicxml",
        ["1", "2", "4", "BreakTo", "BreakFrom", "-3", "-2", "1"],
        ["1", "-2", "-4", "BreakTo", "BreakFrom", "3", "2", "1"],
        ["1", "2", "3", "BreakFrom", "BreakTo", "-4", "-2", "1"],
    ),
    (
        "testData/parsing/basic/with_multiple_voices_in_one_line.musicxml",
        ["1", "1", "2", "4", "BreakTo", "BreakFrom", "-3", "-2", "1"],
        ["1", "1", "-2", "-4", "BreakTo", "BreakFrom", "3", "2", "1"],
        ["1", "2", "3", "BreakFrom", "BreakTo", "-4", "-2", "1", "1"],
    ),
]


class TestParsedFiles(unittest.TestCase):
    @parameterized.expand(test_data)
    def test_without_options(
        self,
        filename,
        expected_motive_units,
        expected_inverted_units,
        expected_inverted_mirrored_units,
    ):
        options = []

        parsed_file = ParsedFile.parse_file(filename, options)

        motive_units_str = [
            str(motive_unit) for motive_unit in parsed_file.motive_units
        ]

        self.assertListEqual(expected_motive_units, motive_units_str)

    @parameterized.expand(test_data)
    def test_with_inverted(
        self,
        filename,
        expected_motive_units,
        expected_inverted_units,
        expected_inverted_mirrored_units,
    ):
        options = [ParseOption.WITH_INVERTED]
        parsed_file = ParsedFile.parse_file(filename, options)

        motive_units_str = [
            str(motive_unit) for motive_unit in parsed_file.motive_units
        ]
        inverted_units_str = [
            str(motive_unit) for motive_unit in parsed_file.motive_units_inverted
        ]

        self.assertListEqual(expected_motive_units, motive_units_str)
        self.assertListEqual(expected_inverted_units, inverted_units_str)

    @parameterized.expand(test_data)
    def test_with_mirrored(
        self,
        filename,
        expected_motive_units,
        expected_inverted_units,
        expected_inverted_mirrored_units,
    ):
        options = [ParseOption.WITH_MIRRORED, ParseOption.WITH_INVERTED]
        parsed_file = ParsedFile.parse_file(Path(filename), options)

        motive_units_str = [
            str(motive_unit) for motive_unit in parsed_file.motive_units
        ]
        inverted_units_str = [
            str(motive_unit) for motive_unit in parsed_file.motive_units_inverted
        ]
        mirrored_units_str = [
            str(motive_unit) for motive_unit in parsed_file.motive_units_mirrored
        ]

        self.assertListEqual(expected_motive_units, motive_units_str)
        self.assertListEqual(expected_inverted_units, inverted_units_str)
        self.assertListEqual(expected_inverted_mirrored_units, mirrored_units_str)


if __name__ == "__main__":
    unittest.main()
