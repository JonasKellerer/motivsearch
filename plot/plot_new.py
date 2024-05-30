import argparse
import logging
from cmath import sqrt
from pathlib import Path

import matplotlib
from matplotlib.colors import LogNorm

matplotlib.use("TkAgg")

import pandas as pd
from matplotlib import pyplot as plt


def parse_args() -> ():
    parser = argparse.ArgumentParser(description="Plot Motive Generator output")
    parser.add_argument("--inputFile", type=str, help="File containing the output")
    parser.add_argument("--outputFolder", type=str, help="Folder for output files")

    args = parser.parse_args()
    inputFile = Path(args.inputFile)
    output_folder = Path(args.outputFolder)

    return inputFile, output_folder


def is_overlapping_with_previous_position(position: int, other: int, length: int):
    return abs(position - other) < length


def main():
    inputFile, output_folder = parse_args()

    data = pd.read_json(inputFile)

    motives = {}
    all_pieces = set()

    for i, entry in data.iterrows():
        intervals = entry["intervals"]

        intervals_original = [
            interval["_interval"]
            for interval in intervals["interval_classes"]["0"]["intervals"]
        ]
        intervals_inverted = [
            interval["_interval"]
            for interval in intervals["interval_classes"]["1"]["intervals"]
        ]
        intervals_mirrored = [
            interval["_interval"]
            for interval in intervals["interval_classes"]["2"]["intervals"]
        ]
        intervals_mirrored_inverted = [
            interval["_interval"]
            for interval in intervals["interval_classes"]["3"]["intervals"]
        ]
        logging.info(f"Intervals: {intervals_original}")

        frequency_per_sequence_type = {
            "original": 0,
            "inverted": 0,
            "mirrored": 0,
            "mirrored_inverted": 0,
        }
        frequency_per_piece = {}
        all_positions = {}

        logging.info(f"Calculating all positions")
        for sequence_type in entry["positions"]:
            for piece in entry["positions"][sequence_type]:
                all_positions[piece] = {}
                for part in entry["positions"][sequence_type][piece]:
                    all_positions[piece][part] = {}
                    for voice in entry["positions"][sequence_type][piece][part]:
                        all_positions[piece][part][voice] = {}
                        positions = entry["positions"][sequence_type][piece][part][
                            voice
                        ]
                        all_positions[piece][part][voice][sequence_type] = positions

        logging.info(f"Filtering all positions")
        for piece in all_positions:
            for part in all_positions[piece]:
                for voice in all_positions[piece][part]:
                    all_positions_per_voice = []
                    for sequence_type in all_positions[piece][part][voice]:
                        positions_per_sequence_type = all_positions[piece][part][voice][
                            sequence_type
                        ]

                        enumerated_positions = [
                            {"position": position, "sequenceType": sequence_type}
                            for position in positions_per_sequence_type
                        ]
                        all_positions_per_voice.extend(enumerated_positions)

                    # sort by position
                    all_positions_per_voice = sorted(
                        all_positions_per_voice, key=lambda x: x["position"]["position"]
                    )

                    # remove overlapping positions
                    filtered_positions = []
                    for i, position in enumerate(all_positions_per_voice):
                        if i == 0:
                            filtered_positions.append(position)
                        else:
                            if not is_overlapping_with_previous_position(
                                position["position"]["position"],
                                filtered_positions[-1]["position"]["position"],
                                filtered_positions[-1]["position"]["length"],
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
                        if piece in entry["positions"][sequence_type]:
                            if part in entry["positions"][sequence_type][piece]:
                                if (
                                    voice
                                    in entry["positions"][sequence_type][piece][part]
                                ):
                                    entry["positions"][sequence_type][piece][part][
                                        voice
                                    ] = filtered_positions_per_sequence_type[
                                        sequence_type
                                    ]

        logging.info(f"Calculating frequencies")
        for sequence_type in entry["positions"]:
            sequence_type_name = ""
            match sequence_type:
                case "0":
                    sequence_type_name = "original"
                case "1":
                    sequence_type_name = "inverted"
                case "2":
                    sequence_type_name = "mirrored"
                case "3":
                    sequence_type_name = "mirrored_inverted"

            for piece in entry["positions"][sequence_type]:
                if piece not in frequency_per_piece:
                    frequency_per_piece[piece] = 0
                all_pieces.add(piece)

                for part in entry["positions"][sequence_type][piece]:
                    for voice in entry["positions"][sequence_type][piece][part]:
                        positions = entry["positions"][sequence_type][piece][part][
                            voice
                        ]

                        frequency_per_sequence_type[sequence_type_name] += len(
                            positions
                        )

                        frequency_per_piece[piece] += len(positions)

        in_n_pieces = 0
        for frequency in frequency_per_piece.values():
            if frequency > 0:
                in_n_pieces += 1

        frequency = sum(frequency_per_sequence_type.values())

        motives[str(intervals_original)] = {
            "frequency": frequency,
            "intervals_original": intervals_original,
            "interval_inverted": intervals_inverted,
            "interval_mirrored": intervals_mirrored,
            "interval_mirrored_inverted": intervals_mirrored_inverted,
            "frequency_per_sequence_type": frequency_per_sequence_type,
            "frequency_per_piece": frequency_per_piece,
            "in_n_pieces": in_n_pieces,
        }

    motives_in_piece = {}
    for piece in all_pieces:
        motives_in_piece[piece] = sum(
            [motives[motive]["frequency_per_piece"].get(piece, 0) for motive in motives]
        )

    number_of_pieces = len(all_pieces)
    logging.info(f"Number of pieces: {number_of_pieces}")

    number_of_motive_classes = len(motives)
    logging.info(f"Number of motive classes: {number_of_motive_classes}")

    mean_motives_in_piece = sum(motives_in_piece.values()) / number_of_pieces
    logging.info(f"Mean number of motives in piece: {mean_motives_in_piece}")

    logging.info("Calculating relative frequencies")
    for motive in motives:
        relative_frequency_per_piece = {}
        for piece in all_pieces:
            relative_frequency_per_piece[piece] = (
                motives[motive]["frequency_per_piece"].get(piece, 0)
                / motives_in_piece[piece]
            )
        motives[motive]["relative_frequency_per_piece"] = relative_frequency_per_piece
        motives[motive]["mean_relative_frequency"] = (
            sum(relative_frequency_per_piece.values()) / number_of_pieces
        )
        motives[motive]["standard_derivation_relative_frequency"] = (
            sqrt(
                sum(
                    [
                        (
                            relative_frequency_per_piece[piece]
                            - motives[motive]["mean_relative_frequency"]
                        )
                        ** 2
                        for piece in all_pieces
                    ]
                )
            )
            / number_of_pieces
        ).real

    logging.info("Calculating number of motive classes per piece")
    motive_classes_per_piece = {}
    for piece in all_pieces:
        motive_classes_per_piece[piece] = sum(
            [
                1
                for motive in motives
                if motives[motive]["frequency_per_piece"].get(piece, 0) > 0
            ]
        )
    mean_number_of_motive_classes_per_piece = (
        sum(motive_classes_per_piece.values()) / number_of_pieces
    )
    logging.info(
        f"Mean number of motive classes per piece: {mean_number_of_motive_classes_per_piece}"
    )

    standard_derivation_number_of_motive_classes_per_piece = sqrt(
        sum(
            [
                (
                    motive_classes_per_piece[piece]
                    - mean_number_of_motive_classes_per_piece
                )
                ** 2
                for piece in all_pieces
            ]
        )
    ).real
    logging.info(
        f"Standard derivation number of motive classes per piece: {standard_derivation_number_of_motive_classes_per_piece}"
    )

    correlation_nominator = sum(
        [
            (motives_in_piece[piece] - mean_motives_in_piece)
            * (
                motive_classes_per_piece[piece]
                - mean_number_of_motive_classes_per_piece
            )
            for piece in all_pieces
        ]
    )
    correlation_denominator = sqrt(
        sum(
            [
                (motives_in_piece[piece] - mean_motives_in_piece) ** 2
                for piece in all_pieces
            ]
        )
        * sum(
            [
                (
                    motive_classes_per_piece[piece]
                    - mean_number_of_motive_classes_per_piece
                )
                ** 2
                for piece in all_pieces
            ]
        )
    ).real

    correlation = correlation_nominator / correlation_denominator
    logging.info(f"Correlation: {correlation}")

    logging.info("Sorting motives")
    # sort by frequency
    motives = dict(
        sorted(motives.items(), key=lambda item: item[1]["frequency"], reverse=True)
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
    ]
    frequency_per_piece_columns = [f"frequency_{piece}" for piece in sorted(all_pieces)]
    columns.extend(frequency_per_piece_columns)

    relative_frequency_per_piece_columns = [
        f"relative_frequency_{piece}" for piece in sorted(all_pieces)
    ]
    columns.extend(relative_frequency_per_piece_columns)

    rows = []
    for key, value in motives.items():
        row = [
            value["intervals_original"],
            value["interval_inverted"],
            value["interval_mirrored"],
            value["interval_mirrored_inverted"],
            value["frequency"],
            value["frequency_per_sequence_type"]["original"],
            value["frequency_per_sequence_type"]["inverted"],
            value["frequency_per_sequence_type"]["mirrored"],
            value["frequency_per_sequence_type"]["mirrored_inverted"],
            value["in_n_pieces"],
            value["mean_relative_frequency"],
            value["standard_derivation_relative_frequency"],
        ]
        # Add frequencies for each piece
        for piece in sorted(all_pieces):
            row.append(value["frequency_per_piece"].get(piece, 0))

        for piece in sorted(all_pieces):
            row.append(value["relative_frequency_per_piece"].get(piece, 0))

        rows.append(row)

    df = pd.DataFrame(rows, columns=columns)

    # Ensure the output folder exists
    logging.info(f"Writing output to {output_folder}")
    output_folder.mkdir(parents=True, exist_ok=True)
    output_file = output_folder / "motives.csv"
    df.to_csv(output_file, index=False)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Current folder: " + str(Path.cwd()))
    main()
