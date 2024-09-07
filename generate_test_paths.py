#!/usr/bin/env python3

"""
Generate a directory structure with long human-readable folder and file names inside `test_paths/`.

References:
1. https://docs.python.org/3/library/os.html#os.makedirs
1. https://docs.python.org/3/library/os.path.html#os.path.join
1. 

"""

import os
import random
import subprocess
import sys


# See my answer: https://stackoverflow.com/a/74800814/4561887
FULL_PATH_TO_SCRIPT = os.path.abspath(__file__)
SCRIPT_DIRECTORY = str(os.path.dirname(FULL_PATH_TO_SCRIPT))

# List of common words to use for generating names
words = [
    "alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta", "iota", "kappa",
    "lambda", "mu", "nu", "xi", "omicron", "pi", "rho", "sigma", "tau", "upsilon", "phi",
    "chi", "psi", "omega", "quick", "brown", "fox", "jumps", "over", "lazy", "dog", "bright",
    "sun", "shines", "high", "sky", "blue", "ocean", "waves", "crash", "shore", "green",
    "forest", "trees", "whisper", "wind", "<>:\"\\|?*"
]

def generate_human_readable_name(num_words):
    """
    Generate a human-readable name by combining random words.
    """
    
    name = '_'.join(random.choice(words) for _ in range(num_words))
    return name


def create_long_name_structure(
        base_dir, 
        num_folders, 
        num_files_per_folder, 
        num_empty_dirs_per_folder, 
        num_words, 
        folder_depth
    ):
    """
    Create a directory structure with long human-readable folder and file names.
    """
    def create_nested_dirs(current_dir, current_depth):
        # Base case to exit recursion
        if current_depth > folder_depth:
            return

        for _ in range(num_folders):
            # Generate a human-readable folder name
            folder_name = generate_human_readable_name(num_words)
            folder_path = os.path.join(current_dir, folder_name)
            os.makedirs(folder_path, exist_ok=True)

            # Create files in the current directory
            for _ in range(num_files_per_folder):
                # Generate a human-readable file name
                file_name = generate_human_readable_name(num_words) + ".txt"
                file_path = os.path.join(folder_path, file_name)
                with open(file_path, 'w') as f:
                    f.write("This is a test file.")

            # Make empty dirs in each folder too
            for _ in range(num_empty_dirs_per_folder):
                empty_dir_name = generate_human_readable_name(num_words)
                empty_dir_path = os.path.join(folder_path, empty_dir_name)
                os.makedirs(empty_dir_path, exist_ok=True)

            # Recursively create nested directories
            create_nested_dirs(folder_path, current_depth + 1)

    # Start creating the directory structure from the base directory
    create_nested_dirs(base_dir, 1)


def move_to_recycle_bin(src_path):
    """
    Move the directory to the recycle bin, appending a number if the target already exists.
    """
    recycle_bin_dir = os.path.expanduser("~/.local/share/Trash/files")
    os.makedirs(recycle_bin_dir, exist_ok=True)

    base_name = os.path.basename(src_path)
    target_path = os.path.join(recycle_bin_dir, base_name)
    counter = 1

    while os.path.exists(target_path):
        target_path = os.path.join(recycle_bin_dir, f"{base_name}_{counter}")
        counter += 1

    subprocess.run(["mv", src_path, target_path], check=True)
    print(f"Moved {src_path} to {target_path}\n")


def main():
    base_dir = os.path.join(SCRIPT_DIRECTORY, "test_paths")

    # Move the base_dir to the recycle bin if it already exists
    if os.path.exists(base_dir):
        print(f"Moving existing test directory to the recycle bin: {base_dir}")
        move_to_recycle_bin(base_dir)

    num_folders = 1
    num_files_per_folder = 3
    num_empty_dirs_per_folder = 2
    num_words = 5  # Number of words to combine for folder and file names
    folder_depth = 8  # Depth of nested folders
    create_long_name_structure(base_dir, num_folders, num_files_per_folder, 
                               num_empty_dirs_per_folder, num_words, folder_depth)

    print(f"Test directory structure created at: {base_dir}\n")

    # Obtain and store as text the tree of the directory structure
    p = subprocess.run(["tree", base_dir], check=True, text=True, capture_output=True)

    print(f"Here is what it looks like:{p.stdout}\n")


if __name__ == "__main__":
    main()
