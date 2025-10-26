import argparse
import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from ParseOptions import (
    ParseOptions,
    RestTreatment,
    AccidentalTreatment,
    ChordTreatment,
)


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
        "--inputFolder",
        type=str,
        help="Folder containing the xml and musicxml files",
        required=True,
    )
    parser.add_argument(
        "--outputFolder", type=str, help="Folder for output files", required=True
    )
    parser.add_argument(
        "--minFrequency",
        type=int,
        help="Minimal frequency, of how often a motive must occur",
        required=True,
    )
    parser.add_argument(
        "--maxGap",
        type=int,
        help="Maximum gap allowed between two notes",
        required=True,
    )
    parser.add_argument(
        "--minNumSequences",
        type=int,
        help="Minimum number of sequences in a motive",
        required=True,
    )
    parser.add_argument(
        "--maxNumSequences",
        type=int,
        help="Maximum number of sequences in a motive",
        required=True,
    )
    parser.add_argument(
        "--maxLength",
        type=int,
        help="Maximum length of a motive, including gaps.",
        required=True,
    )

    parser.add_argument(
        "--restTreatment",
        help="Optional flag to remove rests to a certain length from the corpus before analysing. Default NONE.",
        type=RestTreatment.from_string,
        choices=list(RestTreatment),
        default=ParseOptions.rest_treatment,
        metavar="{NONE,REMOVE_EIGHTS_AND_LOWER,REMOVE_SIXTEENTH_AND_LOWER}",
    )

    parser.add_argument(
        "--accidentalTreatment",
        help="Optional flag to remove all accidentals from notes in the corpus before analysing. Default REMOVE_ACCIDENTALS",
        type=AccidentalTreatment.from_string,
        choices=list(AccidentalTreatment),
        default=ParseOptions.accidental_treatment,
        metavar="{NONE,REMOVE_ACCIDENTALS}",
    )

    parser.add_argument(
        "--chordTreatment",
        help="Optional flag to select how chords should be treated in the corpus before analysing. Default HIGHEST",
        type=ChordTreatment.from_string,
        choices=list(ChordTreatment),
        default=ParseOptions.chord_treatment,
        metavar="{HIGHEST,LOWEST,REMOVE}",
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
