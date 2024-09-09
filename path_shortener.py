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


class AnyStruct:
    """
    A class to store any data structure.
    Ex: 
    ```py
    any_struct = AnyStruct()
    any_struct.my_dict = {}
    ```
    See my answer: https://stackoverflow.com/a/77161026/4561887
    """
    pass


class Paths:
    def __init__(self):
        # intended data to be stored herein
        self.original_path = None
        self.fixed_path = None  # the Windows-friendly path with no illegal chars in Windows
        self.shortened_path = None


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


def add_to_dict(dict, key, value):
    """
    Add a key-value pair to a dictionary if the key does not already exist.
    - Note: for sets, this is not necessary. Simply use `my_set.add(item)` instead. 
    """
    if key not in dict:
        dict[key] = value
    else:
        # print(f"Key '{key}' already exists with value '{dict[key]}'")
        pass


def add_to_sorted_dict(sorted_dict, key, value):
    """
    Add multiple values under the same key by using a list as the value
    """
    if key not in sorted_dict:
        sorted_dict[key] = []

    sorted_dict[key].append(value)


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


def remove_illegal_windows_chars(sorted_illegal_paths_list, sorted_paths_dict_of_lists):
    """
    Remove illegal Windows characters from paths in `sorted_illegal_paths_list`, while also
    fixing inside `sorted_paths_dict_of_lists` all paths which were changed in the former.
    """

    pass


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
    print()

    # Copy the sorted list into a regular list to operate on
    paths_to_fix_list = list(paths_to_fix_sorted_list)

    # debugging
    # for path in paths_to_fix_list:
    #     print(f"{path}")

    #///////////// PICK BACK UP HERE!

    # Fix the root path in the copy
    # for path_len, paths in sorted_paths_dict_of_lists_2.items():
    #     for i, path in enumerate(paths):
    #         new_path = path.replace(args.base_dir, shortened_dir)
    #         sorted_paths_dict_of_lists_2[path_len][i] = new_path


    # remove_illegal_windows_chars(sorted_illegal_paths_list_2, sorted_paths_dict_of_lists_2)


    # #########3
    # # Update the root dir in all paths
    # for path_len, paths in sorted_paths_dict_of_lists.items():
    #     for path in paths:
    #         new_path = path.replace(args.base_dir, shortened_dir)
    #         print(f"  {path} -> {new_path}")

    # # Fix paths with illegal Windows chars 
    # #



    # ############3
    # # Remove the paths that are not too long 
    # for path_len, paths in sorted_paths_dict_of_lists.items():
    #     print(f"{path_len:4}: ", end="")
    #     for i, path in enumerate(paths):
    #         if i == 0:
    #             print(f"{path}")
    #         else:
    #             print(f"      {path}")


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





