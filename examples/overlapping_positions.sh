#!/bin/bash

mkdir output_overlapping_positions

PYTHONPATH=../src uv run ../src/main.py \
  --inputFolder data \
  --outputFolder output_overlapping_positions \
  --minFrequency 1 \
  --maxGap 0 \
  --minNumSequences 3 \
  --maxNumSequences 3 \
  --maxLength 3 \
  --accidentalTreatment REMOVE_ACCIDENTALS

PYTHONPATH=../src uv run ../analysis/analysis.py \
  --inputFile output_overlapping_positions/output.json \
  --outputFolder output_overlapping_positions --no-filterOverlappingPositions