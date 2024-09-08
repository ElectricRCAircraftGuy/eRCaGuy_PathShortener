#!/usr/bin/env bash


# See my answer: https://stackoverflow.com/a/60157372/4561887
FULL_PATH_TO_SCRIPT="$(realpath "${BASH_SOURCE[-1]}")"
SCRIPT_DIRECTORY="$(dirname "$FULL_PATH_TO_SCRIPT")"

cd "$SCRIPT_DIRECTORY"

rm -r test_paths_shortened; ./path_shortener.py test_paths
