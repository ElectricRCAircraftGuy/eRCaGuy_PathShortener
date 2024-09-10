#!/usr/bin/env python3

"""
Shorten long paths to make them accessible on Windows.

Example usage:

```bash
# General example 
./path_shortener.py test_paths

rm -r test_paths_shortened; ./path_shortener.py test_paths
# <======= BEST ========

# Help menu
./path_shortener.py -h

# **Dry-run** the script on a directory
./path_shortener.py /path/to/directory

# Actually run the script on a directory (without the `-F` "force" flag, it will be a dry-run)
./path_shortener.py -F /path/to/directory
```

"""

# Local imports
import config
import paths

# Third party imports
from sortedcontainers import SortedList

# Python imports
import argparse
import copy
import inspect 
import os
import pprint
import shutil
import textwrap

from pathlib import Path 


# See my answer: https://stackoverflow.com/a/74800814/4561887
FULL_PATH_TO_SCRIPT = os.path.abspath(__file__)
SCRIPT_DIRECTORY = str(os.path.dirname(FULL_PATH_TO_SCRIPT))

EXIT_SUCCESS = 0
EXIT_FAILURE = 1


def copy_directory(src, dst):
    src_path = Path(src)
    dst_path = Path(dst)
    
    if not src_path.exists():
        print(f"Error: Source directory {src} does not exist. Exiting.")
        exit(EXIT_FAILURE)
    
    if dst_path.exists():
        print(f"Error: Destination directory {dst} already exists. Exiting.")
        exit(EXIT_FAILURE)
    
    shutil.copytree(src_path, dst_path)
    print(f"Copied \"{src}\" to \"{dst}\"")
    print("  Note: if symlinks were in the source directory, they were copied as real files.")


# class AnyStruct:
#     """
#     A class to store any data structure.
#     Ex: 
#     ```py
#     any_struct = AnyStruct()
#     any_struct.my_dict = {}
#     ```
#     See my answer: https://stackoverflow.com/a/77161026/4561887
#     """
#     pass


# class Paths:
#     def __init__(self):
#         # intended data to be stored herein
#         self.original_path = None
#         self.fixed_path = None  # the Windows-friendly path with no illegal chars in Windows
#         self.shortened_path = None


class PathStats:
    def __init__(self):
        self.max_allowed_path_len = None
        self.max_len = None
        self.total_path_count = 0
        self.too_long_path_count = None
        self.symlink_path_count = None
        self.illegal_windows_char_path_count = None
        self.paths_to_fix_count = None

    def print(self):
        print("Path stats:")
        print(f"  max_allowed_path_len: {self.max_allowed_path_len}")
        print(f"  max_len: {self.max_len}")
        print(f"  total_path_count: {self.total_path_count}")
        print(f"  too_long_path_count: {self.too_long_path_count}")
        print(f"  symlink_path_count: {self.symlink_path_count}")
        print(f"  illegal_windows_char_path_count: {self.illegal_windows_char_path_count}")
        print(f"  paths_to_fix_count: {self.paths_to_fix_count}")
        print()


def print_global_variables(module):
    """
    Print all global variables in a module.
    """

    # members = inspect.getmembers(module)
    # global_vars = {
    #     name: value for name, value in members 
    #     if not inspect.ismodule(value) 
    #     and not inspect.isfunction(value) 
    #     and not name.startswith("__")
    # }
    #
    # print(f"Global variables in module: {module.__name__}:")
    # for name, value in global_vars.items():
    #     print(f"  {name}: {value}")
    
    global_vars = [
        "WINDOWS_MAX_PATH_LEN",
        "PATH_LEN_ALREADY_USED",
        "MAX_ALLOWED_PATH_LEN",
    ]
    
    print(f"Global variables in module: {module.__name__}:")
    for name in global_vars:
        value = getattr(module, name)
        print(f"  {name}: {value}")

    print()


# def add_to_dict(dict, key, value):
#     """
#     Add a key-value pair to a dictionary if the key does not already exist.
#     - Note: for sets, this is not necessary. Simply use `my_set.add(item)` instead. 
#     """
#     if key not in dict:
#         dict[key] = value
#     else:
#         # print(f"Key '{key}' already exists with value '{dict[key]}'")
#         pass


# def add_to_sorted_dict(sorted_dict, key, value):
#     """
#     Add multiple values under the same key by using a list as the value
#     """
#     if key not in sorted_dict:
#         sorted_dict[key] = []

#     sorted_dict[key].append(value)


def walk_directory(path):
    """
    Walk a directory and return all unique paths in a Python set (hash set).
    """
    
    all_paths_set = set()

    for root_dir, subdirs, files in os.walk(path):
        # print(f"Root dir: {root_dir}\t(Len: {len(root_dir)})")
        all_paths_set.add(root_dir)
        
        for dirname in subdirs:
            subdir_path = os.path.join(root_dir, dirname)
            # print(f"  Subdir: {subdir_path}\t(Len: {len(subdir_path)})")
            all_paths_set.add(subdir_path)

        for filename in files:
            file_path = os.path.join(root_dir, filename)
            # print(f"  File:   {file_path}\t(Len: {len(file_path)})")
            all_paths_set.add(file_path)

    return all_paths_set


