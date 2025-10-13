from pathlib import Path

from MotiveList import MotiveList


def write_motives_as_json_to_file(motives: MotiveList, output_folder: Path):
    if not output_folder.exists():
        output_folder.mkdir()

    with open(output_folder / output_json_filename, "w") as file:
        file.write(motives.model_dump_json(indent=2))


output_filename = "output.csv"
output_json_filename = "output.json"
