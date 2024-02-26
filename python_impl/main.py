import argparse
import logging
from dataclasses import dataclass

from music21 import stream, spanner

from MotiveGenerator import MotiveGenerator
from xmlReader import XmlReader, ParseOption


def main():
    motive_generator_options, parser_options = prase_args()

    intervals, notes_and_rests = XmlReader.parse_file(
        parser_options.folder,
        parser_options.options,
        motive_generator_options.max_gap,
    )

    sequence = ",".join([XmlReader.get_motive_unit(interval) for interval in intervals])
    logging.info(f"Sequence: {sequence}")

    generator = MotiveGenerator()

    units = generator.get_motive_units(sequence)
    motives = generator.generate_motives(
        units,
        motive_generator_options.min_frequency,
        motive_generator_options.max_gap,
        motive_generator_options.max_length,
        motive_generator_options.min_num_sequences,
        motive_generator_options.max_num_sequences,
    )

    for motive in motives:
        print(motive)

    s = stream.Stream()
    for note in notes_and_rests:
        s.append(note)

    for motive in motives:
        for position in motive.positions:

            shown_position = position.position % len(notes_and_rests)

            s.insert(
                position.position,
                spanner.Slur(
                    notes_and_rests[shown_position],
                    notes_and_rests[shown_position + position.length],
                ),
            )

            notes_and_rests[shown_position + 1].lyric = motive.sequence

    s.write("musicxml.pdf", fp="output.pdf")


@dataclass
class MotiveGeneratorOptions:
    min_frequency: int
    max_gap: int
    max_length: int
    min_num_sequences: int
    max_num_sequences: int


@dataclass
class ParserOptions:
    folder: str
    options: list[ParseOption]


def prase_args() -> (MotiveGeneratorOptions, ParserOptions):
    parser = argparse.ArgumentParser(description="Motive Generator")
    parser.add_argument("--folder", type=str, help="Folder containing the xml files")
    parser.add_argument("--output", type=str, help="Output file")
    parser.add_argument(
        "--minFrequency",
        type=int,
        help="Minimal frequency, of how often a motive must occur",
    )
    parser.add_argument(
        "--maxGap", type=int, help="Maximum gap allowed between two notes"
    )
    parser.add_argument(
        "--minNumSequences", type=int, help="Minimum number of sequences"
    )
    parser.add_argument(
        "--maxNumSequences", type=int, help="Maximum number of sequences"
    )
    parser.add_argument("--maxLength", type=int, help="Maximum length of a motive")
    parser.add_argument(
        "--withInverted", action="store_true", help="Searches also for inverted motives"
    )
    parser.add_argument(
        "--withMirrored", action="store_true", help="Searches also for mirrored motives"
    )
    parser.add_argument(
        "--useDiatonic", action="store_true", help="Use diatonic intervals"
    )

    args = parser.parse_args()
    motive_generator_options = MotiveGeneratorOptions(
        args.minFrequency,
        args.maxGap,
        args.maxLength,
        args.minNumSequences,
        args.maxNumSequences,
    )
    parsers_options = ParserOptions(
        args.folder,
        [
            ParseOption.WITH_INVERTED if args.withInverted else None,
            ParseOption.WITH_MIRRORED if args.withMirrored else None,
            ParseOption.USE_DIATONIC if args.useDiatonic else None,
        ],
    )

    return motive_generator_options, parsers_options


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
