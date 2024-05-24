import argparse
import logging
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


def extract_piece_name(piece_path: str) -> str:
    filename = piece_path.split("/")[-1]
    if filename.endswith(".xml"):
        return filename[:-4]
    if filename.endswith(".musicxml"):
        return filename[:-9]
    return filename


def is_overlapping_with_previous_position(
    positions: list[int], position: int, length: int
):
    for pos in positions:
        if abs(pos - position) < length:
            return True
    return False


def main():
    inputFile, output_folder = parse_args()

    data = pd.read_json(inputFile)

    motives = {}
    all_pieces = set()

    for i, entry in data.iterrows():
        intervals = [seq["_interval"] for seq in entry["sequence"]]

        non_overlapping_positions = {
            "original": [],
            "inverted": [],
            "mirrored": [],
        }
        frequency_per_position_in_work = {
            "original": 0,
            "inverted": 0,
            "mirrored": 0,
        }
        frequency_per_piece = {}

        for positions in entry["positions"]:
            length = positions["length"]
            position = positions["position"]
            position_in_work = positions["position_in_work"]
            position_in_work_name = ""
            match position_in_work:
                case "0":
                    position_in_work_name = "original"
                case "1":
                    position_in_work_name = "inverted"
                case "2":
                    position_in_work_name = "mirrored"

            if not is_overlapping_with_previous_position(
                non_overlapping_positions[position_in_work_name], position, length
            ):
                non_overlapping_positions[position_in_work_name].append(position)

            frequency_per_position_in_work[position_in_work_name] += 1

            # get frequency_per_piece
            piece = extract_piece_name(positions["origin"]["piece_title"])
            if piece not in frequency_per_piece:
                frequency_per_piece[piece] = 0

            frequency_per_piece[piece] += 1
            all_pieces.add(piece)

        frequency_per_position_in_work_non_overlapping = {
            "original": len(non_overlapping_positions["original"]),
            "inverted": len(non_overlapping_positions["inverted"]),
            "mirrored": len(non_overlapping_positions["mirrored"]),
        }

        in_n_pieces = 0
        for frequency in frequency_per_piece.values():
            if frequency > 0:
                in_n_pieces += 1

        motives[str(intervals)] = {
            "frequency": entry["frequency"],
            "intervals": intervals,
            "frequency_per_position_in_work": frequency_per_position_in_work,
            "frequency_per_piece": frequency_per_piece,
            "frequency_per_position_in_work_non_overlapping": frequency_per_position_in_work_non_overlapping,
            "in_n_pieces": in_n_pieces,
        }

    frequency_per_piece = {}
    for piece in all_pieces:
        frequency_per_piece[piece] = sum(
            [motives[motive]["frequency_per_piece"].get(piece, 0) for motive in motives]
        )
        print(f"{piece}: {frequency_per_piece[piece]}")

    for motive in motives:
        relative_frequency_per_piece = {}
        for piece in all_pieces:
            relative_frequency_per_piece[piece] = (
                motives[motive]["frequency_per_piece"].get(piece, 0)
                / frequency_per_piece[piece]
            )
        motives[motive]["relative_frequency_per_piece"] = relative_frequency_per_piece

    # sort by frequency
    motives = dict(
        sorted(motives.items(), key=lambda item: item[1]["frequency"], reverse=True)
    )

    # Create DataFrame
    columns = [
        "intervals",
        "frequency",
        "frequency_original",
        "frequency_original_non_overlapping",
        "frequency_inverted",
        "frequency_inverted_non_overlapping",
        "frequency_mirrored",
        "frequency_mirrored_non_overlapping",
        "in_n_pieces",
    ]
    piece_columns = [f"frequency_{piece}" for piece in sorted(all_pieces)]
    columns.extend(piece_columns)

    relative_frequency_per_piece_columns = [
        f"relative_frequency_{piece}" for piece in sorted(all_pieces)
    ]
    columns.extend(relative_frequency_per_piece_columns)

    rows = []
    for key, value in motives.items():
        row = [
            key,
            value["frequency"],
            value["frequency_per_position_in_work"]["original"],
            value["frequency_per_position_in_work_non_overlapping"]["original"],
            value["frequency_per_position_in_work"]["inverted"],
            value["frequency_per_position_in_work_non_overlapping"]["inverted"],
            value["frequency_per_position_in_work"]["mirrored"],
            value["frequency_per_position_in_work_non_overlapping"]["mirrored"],
            value["in_n_pieces"],
        ]
        # Add frequencies for each piece
        for piece in sorted(all_pieces):
            row.append(value["frequency_per_piece"].get(piece, 0))

        for piece in sorted(all_pieces):
            row.append(value["relative_frequency_per_piece"].get(piece, 0))
        rows.append(row)

    df = pd.DataFrame(rows, columns=columns)

    # Ensure the output folder exists
    output_folder.mkdir(parents=True, exist_ok=True)
    output_file = output_folder / "motives.csv"
    df.to_csv(output_file, index=False)

    # 2d color plot: x-axis is piece, y-axis is motive, color is relative frequency
    # use only the first 100 motives
    # df = df.set_index("intervals")
    # df = df.drop(
    #     columns=[
    #         "frequency",
    #         "frequency_original",
    #         "frequency_inverted",
    #         "frequency_mirrored",
    #     ]
    # )
    # df = df.drop(columns=piece_columns)
    # # df = df.head(20)
    #
    # df = df.T
    #
    # plt.figure(figsize=(15, 8))  # Increase the figure size
    #
    # # Use pcolormesh for better control over the heatmap
    # plt.pcolormesh(df, cmap="hot_r", norm=LogNorm(), edgecolors="k", linewidth=0.0)
    # plt.colorbar(label="Relative Frequency")
    # plt.xlabel("Intervals")
    # plt.ylabel("Pieces")
    # plt.xticks(range(len(df.columns)), df.columns, rotation=90)
    # plt.yticks(range(len(df.index)), df.index)
    # plt.tight_layout()  # Adjust layout to fit everything
    # plt.savefig(output_folder / "motives_heatmap.png")
    # plt.show()

    # # print 20 most common motives
    # print("Most common motives:")
    # for i, (key, value) in enumerate(motives.items()):
    #
    #     if i == 20:
    #         break
    #     print(
    #         f"{i+1}. {key} - {value['frequency']} - {value['frequency_per_position_in_work']} - occuring in {len(value['frequency_per_piece'])} pieces"
    #     )
    #
    # motives = dict(
    #     sorted(
    #         motives.items(),
    #         key=lambda item: len(item[1]["frequency_per_piece"]),
    #         reverse=True,
    #     )
    # )
    #
    # # print motives which occur most often in different pieces
    # print("Most occuring motives (per piece):")
    # for i, (key, value) in enumerate(motives.items()):
    #
    #     if i == 20:
    #         break
    #     print(
    #         f"{i+1}. {key} - {value['frequency']} - {value['frequency_per_position_in_work']} - occuring in {len(value['frequency_per_piece'])} pieces"
    #     )

    # frequency per length

    # # plot 20 most common motives as bar chart with frequency on y-axis, motive on x-axis and safe to file
    # print("Plotting...")
    # df = pd.DataFrame(motives).T.head(30)
    #
    # df.columns = ["frequency", "motive"]
    # df["motive"] = df["motive"].apply(str)
    #
    # plt.figure(figsize=(15, 8))  # Increase the figure size
    # plot = df.plot(kind="bar", x="motive", y="frequency", legend=False)
    # plot.set_xlabel("Motive")
    # plot.set_ylabel("Frequency")
    # # Rotate x-axis labels
    #
    # plt.tight_layout()  # Adjust layout to fit everything
    # output_folder.mkdir(parents=True, exist_ok=True)  # Ensure the output folder exists
    # plt.savefig(output_folder / "motive_frequency.png")
    # plt.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Current folder: " + str(Path.cwd()))
    main()
