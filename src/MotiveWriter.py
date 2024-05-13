import json
from dataclasses import asdict
from pathlib import Path
from typing import List

from Motive import Motive
from MotivePosition import PositionInWork


def write_motives_as_json_to_file(motives: List[Motive], output_folder: Path):
    if not output_folder.exists():
        output_folder.mkdir()

    with open(output_folder / output_json_filename, "w") as file:
        instances_dict = [asdict(motive) for motive in motives]

        file.write(json.dumps(instances_dict, indent=4))


output_filename = "output.csv"
output_json_filename = "output.json"


def write_motives_to_file(motives: List[Motive], output_folder: Path):

    if not output_folder.exists():
        output_folder.mkdir()

    with open(output_folder / output_filename, "w") as file:
        file.write(
            "work\tsequence\tfrequency\tpositions\tfrequency_original\tpositions_original\tfrequency_inverted\tpositions_inverted\tfrequency_mirrored\tposition_mirrored\n"
        )
        for motive in motives:
            original_positions = list(
                filter(
                    lambda pos: pos.position_in_work == PositionInWork.ORIGINAL,
                    motive.positions,
                )
            )

            inverted_positions = list(
                filter(
                    lambda pos: pos.position_in_work == PositionInWork.INVERTED,
                    motive.positions,
                )
            )
            mirrored_positions = list(
                filter(
                    lambda pos: pos.position_in_work == PositionInWork.MIRRORED,
                    motive.positions,
                )
            )

            output: List[str] = []
            output.append(motive.sequence[0].origin.piece_title)
            output.append(str(motive.sequence))
            output.append(str(motive.frequency))
            output.append(str(motive.positions))
            output.append(str(len(original_positions)))
            output.append(str(original_positions))
            output.append(str(len(inverted_positions)))
            output.append(str(inverted_positions))
            output.append(str(len(mirrored_positions)))
            output.append(str(mirrored_positions))

            file.write("\t".join(output) + "\n")