def parse_args():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent("""\
            Shorten long paths to make them accessible on Windows.
            This script makes a copy of 'dir', called 'dir_shortened', and performs the 
            following on the copy:
              1. Removes illegal Windows characters from paths.
              2. Shortens all paths to a length that is acceptable on Windows.
              3. Copies symlinks as files, so they are not broken on Windows.
            You may change other settings inside `config.py`.  
        """)
    )
    # `action="store_true"` means that if the flag is present, the value will be set to `True`. 
    # Otherwise, it will be `False`.
    parser.add_argument("-F", action="store_true", help="Force the run to NOT be a dry run")
    parser.add_argument("dir", type=str, help="Path to directory to operate on")

    # Parse arguments; note: this automatically exits the program here if the arguments are invalid
    # or if the user requested the help menu.
    args = parser.parse_args()

    if args.F:
        print("Force flag is set.")

    args.parent_dir = os.path.dirname(args.dir)

    # is parent_dir empty?
    if not args.parent_dir:
        args.parent_dir = "."

    args.base_dir = os.path.basename(args.dir)

    print(f"dir:        {args.dir}")
    print(f"parent_dir: {args.parent_dir}")
    print(f"base_dir:   {args.base_dir}")
    
    # Check if the directory exists, if it is not a dir, and if there are permission errors
    if not os.path.exists(args.dir):
        print("Error: directory not found.")
        exit(EXIT_FAILURE)
    elif not os.path.isdir(args.dir):
        print("Error: path is not a directory.")
        exit(EXIT_FAILURE)
    elif not os.access(args.dir, os.R_OK):
        print("Error: read permission denied.")
        exit(EXIT_FAILURE)

    # Ensure we can execute (cd into) and write to the parent directory
    if not os.access(args.parent_dir, os.X_OK):
        print("Error: execute permission denied, so we cannot 'cd' into the parent dir.")
        exit(EXIT_FAILURE)
    elif not os.access(args.parent_dir, os.W_OK):
        print("Error: write permission denied in the parent dir.")
        exit(EXIT_FAILURE)

    os.chdir(args.parent_dir)

    print()

    return args


def print_paths_to_fix(paths_to_fix_sorted_list):
    """
    Print the paths that need to be fixed.
    """
    print("Paths to fix, sorted by path length in descending order:")
    print("Index: Len: Path")
    for i, path in enumerate(paths_to_fix_sorted_list):
        print(f"{i:4}: {len(path):4}: {path}")


def add_unique_to_sorted_list(sorted_list, value):
    """
    Add a value to a sorted list if it is not already present.
    """
    if value not in sorted_list:
        sorted_list.add(value)


def get_paths_to_fix(all_paths_set):
    """
    Get the paths that need to be fixed and return them in a sorted list reverse-sorted by path
    length.

    Check 3 things that indicate if a path needs to be fixed:
    # 1. If the path is too long
    # 2. If there are symlinks in the path
    # 3. If there are illegal Windows characters in the path
    """
    paths_to_fix_sorted_list = SortedList(key=lambda path: -len(path))
    path_stats = PathStats()

    path_stats.max_allowed_path_len = config.MAX_ALLOWED_PATH_LEN - len("_shortened")
    path_stats.max_len = 0
    path_stats.total_path_count = len(all_paths_set)
    path_stats.too_long_path_count = 0
    path_stats.symlink_path_count = 0
    path_stats.illegal_windows_char_path_count = 0  # count of paths with illegal Windows characters    

    for path in all_paths_set:
        add_to_list = False
        path_stats.max_len = max(path_stats.max_len, len(path))

        # Check if the path is too long
        if len(path) > path_stats.max_allowed_path_len:
            path_stats.too_long_path_count += 1
            add_to_list = True

        # Check if the path is a symlink
        if os.path.islink(path):
            path_stats.symlink_path_count += 1
            add_to_list = True

        # Check if the path has illegal Windows characters
        if any(char in path for char in config.ILLEGAL_WINDOWS_CHARS):
            path_stats.illegal_windows_char_path_count += 1
            add_to_list = True

        if add_to_list:
            add_unique_to_sorted_list(paths_to_fix_sorted_list, path)

    path_stats.paths_to_fix_count = len(paths_to_fix_sorted_list)

    return paths_to_fix_sorted_list, path_stats


def print_paths_to_fix_list(paths_to_fix_list):
    print("\nIndex: Len: Path element list")

    for i, path_list in enumerate(paths_to_fix_list):
        path = paths.list_to_path(path_list)
        path_str = str(path)
        print(f"{i:4}: {len(path_str):4}: {path_list}")


