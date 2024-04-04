from unittest import TestCase

from xmlReader import XmlReader, ParseOption

test_folder = "./testData"


class XmlReaderTest(TestCase):
    def test_get_intervals(self):
        intervals = XmlReader().get_intervals(test_folder + "/Test_1.xml")

        self.assertEqual(len(intervals), 19)
        self.assertEqual(intervals[0].name, "M2")
        self.assertEqual(intervals[0].semitones, -2)
        self.assertEqual(intervals[0].inverse_semitones, 10)

    def test_get_inverted(self):
        intervals = XmlReader().get_intervals(test_folder + "/Test_1.xml")
        inverted = XmlReader().get_inverted(intervals)

        self.assertEqual(len(inverted), 19)
        self.assertEqual(inverted[0].name, "M2")
        self.assertEqual(inverted[0].semitones, 2)
        self.assertEqual(inverted[0].inverse_semitones, -10)

    def test_get_mirrored(self):
        intervals = XmlReader().get_intervals(test_folder + "/Test_1.xml")
        mirrored = XmlReader().get_mirrored(intervals)

        self.assertEqual(len(mirrored), 19)
        self.assertEqual(mirrored[0].name, "M2")
        self.assertEqual(mirrored[0].semitones, 10)
        self.assertEqual(mirrored[0].inverse_semitones, -2)

    def test_parse_file_with_no_extra_options(self):
        intervals = XmlReader().parse_file(test_folder + "/Test_1.xml", [], 1)

        self.assertEqual(len(intervals), 19)
        self.assertEqual(intervals[0].name, "M2")
        self.assertEqual(intervals[0].semitones, -2)
        self.assertEqual(intervals[0].inverse_semitones, 10)

    def test_parse_file_with_inverted_and_mirrored(self):
        intervals = XmlReader().parse_file(
            test_folder + "/Test_1.xml",
            [ParseOption.WITH_INVERTED, ParseOption.WITH_MIRRORED],
            1,
        )

        self.assertEqual(len(intervals), 61)
        self.assertEqual(intervals[20].name, "Rest")
        self.assertEqual(intervals[40].name, "Rest")
