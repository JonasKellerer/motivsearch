import argparse
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class ParseOption(Enum):
    WITH_INVERTED = 1
    WITH_MIRRORED = 2
    USE_DIATONIC = 3

@dataclass
class MotiveGeneratorOptions:
    min_frequency: int
    max_gap: int
    max_length: int
    min_num_sequences: int
    max_num_sequences: int


@dataclass
class ParserOptions:
    input_folder: Path
    output_folder: Path
    options: list[ParseOption]


def parse_args() -> (MotiveGeneratorOptions, ParserOptions):
    parser = argparse.ArgumentParser(description="Motive Generator")
    parser.add_argument(
        "--inputFolder", type=str, help="Folder containing the xml files"
    )
    parser.add_argument("--outputFolder", type=str, help="Folder for output files")
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
        Path(args.inputFolder),
        Path(args.outputFolder),
        [
            ParseOption.WITH_INVERTED if args.withInverted else None,
            ParseOption.WITH_MIRRORED if args.withMirrored else None,
            ParseOption.USE_DIATONIC if args.useDiatonic else None,
        ],
    )

    return motive_generator_options, parsers_options
