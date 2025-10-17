import argparse
import logging
from cmath import sqrt
from dataclasses import dataclass
from pathlib import Path
from typing import Set, Dict, Tuple

import matplotlib

from MotiveList import ResultMotive, MotiveList
from SequenceType import SequenceType

matplotlib.use("TkAgg")

import pandas as pd


def parse_args() -> (Path, Path):
    parser = argparse.ArgumentParser(description="Plot Motive Generator output")
    parser.add_argument("--inputFile", type=str, help="File containing the output")
    parser.add_argument("--outputFolder", type=str, help="Folder for output files")
    parser.add_argument("--filterOverlappingPositions", action=argparse.BooleanOptionalAction, help="Filter overlapping positions of motives", default=True)

    args = parser.parse_args()
    input_file = Path(args.inputFile)
    output_folder = Path(args.outputFolder)
    filter_overlapping_positions_option = args.filterOverlappingPositions

    return input_file, output_folder, filter_overlapping_positions_option


def is_overlapping_with_previous_position(position: int, other: int, length: int):
    return abs(position - other) < length


def read_motives_from_json(input_file: Path) -> MotiveList:
    with open(input_file, "r") as file:
        json_str = file.read()
        return MotiveList.model_validate_json(json_str)


@dataclass
class MotiveClass:
    frequency: int
    intervals_original: str
    interval_inverted: str
    interval_mirrored: str
    interval_mirrored_inverted: str
    frequency_per_sequence_type: Dict[str, int]
    frequency_per_piece: Dict[str, int]
    in_n_pieces: int
    relative_frequency_per_piece: Dict[str, float]
    mean_relative_frequency: float
    standard_derivation_relative_frequency: float
    weighted_arithmetic_mean: float

def rearrange_so_original_has_max_value(original_dict: Dict[str, int], original: str, inverted: str, mirrored: str, mirrored_inverted: str) -> Tuple[Dict[str, int], str, str, str, str]:
    key_with_max_value = max(original_dict, key=original_dict.get)

    if key_with_max_value == "INVERTED":
        new_dict = {
            "ORIGINAL": original_dict["INVERTED"],
            "INVERTED": original_dict["ORIGINAL"],
            "MIRRORED": original_dict["MIRRORED_INVERTED"],
            "MIRRORED_INVERTED": original_dict["MIRRORED"],
        }
        return new_dict, inverted, original, mirrored_inverted, mirrored
    elif key_with_max_value == "MIRRORED":
        new_dict = {
            "ORIGINAL": original_dict["MIRRORED"],
            "INVERTED": original_dict["MIRRORED_INVERTED"],
            "MIRRORED": original_dict["ORIGINAL"],
            "MIRRORED_INVERTED": original_dict["INVERTED"],
        }
        return new_dict, mirrored, mirrored_inverted, original, inverted
    elif key_with_max_value == "MIRRORED_INVERTED":
        new_dict = {
            "ORIGINAL": original_dict["MIRRORED_INVERTED"],
            "INVERTED": original_dict["MIRRORED"],
            "MIRRORED": original_dict["INVERTED"],
            "MIRRORED_INVERTED": original_dict["ORIGINAL"],
        }
        return new_dict, mirrored_inverted, mirrored, inverted, original
    else:
        return original_dict, original, inverted, mirrored, mirrored_inverted

