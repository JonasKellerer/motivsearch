# Examples

In this directory, you’ll find example scripts that provide a first introduction to using the motive finder.
These scripts were also used to evaluate the corpus from (TODO).

To run these scripts, first follow the “Installation” section of the README in the root folder.
Then run the scripts from this examples directory; for example, start `basic.sh` like this:

```bash
./basic.sh
```

For these examples, we assume you are searching for a 4‑note pattern inside the corpus provided in the `data` folder 
(`--minNumSequences 3` specifies that the output motive must have at least 3 intervals,
`--maxNumSequences 3` specifies that the output motive can have at most 3 intervals,
`--maxLength 3` specifies that the first and last interval are at most 3 steps apart—this is relevant when used with the `--maxGap` argument)
.
We do not allow gaps within the note pattern (`--maxGap 0`).
We also remove accidentals from the input data (`--accidentalTreatment REMOVE_ACCIDENTALS`).

The `main.py` script produces a JSON output of the run. To compute statistical data for this run, use the
`analysis.py` script. There you can optionally specify the input and output folders, and request that it only count motives with no
overlapping intervals within each sequence type (`--filterOverlappingPositions`).

We provide six examples::
- basic: A standard run. Removes accidentals, uses only the highest note in chords, and filters overlapping positions in the analysis.
- overlapping positions: Includes overlapping positions of motives in the analysis.
- lowest note in chord: Uses the lowest note in chords instead of the highest.
- remove chords: Removes all chords before searching for motives.
- remove eights rests and lower: Removes all rests that are eighth-note or shorter before searching for motives.
- remove sixteenth rests and lower: Removes all rests that are eighth-note or shorter before searching for motives.
