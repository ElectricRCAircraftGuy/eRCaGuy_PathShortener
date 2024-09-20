#!/usr/bin/env bash


# See my answer: https://stackoverflow.com/a/60157372/4561887
FULL_PATH_TO_SCRIPT="$(realpath "${BASH_SOURCE[-1]}")"
SCRIPT_DIRECTORY="$(dirname "$FULL_PATH_TO_SCRIPT")"
SCRIPT_FILENAME="$(basename "$FULL_PATH_TO_SCRIPT")"
SCRIPT_FILENAME_STEM="${SCRIPT_FILENAME%.*}"        # withOUT the extension
SCRIPT_FILENAME_EXTENSION="${SCRIPT_FILENAME##*.}"  # JUST the extension

# # debug prints
# echo "FULL_PATH_TO_SCRIPT:       $FULL_PATH_TO_SCRIPT"
# echo "SCRIPT_DIRECTORY:          $SCRIPT_DIRECTORY"
# echo "SCRIPT_FILENAME:           $SCRIPT_FILENAME"
# echo "SCRIPT_FILENAME_STEM:      $SCRIPT_FILENAME_STEM"
# echo "SCRIPT_FILENAME_EXTENSION: $SCRIPT_FILENAME_EXTENSION"

cd "$SCRIPT_DIRECTORY"

rm -r test_paths_shortened
./path_shortener.py test_paths | tee "${SCRIPT_FILENAME_STEM}_log.txt"
