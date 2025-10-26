#!/bin/bash

mkdir output_lowest_note_in_chord

PYTHONPATH=../src uv run ../src/main.py \
  --inputFolder data \
  --outputFolder output_lowest_note_in_chord \
  --minFrequency 1 \
  --maxGap 0 \
  --minNumSequences 3 \
  --maxNumSequences 3 \
  --maxLength 3 \
  --accidentalTreatment REMOVE_ACCIDENTALS \
  --chordTreatment LOWEST

PYTHONPATH=../src uv run ../analysis/analysis.py \
  --inputFile output_lowest_note_in_chord/output.json \
  --outputFolder output_lowest_note_in_chord --filterOverlappingPositions