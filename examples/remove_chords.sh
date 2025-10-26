#!/bin/bash

mkdir output_remove_chords

PYTHONPATH=../src uv run ../src/main.py \
  --inputFolder data \
  --outputFolder output_remove_chords \
  --minFrequency 1 \
  --maxGap 0 \
  --minNumSequences 3 \
  --maxNumSequences 3 \
  --maxLength 3 \
  --accidentalTreatment REMOVE_ACCIDENTALS \
  --chordTreatment REMOVE

PYTHONPATH=../src uv run ../analysis/analysis.py \
  --inputFile output_remove_chords/output.json \
  --outputFolder output_remove_chords --filterOverlappingPositions