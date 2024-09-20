#!/usr/bin/env bash

# Gabriel Staples
# Sept. 2024


# See my answer: https://stackoverflow.com/a/60157372/4561887
FULL_PATH_TO_SCRIPT="$(realpath "${BASH_SOURCE[-1]}")"
SCRIPT_DIRECTORY="$(dirname "$FULL_PATH_TO_SCRIPT")"
SCRIPT_FILENAME="$(basename "$FULL_PATH_TO_SCRIPT")"
SCRIPT_FILENAME_STEM="${SCRIPT_FILENAME%.*}"        # withOUT the extension
SCRIPT_FILENAME_EXTENSION="${SCRIPT_FILENAME##*.}"  # JUST the extension

cd "$SCRIPT_DIRECTORY"

SCRIPT_TO_INSTALL="path_shortener.py"
SCRIPT_TO_INSTALL_STEM="${SCRIPT_TO_INSTALL%.*}"    # withOUT the extension

echo "Installing script '$SCRIPT_TO_INSTALL' into ~/bin as '$SCRIPT_TO_INSTALL_STEM'"

mkdir -p ~/bin
ln -si "$SCRIPT_DIRECTORY/$SCRIPT_TO_INSTALL" ~/bin/"$SCRIPT_TO_INSTALL_STEM"
# also add the version with my gs initials in front to make it easy to find
ln -si "$SCRIPT_DIRECTORY/$SCRIPT_TO_INSTALL" ~/bin/"gs_$SCRIPT_TO_INSTALL_STEM"

# Check to see if ~/bin is inside the PATH, and add it if not
if [[ ":$PATH:" != *":$HOME/bin:"* ]]; then
    echo "Adding ~/bin to PATH in ~/.bashrc"
    echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
    . ~/.bashrc  # re-source the newly-updated .bashrc file
fi

echo "Done installing '$SCRIPT_TO_INSTALL_STEM'."
echo "Important: the installation was done via a symlink to" \
    "\"$SCRIPT_DIRECTORY/$SCRIPT_TO_INSTALL\", so do NOT move or delete that file."

echo "Test it with '$SCRIPT_TO_INSTALL_STEM -h'."
