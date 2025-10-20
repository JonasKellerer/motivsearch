#!/bin/bash

MSCORE="/Applications/MuseScore 4.app/Contents/MacOS/mscore"
INPUT_DIR="$1"
OUTPUT_DIR="$INPUT_DIR/converted"
LOG_FILE="$OUTPUT_DIR/conversion.log"
ALTERNATIVE_CONVERSIONS=0

# Validate input
if [ ! -d "$INPUT_DIR" ]; then
    echo "Usage: $0 /path/to/input/dir"
    echo "Error: Invalid input directory" >&2
    exit 1
fi

mkdir -p "$OUTPUT_DIR"
> "$LOG_FILE"  # Clear log file

echo "Starting conversion process at $(date)"
echo "Input Directory: $INPUT_DIR"
echo "Output Directory: $OUTPUT_DIR"

process_file() {
    local xml_file="$1"
    local filename=$(basename -- "$xml_file")
    local base_name="${filename%.*}"
    local output_file="$OUTPUT_DIR/$base_name.musicxml"
    local alt_extensions=("mscz" "capx")
    
    # Attempt XML conversion first
    if "$MSCORE" --force "$xml_file" -o "$output_file" 2>> "$LOG_FILE"; then
        echo "✓ Converted XML: $filename"
        return 0
    fi
    
    # Try alternative extensions if XML conversion failed
    for ext in "${alt_extensions[@]}"; do
        local alt_file="$INPUT_DIR/$base_name.$ext"
        if [[ -f "$alt_file" ]]; then
            echo "Trying alternative: $base_name.$ext" >> "$LOG_FILE"
            if "$MSCORE" --force "$alt_file" -o "$output_file" 2>> "$LOG_FILE"; then
                echo "✓ Converted from $ext: $base_name.$ext"
                ((ALTERNATIVE_CONVERSIONS++))
                return 0
            fi
        fi
    done
    
    # All conversion attempts failed
    echo "❌ FAILED: $filename (no viable alternatives)"
    echo "$filename" >> "$OUTPUT_DIR/failed_files.txt"
    return 1
}

export MSCORE INPUT_DIR OUTPUT_DIR LOG_FILE ALTERNATIVE_CONVERSIONS
export -f process_file

# Process all XML files using parallel find
find "$INPUT_DIR" -maxdepth 1 -name "*.xml" -print0 | \
    xargs -0 -n1 -P4 bash -c 'process_file "$@"' _

echo "--------------------------------------------------"
echo "Conversion complete!"
echo "Alternative format conversions: $ALTERNATIVE_CONVERSIONS"
echo "Failed files listed in: $OUTPUT_DIR/failed_files.txt"
echo "Detailed log: $LOG_FILE"

[ -s "$LOG_FILE" ] && grep -i error "$LOG_FILE" | tail -n5

