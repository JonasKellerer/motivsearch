# Motive search

In this repo you will find a tool to search for motives in a folder of music scores in xml/musicxml format.
The tool will search for motives that are repeated in the scores.

Major features of the tool:
- Find motives across hundreds of scores, including orchestral scores
- Account for mirrored, inverted, and mirrored-and-inverted motives
- Filter motives by frequency, length, and number of intervals
- Allow gaps between intervals
- Option to remove accidentals from the input
- Option to ignore eighth and sixteenth rests (or shorter)
- Option to use only the highest/lowest note in a chord or to ignore chords
- Ignore rhythm and consider only pitch

This tool was used for the paper: TODO.

## Algorithm details

The algorithm is loosely based on the paper [Benammar et al.](https://doi.org/10.1007/978-3-319-68765-0_2).

### Determination of mirrored and inverted motives

n contrast to Benammar et al., the algorithm does not determine mirrored and inverted motives directly.
It first determines the motives within each score.
Then, in a second step, it merges the motives across scores, grouping mirrored and inverted motives together.
This way, mirrored and inverted motives can be found across different scores.

### Handling of rests

While determining intervals, rests are handled as follows:

- If a note is followed by a rest, the interval gets the special value "note before".
- If a rest is followed by a note, the interval gets the special value "note after".
- If a rest is followed by a rest, the interval gets the special value "rest".

The algorithm then runs as if rests are regular intervals. Thus, they can be "skipped" through the gap feature.
In the end, motives with rests are removed from the result, so it only contains regular intervals.

### Handling of slurs

The algorithm treats slurs as a single note; for example, two quarter notes connected by a slur are treated as a single half note.

# Installation

This project is developed for Linux distributions.
It may also work on other systems, since it runs Python scripts.
For this project you need Python 3.10 and MuseScore 4.6.2. It might run with other versions, but was not tested.

We use [uv](https://docs.astral.sh/uv/) to install packages and handle the python version.
To install the necessary Python packages, run:

```bash
uv venv
source .venv/bin/activate
uv pip install -e . 
```

# Usage
You can run 
```bash
PYTHONPATH=src uv run src/main --help
```
from the root folder to get an overview of the available and required options.

Example:
```bash
python3 src/main.py
    --inputFolder yourPathToInputFolder
    --outputFolder yourPathToInputFolder
    --minFrequency 1
    --maxGap 0
    --minNumSequences 3
    --maxNumSequences 3
    --maxLength 3
    --accidentalTreatment REMOVE_ACCIDENTALS
    --chordTreatment LOWEST
    --restTreatment REMOVE_EIGHTS_AND_LOWER
```
You can find more examples in the "examples" folder.

## Output

The script outputs a JSON file containing a list of the motives found in the scores.
Each motive contains a list of intervals and the positions where the motives are found.

The intervals are classified into so-called interval classes. An interval class is one of:

- 0: Original — the interval in its original orientation
- 1: Inverted — the interval inverted
- 2: Mirrored — the interval mirrored
- 3: Mirrored and inverted — the interval mirrored and inverted

Intervals are then classified by interval number; e.g., a third is 3; a seventh is 7; etc.
The sign of the interval indicates direction: positive intervals are ascending, negative intervals are descending.

Positions are grouped first by interval class, then by score name, part, voice number, and finally by the absolute position in the piece and the length of the motive.
The length of the motive is determined by the positions of the first and last notes of the motive.

An example motive:

```json
{
  "intervals": {
    "interval_classes": {
      "ORIGINAl": {
        "intervals": [
          {
            "_interval": -8
          },
          {
            "_interval": -8
          },
          {
            "_interval": 10
          }
        ]
      },
      "INVERTED": {
        "intervals": [
          {
            "_interval": 8
          },
          {
            "_interval": 8
          },
          {
            "_interval": -10
          }
        ]
      },
      "MIRRORED": {
        "intervals": [
          {
            "_interval": -10
          },
          {
            "_interval": 8
          },
          {
            "_interval": 8
          }
        ]
      },
      "MIRRORED_INVERTED": {
        "intervals": [
          {
            "_interval": 10
          },
          {
            "_interval": -8
          },
          {
            "_interval": -8
          }
        ]
      }
    }
  },
  "positions": {
    "ORIGINAl": {
      "SomePiece": {
        "SomePart": {
          "0": [
            {
              "position": 35,
              "length": 3
            }
          ]
        }
      }
    },
    "1": {},
    "2": {},
    "3": {}
  }
}
```

# Analysis

The JSON file from the previous step containing the motives found in the scores can be analyzed using the script `analysis/analysis.py`.
It produces a statistical analysis of the output.
It also reorders the interval classes within each motive so that the original interval class has the highest number of entries.   

```bash
python3 analysis/analysis.py 
  --inputFile yourPathToInputFile
  --outputFolder yourPathToOutputFolder
```

Optionally, via the `--filterOverlappingPositions` or `--no-filterOverlappingPositions flag`,
you can let the analysis script filter motive positions so that positions within a motive (per interval type) do not overlap.

The script reads the JSON file and analyzes the motives,
producing a CSV file containing the following columns:

- intervals_original: The intervals of the original interval class
- intervals_inverted: The intervals of the inverted interval class
- intervals_mirrored: The intervals of the mirrored interval class
- intervals_mirrored_inverted: The intervals of the mirrored and inverted interval class
- frequency: The total number of times the motive appears in the scores (sum of all interval classes)
- frequency_original: The number of times the original interval class appears in the scores
- frequency_inverted: The number of times the inverted interval class appears in the scores
- frequency_mirrored: The number of times the mirrored interval class appears in the scores
- frequency_mirrored_inverted: The number of times the mirrored and inverted interval class appears in the scores
- in_n_pieces: The number of scores where the motive appears.
- mean_relative_frequency: The mean relative frequency of the motive in the scores over all pieces
- standard_deviation_relative_frequency: The standard deviation of the relative frequency of the motive in the scores over all pieces
- weighted_arithmetic_mean: The weighted arithmetic mean of the relative frequency of the motive in the scores over all pieces
- frequency_<piece>: The number of times the motive appears in the piece, where \<piece\> is the name of the piece
- relative_frequency_<piece>: The relative frequency of the motive in the piece, where \<piece\> is the name of the piece
