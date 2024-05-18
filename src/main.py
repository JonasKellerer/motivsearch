import logging

from MotiveGenerator import MotiveGenerator
from MotiveWriter import write_motives_to_file, write_motives_as_json_to_file
from src.MainParser import parse_args


def main():
    motive_generator_options, parser_options = parse_args()

    generator = MotiveGenerator(
        motive_generator_options.min_frequency,
        motive_generator_options.max_gap,
        motive_generator_options.max_length,
        motive_generator_options.min_num_sequences,
        motive_generator_options.max_num_sequences,
    )

    motives = generator.discover_motives(
        parser_options.input_folder, parser_options.options
    )

    write_motives_as_json_to_file(motives, parser_options.output_folder)

    for motive in motives:
        print(motive)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
