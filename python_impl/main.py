from MotiveGenerator import MotiveGenerator
from xmlReader import XmlReader


def main():
    intervals = XmlReader.get_intervals("path/to/file.xml")

    sequence = ",".join(intervals)

    generator = MotiveGenerator()
    # sequence = "A,B,A,B,C,D,C,A,B,D,C,E"
    units = generator.get_motive_units(sequence)
    motives = generator.generate_motives(units, 2, 1, 1, 4)
    for motive in motives:
        print(motive)


if __name__ == '__main__':
    main()