def main():
    input_file, output_folder, filter_overlapping_positions_option = parse_args()

    motive_list = read_motives_from_json(input_file)

    piece_titles = extract_piece_titles(motive_list)
    motive_classes: Dict[str, MotiveClass] = {}

    for motive in motive_list.motives:
        intervals_original = str(motive.intervals.interval_classes[SequenceType.ORIGINAL])
        intervals_inverted = str(motive.intervals.interval_classes[SequenceType.INVERTED])
        intervals_mirrored = str(motive.intervals.interval_classes[SequenceType.MIRRORED])
        intervals_mirrored_inverted = str(motive.intervals.interval_classes[SequenceType.MIRRORED_INVERTED])

        if filter_overlapping_positions_option:
            filter_overlapping_positions(motive)

        frequency_per_sequence_type = get_frequency_per_sequence_type(motive)

        frequency_per_sequence_type, intervals_original, intervals_inverted, intervals_mirrored, intervals_mirrored_inverted = rearrange_so_original_has_max_value(frequency_per_sequence_type, intervals_original, intervals_inverted, intervals_mirrored, intervals_mirrored_inverted)

        frequency_per_piece = get_frequency_per_piece(piece_titles, motive)

        in_n_pieces = get_occurance_of_motive_class(frequency_per_piece)

        motive_classes[str(intervals_original)] = MotiveClass(
            frequency=motive.frequency(),
            intervals_original=intervals_original,
            interval_inverted=intervals_inverted,
            interval_mirrored=intervals_mirrored,
            interval_mirrored_inverted=intervals_mirrored_inverted,
            frequency_per_sequence_type=frequency_per_sequence_type,
            frequency_per_piece=frequency_per_piece,
            in_n_pieces=in_n_pieces,
            relative_frequency_per_piece={},
            mean_relative_frequency=0,
            standard_derivation_relative_frequency=0,
            weighted_arithmetic_mean=0,
        )

    motives_per_piece = get_motives_per_piece(motive_classes, piece_titles)

    number_of_pieces = len(piece_titles)
    logging.info(f"Number of pieces: {number_of_pieces}")

    number_of_motive_classes = len(motive_classes)
    logging.info(f"Number of motive classes: {number_of_motive_classes}")

    mean_motives_in_piece = sum(motives_per_piece.values()) / number_of_pieces
    logging.info(f"Mean number of motives in piece: {mean_motives_in_piece}")

    logging.info("Calculating relative frequencies")
    for motive_class in motive_classes.values():
        (
            relative_frequency_per_piece,
            mean_relative_frequency,
            standard_derivation_relative_frequency,
        ) = calculate_relative_frequency(
            motive_class, motives_per_piece, number_of_pieces, piece_titles
        )

        motive_class.relative_frequency_per_piece = relative_frequency_per_piece
        motive_class.mean_relative_frequency = mean_relative_frequency
        motive_class.standard_derivation_relative_frequency = (
            standard_derivation_relative_frequency
        )

    mean_number_of_motive_classes_per_piece, motive_classes_per_piece = (
        get_motive_classes_per_piece(motive_classes, number_of_pieces, piece_titles)
    )

    correlation_nominator = sum(
        [
            (motives_per_piece[piece] - mean_motives_in_piece)
            * (
                motive_classes_per_piece[piece]
                - mean_number_of_motive_classes_per_piece
            )
            for piece in piece_titles
        ]
    )
    correlation_denominator = sqrt(
        sum(
            [
                (motives_per_piece[piece] - mean_motives_in_piece) ** 2
                for piece in piece_titles
            ]
        )
        * sum(
            [
                (
                    motive_classes_per_piece[piece]
                    - mean_number_of_motive_classes_per_piece
                )
                ** 2
                for piece in piece_titles
            ]
        )
    ).real

    correlation = correlation_nominator / correlation_denominator
    logging.info(f"Correlation: {correlation}")

    # Gewichtete Arithmetische Mittel
    total_number_of_motives = sum([motives_per_piece[piece] for piece in piece_titles])

    weighted_arithmetic_mean_per_motive = {}

    for key, motive_class in motive_classes.items():
        weighted_arithmetic_mean_per_motive[key] = (
            sum(
                [
                    motive_class.frequency_per_piece[piece] * motives_per_piece[piece]
                    for piece in piece_titles
                ]
            )
            / total_number_of_motives
        )
        motive_class.weighted_arithmetic_mean = weighted_arithmetic_mean_per_motive[key]

    logging.info("Sorting motives")
    # sort by frequency
    sorted_motive_classes = dict(
        sorted(motive_classes.items(), key=lambda item: item[1].frequency, reverse=True)
    )

    logging.info("Creating DataFrame")
    # Create DataFrame
    columns = [
        "intervals_original",
        "interval_inverted",
        "interval_mirrored",
        "interval_mirrored_inverted",
        "frequency",
        "frequency_original",
        "frequency_inverted",
        "frequency_mirrored",
        "frequency_mirrored_inverted",
        "in_n_pieces",
        "mean_relative_frequency",
        "standard_derivation_relative_frequency",
        "weighted_arithmetic_mean",
    ]
    frequency_per_piece_columns = [
        f"frequency_{piece}" for piece in sorted(piece_titles)
    ]
    columns.extend(frequency_per_piece_columns)

    relative_frequency_per_piece_columns = [
        f"relative_frequency_{piece}" for piece in sorted(piece_titles)
    ]
    columns.extend(relative_frequency_per_piece_columns)

    rows = []
    for key, motive_class in sorted_motive_classes.items():
        row = [
            motive_class.intervals_original,
            motive_class.interval_inverted,
            motive_class.interval_mirrored,
            motive_class.interval_mirrored_inverted,
            motive_class.frequency,
            motive_class.frequency_per_sequence_type["ORIGINAL"],
            motive_class.frequency_per_sequence_type["INVERTED"],
            motive_class.frequency_per_sequence_type["MIRRORED"],
            motive_class.frequency_per_sequence_type["MIRRORED_INVERTED"],
            motive_class.in_n_pieces,
            motive_class.mean_relative_frequency,
            motive_class.standard_derivation_relative_frequency,
            motive_class.weighted_arithmetic_mean,
        ]
        # Add frequencies for each piece
        for piece in sorted(piece_titles):
            row.append(motive_class.frequency_per_piece.get(piece, 0))

        for piece in sorted(piece_titles):
            row.append(motive_class.relative_frequency_per_piece.get(piece, 0))

        rows.append(row)

    df = pd.DataFrame(rows, columns=columns)

    # Ensure the output folder exists
    logging.info(f"Writing output to {output_folder}")
    output_folder.mkdir(parents=True, exist_ok=True)
    output_file = output_folder / "motives.csv"
    df.to_csv(output_file, index=False)


