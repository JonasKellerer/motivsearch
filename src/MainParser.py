import argparse
import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from ParseOptions import ParseOptions, RestTreatment, AccidentalTreatment, ChordTreatment


class ParseOption(Enum):
    USE_DIATONIC = 1

    def __eq__(self, other):
        if type(self).__qualname__ != type(other).__qualname__:
            return NotImplemented
        return self.name == other.name and self.value == other.value

    def __hash__(self):
        return hash((type(self).__qualname__, self.name))


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
    options: ParseOptions = ParseOptions()


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
        "--restTreatment",
        type=RestTreatment.from_string,
        choices=list(RestTreatment),
        default=ParseOptions.rest_treatment
    )

    parser.add_argument(
        "--accidentalTreatment",
        type=AccidentalTreatment.from_string,
        choices=list(AccidentalTreatment),
        default=ParseOptions.accidental_treatment
    )

    parser.add_argument(
        "--chordTreatment",
        type=ChordTreatment.from_string,
        choices=list(ChordTreatment),
        default=ParseOptions.chord_treatment
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
        ParseOptions(
            args.restTreatment,
            args.chordTreatment,
            args.accidentalTreatment,
        ),
    )

    logging.info(f"Motive generator options: {motive_generator_options}")
    logging.info(f"Parser options: {parsers_options}")


    return motive_generator_options, parsers_options
