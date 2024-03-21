import logging

from music21 import stream, spanner

from MotiveGenerator import (
    MotiveGenerator,
    prase_args,
    write_motives_to_file,
    write_motives_as_json_to_file,
)


def main():
    motive_generator_options, parser_options = prase_args()

    generator = MotiveGenerator(
        motive_generator_options.min_frequency,
        motive_generator_options.max_gap,
        motive_generator_options.max_length,
        motive_generator_options.min_num_sequences,
        motive_generator_options.max_num_sequences,
    )

    motives, parsed_files = generator.discover_motives(
        parser_options.input_folder, parser_options.options
    )

    write_motives_to_file(motives, parser_options.output_folder)
    write_motives_as_json_to_file(motives, parser_options.output_folder)

    # plot_motives(motives, parser_options)
    # write_motives(motives, parser_options)

    for motive in motives:
        print(motive)

    # s = stream.Stream()
    # for note in parsed_file.notes_and_rests:
    #     s.append(note)
    #
    # for motive in motives:
    #     for position in motive.positions:
    #
    #         shown_position = position.position % len(parsed_file.notes_and_rests)
    #
    #         s.insert(
    #             position.position,
    #             spanner.Slur(
    #                 parsed_file.notes_and_rests[shown_position],
    #                 parsed_file.notes_and_rests[shown_position + position.length],
    #             ),
    #         )
    #
    #         parsed_file.notes_and_rests[shown_position + 1].lyric = motive.sequence
    #
    # s.write("musicxml.pdf", fp="output.pdf")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