def get_motive_classes_per_piece(
    motive_classes: Dict[str, MotiveClass],
    number_of_pieces: int,
    piece_titles: Set[str],
):
    logging.info("Calculating number of motive classes per piece")
    motive_classes_per_piece = {}
    for piece in piece_titles:
        motive_classes_per_piece[piece] = sum(
            [
                1
                for motive in motive_classes
                if motive_classes[motive].frequency_per_piece.get(piece, 0) > 0
            ]
        )
    mean_number_of_motive_classes_per_piece = (
        sum(motive_classes_per_piece.values()) / number_of_pieces
    )
    logging.info(
        f"Mean number of motive classes per piece: {mean_number_of_motive_classes_per_piece}"
    )
    standard_derivation_number_of_motive_classes_per_piece = (
        sqrt(
            sum(
                [
                    (
                        motive_classes_per_piece[piece]
                        - mean_number_of_motive_classes_per_piece
                    )
                    ** 2
                    for piece in piece_titles
                ]
            )
        ).real
        / number_of_pieces
    )
    logging.info(
        f"Standard derivation number of motive classes per piece: {standard_derivation_number_of_motive_classes_per_piece}"
    )
    return mean_number_of_motive_classes_per_piece, motive_classes_per_piece


def get_motives_per_piece(motive_classes, piece_titles):
    motives_in_piece = {}
    for piece in piece_titles:
        motives_in_piece[piece] = sum(
            [
                motive_class.frequency_per_piece.get(piece, 0)
                for motive_class in motive_classes.values()
            ]
        )
    return motives_in_piece


def calculate_relative_frequency(
    motive_class: MotiveClass, motives_in_piece, number_of_pieces, piece_titles
):
    relative_frequency_per_piece = {}
    for piece in piece_titles:
        relative_frequency_per_piece[piece] = (
            motive_class.frequency_per_piece.get(piece, 0) / motives_in_piece[piece]
        )

    mean_relative_frequency = (
        sum(relative_frequency_per_piece.values()) / number_of_pieces
    )
    standard_derivation_relative_frequency = (
        sqrt(
            sum(
                [
                    (relative_frequency_per_piece[piece] - mean_relative_frequency) ** 2
                    for piece in piece_titles
                ]
            )
        )
        / number_of_pieces
    ).real

    return (
        relative_frequency_per_piece,
        mean_relative_frequency,
        standard_derivation_relative_frequency,
    )


