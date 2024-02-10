import unittest

from MotiveGenerator import MotiveGenerator, MotiveUnit, MotivePosition, Motive


class MotiveGeneratorTest(unittest.TestCase):
    def setUp(self):
        self.generator = MotiveGenerator()
        self.sequence = "A,B,A,B,C,D,C,A,B,D,C,E"

    def test_get_motive_units(self):
        units = self.generator.get_motive_units(self.sequence)
        self.assertEqual(len(units), 12)
        self.assertEqual(units[0].name, "A")

    def test_get_basic_motives(self):
        units = self.generator.get_motive_units(self.sequence)
        motives = self.generator.get_basic_motives(units, 2)
        self.assertTrue(len(motives) >= 1)  # Check that we have at least one motive
        self.assertTrue(all(motive.frequency >= 2 for motive in motives))

    def test_get_frequent_position(self):
        units = [MotiveUnit("A")]
        positions = [MotivePosition(0, 1), MotivePosition(2, 1), MotivePosition(7, 1)]
        motive = Motive.from_positions(positions, units)
        freq_pos = self.generator.get_frequent_position(motive, 2)
        self.assertEqual(freq_pos, 3)

    def test_generate_candidate_extensions(self):
        units = self.generator.get_motive_units(self.sequence)
        motives = self.generator.get_basic_motives(units, 2)
        extensions = self.generator.generate_candidate_extension(motives, 11)
        self.assertTrue(len(extensions) >= 1)

    def test_merge_motives(self):
        units = self.generator.get_motive_units(self.sequence)
        motives = self.generator.get_basic_motives(units, 2)
        merged = self.generator.merge_motives(motives[0], motives[1], 1, 4)
        self.assertIsNotNone(merged)

    def test_generate_motives(self):
        units = self.generator.get_motive_units(self.sequence)
        motives = self.generator.generate_motives(units, 2, 1, 1, 4)
        self.assertTrue(len(motives) >= 1)


if __name__ == "__main__":
    unittest.main()
