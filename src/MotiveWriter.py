import json
from dataclasses import asdict
from pathlib import Path

from MotiveList import MotiveList


def write_motives_as_json_to_file(motives: MotiveList, output_folder: Path):
    if not output_folder.exists():
        output_folder.mkdir()

    with open(output_folder / output_json_filename, "w") as file:
        instances_dict = [asdict(motive) for motive in motives]

        file.write(json.dumps(instances_dict, indent=4))


output_filename = "output.csv"
output_json_filename = "output.json"
