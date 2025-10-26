#!/bin/bash

mkdir output_remove_sixteenth_rests_and_lower

PYTHONPATH=../src uv run ../src/main.py \
  --inputFolder data \
  --outputFolder output_remove_sixteenth_rests_and_lower \
  --minFrequency 1 \
  --maxGap 0 \
  --minNumSequences 3 \
  --maxNumSequences 3 \
  --maxLength 3 \
  --accidentalTreatment REMOVE_ACCIDENTALS \
  --restTreatment REMOVE_SIXTEENTH_AND_LOWER

PYTHONPATH=../src uv run ../analysis/analysis.py \
  --inputFile output_remove_sixteenth_rests_and_lower/output.json \
  --outputFolder output_remove_sixteenth_rests_and_lower --filterOverlappingPositions