def replace_chars(input_string, chars_to_replace, replacement_char):
    # Create a translation table
    translation_table = str.maketrans(chars_to_replace, replacement_char * len(chars_to_replace))
    # Translate the input string using the translation table
    return input_string.translate(translation_table)


def fix_paths(paths_to_fix_sorted_list, args):
    """
    Fix the paths in `paths_to_fix_sorted_list`: 

    1. Replace symlinks with real files. 
    2. Replace illegal Windows characters with valid ones.
    3. Shorten the paths to a length that is acceptable on Windows.
    """

    # Note: this also automatically fixes the symlinks by replacing them with real files. 
    print("\nCopying files to a new directory...")
    shortened_dir = args.base_dir + "_shortened"
    copy_directory(args.base_dir, shortened_dir)

    # Copy the sorted list into a regular list of parts (lists) to operate on
    paths_to_fix_list = [list(Path(path).parts) for path in paths_to_fix_sorted_list]

    # fix the root path

    for path in paths_to_fix_list:
        path[0] = shortened_dir

    print_paths_to_fix_list(paths_to_fix_list)  # debugging

    # Store the original paths for later
    original_paths_list = copy.deepcopy(paths_to_fix_list)

    # Fix all paths: including illegal Windows characters and path length, all at once in one
    # pass, row by row and column by column
    #
    # Algorithm:
    # 1. Start at the top and go down the path list, fixing longest paths first
    #   TODO: evaluate later if fixing **deepest** paths first is better/faster.
    # 1. For each path:
    #   1. Iterate over all columns, beginning at the far right (last column). 
    #   1. For a given column, replace illegal chars, then shorten it. 
    #   1. Go to the next column to the left. Repeat: replace illegal chars, then shorten it, etc.
    #   1. When done with all columns, check the path length. If still too long, shorten paths 
    #      even more, starting at the right-most column.
    #   1. ONCE THE PATH has all illegal chars removed, AND is short enough, make that change to the
    #      disk one column at a time, starting at the end (right-most) column. 
    #   1. If it is the last (far right) column and that path is a dir, NOT a file, then you must
    #      also propagate that change across all other paths in the list at this parent path AND
    #      column index since that dir was just renamed and we need to account for it elsewhere
    #      in our list. So, iterate over ALL PATHS from 0 to end, including the path we are 
    #      currently on since it doesn't matter. 
    #   1. If it is any column < last_column_i, then you must propagate that change across all other
    #      paths in the list at this parent path AND column index since that dir was just renamed
    #      and we need to account for it elsewhere in our list. 
    # 1. Done: all paths are fixed, and all changes have been propagated to the disk.
    # 1. Double-check that all paths are now valid and short enough by walking the directory tree
    #    and checking each path length one last time. 

    # return

    print()
    for path in paths_to_fix_list:
        num_columns = len(path)
        i_last_column = num_columns - 1
        i_column = i_last_column
        path_len = paths.get_len(path)

        print(f"Path: {path}")
        print(f"  num_columns: {num_columns}")
        print(f"  i_last_column: {i_last_column}")
        print(f"  path_len: {path_len}")


        # while num_chars > config.MAX_ALLOWED_PATH_LEN:
        #     while i_column >= 0:
                

        #         i_column -= 1

        #     for i_column, element in enumerate(path):
        #         path[i_column] = replace_chars(element, config.ILLEGAL_WINDOWS_CHARS, "_")




    # 2. fix the paths with illegal Windows characters

    # 2.A. Fix the paths 
    # for path_elements_list in paths_to_fix_list:
    #     for i_column, element in enumerate(path_elements_list):
    #         path_elements_list[i_column] = replace_chars(element, config.ILLEGAL_WINDOWS_CHARS, "_")

    # print_paths_to_fix_list(paths_to_fix_list)  # debugging

    # 2.B. Apply the changes to disk


    # 3. shorten the paths

    # Fix the root path in the copy
    # for path_len, paths in sorted_paths_dict_of_lists_2.items():
    #     for i, path in enumerate(paths):
    #         new_path = path.replace(args.base_dir, shortened_dir)
    #         sorted_paths_dict_of_lists_2[path_len][i] = new_path


    # remove_illegal_windows_chars(sorted_illegal_paths_list_2, sorted_paths_dict_of_lists_2)


def main():
    args = parse_args()
    print_global_variables(config)

    all_paths_set = walk_directory(args.base_dir)
    # pprint.pprint(all_paths_set)
    paths_to_fix_sorted_list, path_stats = get_paths_to_fix(all_paths_set)
    path_stats.print()

    if len(paths_to_fix_sorted_list) == 0:
        print("Nothing to do. Exiting...")
        exit(EXIT_SUCCESS)

    print_paths_to_fix(paths_to_fix_sorted_list)
    fix_paths(paths_to_fix_sorted_list, args)


if __name__ == "__main__":
    main()





