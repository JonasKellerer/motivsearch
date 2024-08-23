# Motive search

This project is a tool to search for motives in a folder of music scores in xml format.
The tool will search for motives that are repeated in the scores.

Major features of the tool are:

- Find motives across hundreds of scores, even orchestral scores
- Take mirrored, inverted and mirrored and inverted motives into account
- Filter motives by frequency, length and number of intervals
- Allow for gaps between intervals
- Option to remove accidentals from the input
- Ignores rhythms and only considers the pitch of the notes

## Algorithm details

The algorithm is loosely based on the paper [Benammar et al.](https://doi.org/10.1007/978-3-319-68765-0_2).

### Determination of mirrored and inverted motives

In contrast to Benammar et al., the algorithm does not determine mirrored and inverted motives directly.
It first determines the motives inside each score.
Then in a second step, it merges the motives across the scores, sorting the mirrored and inverted motives together.
This way, mirrored and inverted motives can be found across different scores.

### Handling of rests

While determining the intervals, rests are handled in the following manner:

- If a note is followed by a rest, the interval get the special value: "note before"
- If a rest is followed by a note, the interval get the special value: "note after"
- If a rest is followed by a rest, the interval get the special value: "rest"

The algorithm then runs as if rests are regular intervals. Thus, they can be "skipped" through the gap feature.
In the end, motives with rests are removed from the result, so it only contains regular intervals.

### Handling of slurs

The algorithm treats slurs as a single note, e.g. two quarter notes connected by a slur are treated as a single half
note.

# Installation

This project is developed for linux distributions.
It might work also for other distributions, since it runs python scripts.

For this project you need to have a running version of python3 and musecore3.
To install the necessary python packages you can run the following command:

```bash
pip install -r requirements.txt
```

# Usage

To run the script you need to execute the following command:

```bash
python3 src/main.py
    --inputFolder yourPathToInputFolder
    --outputFolder yourPathToInputFolder
    --minFrequency 2
    --maxGap 0
    --minNumSequences 3
    --maxNumSequences 3
    --maxLength 4
    --useDiatonic
```

## Settings

- `--inputFolder` : Path to the folder containing the music scores in the format of .musicxml or .xml
- `--outputFolder` : Path to the folder where the output will be saved
- `--minFrequency` : Minimum number of times a motive should appear in the scores
- `--maxGap` : Maximum number of intervals that can be skipped between two intervals of the motive
- `--minNumSequences` : Minimum number of intervals of the result motives
- `--maxNumSequences` : Maximum number of intervals of the result motives
- `--maxLength` : Maximum length of the motive (difference of the position between the first and last note)
- `--useDiatonic` : Removes accidentals from the input

## Output

The script will output a json file containing a list the motives found in the scores.
Each motive will contain a list of intervals and the positions where the motives are found.

The intervals are classified in so-called interval classes. An interval class can be either:

- 0: Original: The first occurrence of the interval, which is defined as the original
- 1: Inverted: The interval inverted
- 2: Mirrored: The interval mirrored
- 3: Mirrored and Inverted: The interval mirrored and inverted

The intervals are then classified by the interval name, e.g. a Third is 3; a Seventh is 7, etc.
The direction of the interval is defined by the sign of the interval.
Positive intervals are ascending, negative intervals are descending.

The positions are defined first by the interval class, then by the score name, then by the part, then by voice number
and finally by the absolute position in the piece and length of the motive.
The length of the motive is defined by the position of the first and last note of the motive.

An example of one motive is the following:

```json
{
  "intervals": {
    "interval_classes": {
      "0": {
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
      "1": {
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
      "2": {
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
      "3": {
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
    "0": {
      "SmokeOnTheWater_MusiX1_S.149": {
        "P2-Staff2": {
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

The json file from the previous step containing the motives found in the scores,
can be analyzed using the script `analysis/analysis.py`.

The analysis script filters first the motive positions, such that the positions inside a motive do not overlap.
This means that each occurrence of a motive can only overlap with one note of the same motive.

The script will read the json file and analyze the motives,
which in turn creates a csv file containing the following columns:

- intervals_original: The intervals of the original motive
- intervals_inverted: The intervals of the inverted motive
- intervals_mirrored: The intervals of the mirrored motive
- intervals_mirrored_inverted: The intervals of the mirrored and inverted motive
- frequency: The total number of times the motive appears in the scores (sum of all interval classes)
- frequency_original: The number of times the original motive appears in the scores
- frequency_inverted: The number of times the inverted motive appears in the scores
- frequency_mirrored: The number of times the mirrored motive appears in the scores
- frequency_mirrored_inverted: The number of times the mirrored and inverted motive appears in the scores
- in_n_pieces: The number of scores where the motive appears.
- mean_relative_frequency: The mean relative frequency of the motive in the scores over all pieces
- standard_deviation_relative_frequency: The standard deviation of the relative frequency of the motive in the scores
  over all pieces
- weighted_arithmetic_mean: The weighted arithmetic mean of the relative frequency of the motive in the scores over all
  pieces
- frequency_<piece>: The number of times the motive appears in the piece, where <piece> is the name of the piece
- relative_frequency_<piece>: The relative frequency of the motive in the piece, where <piece> is the name of the piece

It can be run with the following command:

```bash
python3 analysis/analysis.py 
  --inputFile yourPathToInputFile
  --outputFolder yourPathToOutputFolder
```