def get_occurance_of_motive_class(frequency_per_piece):
    in_n_pieces = 0
    for frequency in frequency_per_piece.values():
        if frequency > 0:
            in_n_pieces += 1
    return in_n_pieces


def get_frequency_per_sequence_type(result_motive: ResultMotive):
    logging.info(f"Calculating frequencies per sequence type")
    frequency_per_sequence_type = {}
    for sequence_type in result_motive.positions:
        frequency_per_sequence_type[str(sequence_type)] = result_motive.frequency(
            sequence_type
        )
    return frequency_per_sequence_type


def get_frequency_per_piece(piece_titles: Set[str], result_motive: ResultMotive):
    logging.info(f"Calculating frequencies per piece")
    frequency_per_piece = {piece_title: 0 for piece_title in piece_titles}

    for sequence_type, position_per_sequence_type in result_motive.positions.items():
        for (
            piece_title,
            positions_per_piece_title,
        ) in position_per_sequence_type.items():
            for part, positions_per_part in positions_per_piece_title.items():
                for voice, positions_per_voice in positions_per_part.items():
                    frequency_per_piece[piece_title] += len(positions_per_voice)

    return frequency_per_piece


def filter_overlapping_positions(result_motive: ResultMotive, filter_overlapping_positions_option: bool = True):
    helper_positions_by_piece = {}
    logging.info(f"Calculating helper positions")
    for sequence_type, positions_by_sequence_type in result_motive.positions.items():
        for piece, positions_by_piece in positions_by_sequence_type.items():
            if piece not in helper_positions_by_piece:
                helper_positions_by_piece[piece] = {}
            for part, positions_by_part in positions_by_piece.items():
                if part not in helper_positions_by_piece[piece]:
                    helper_positions_by_piece[piece][part] = {}
                for voice, positions_by_voice in positions_by_part.items():
                    if voice not in helper_positions_by_piece[piece][part]:
                        helper_positions_by_piece[piece][part][voice] = {}
                    helper_positions_by_piece[piece][part][voice][
                        sequence_type
                    ] = positions_by_voice

    logging.info(f"Filtering all positions")
    for piece, positions_by_piece in helper_positions_by_piece.items():
        for part, positions_by_part in positions_by_piece.items():
            for voice, positions_by_voice in positions_by_part.items():
                all_positions_per_voice = []
                for (
                    sequence_type,
                    positions_by_sequence_type,
                ) in positions_by_voice.items():

                    enumerated_positions = [
                        {"position": position, "sequenceType": sequence_type}
                        for position in positions_by_sequence_type
                    ]
                    all_positions_per_voice.extend(enumerated_positions)

                # sort by position
                all_positions_per_voice = sorted(
                    all_positions_per_voice, key=lambda x: x["position"].position
                )

                # remove overlapping positions
                filtered_positions = []
                for i, position in enumerate(all_positions_per_voice):
                    if i == 0:
                        filtered_positions.append(position)
                    else:
                        if not is_overlapping_with_previous_position(
                            position["position"].position,
                            filtered_positions[-1]["position"].position,
                            filtered_positions[-1]["position"].length,
                        ):
                            filtered_positions.append(position)

                # split by sequence type
                filtered_positions_per_sequence_type = {}
                for position in filtered_positions:
                    if (
                        position["sequenceType"]
                        not in filtered_positions_per_sequence_type
                    ):
                        filtered_positions_per_sequence_type[
                            position["sequenceType"]
                        ] = []
                    filtered_positions_per_sequence_type[
                        position["sequenceType"]
                    ].append(position["position"])

                for sequence_type in filtered_positions_per_sequence_type:
                    if piece in result_motive.positions[sequence_type]:
                        if part in result_motive.positions[sequence_type][piece]:
                            if (
                                voice
                                in result_motive.positions[sequence_type][piece][part]
                            ):
                                result_motive.positions[sequence_type][piece][part][
                                    voice
                                ] = filtered_positions_per_sequence_type[sequence_type]


def extract_piece_titles(motive_list: MotiveList):
    all_pieces = set()
    for motive in motive_list.motives:
        for pieces in motive.positions.values():
            for piece in pieces.keys():
                all_pieces.add(piece)
    return all_pieces


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Current folder: " + str(Path.cwd()))
    main()
