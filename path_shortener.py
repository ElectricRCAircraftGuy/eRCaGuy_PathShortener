#!/usr/bin/env python3

"""
Shorten long paths to make them accessible on Windows.

Example usage:

```bash
# General example 
# <======= RUN THIS ========
./path_shortener.py test_paths

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

# Third party imports
# NA

# Python imports
import argparse
import inspect 
import os
import pprint
import shutil
import textwrap

from pathlib import Path 


# See my answer: https://stackoverflow.com/a/74800814/4561887
FULL_PATH_TO_SCRIPT = os.path.abspath(__file__)
SCRIPT_DIRECTORY = str(os.path.dirname(FULL_PATH_TO_SCRIPT))


def copy_directory(src, dst):
    src_path = Path(src)
    dst_path = Path(dst)
    
    if not src_path.exists():
        print(f"Error: Source directory {src} does not exist. Exiting.")
        exit(1)
    
    if dst_path.exists():
        print(f"Error: Destination directory {dst} already exists. Exiting.")
        exit(1)
    
    shutil.copytree(src_path, dst_path)
    print(f"Copied {src} to {dst}")
    print("  Note: if symlinks were in the source directory, they were copied as real files.")


# /////////
# class Global_vars:
#     """
#     Global variables.
#     See my answer: https://stackoverflow.com/a/77161026/4561887
#     """
#     pass

# global_vars = Global_vars() 


# class PathData:
#     def __init__(self):
#         pass

#     # intended data to be stored herein
#     self.max_path

class Paths:
    def __init__(self):
        pass

    # # intended data to be stored herein
    # self.original_path = None
    # self.fixed_path = None  # the Windows-friendly path with no illegal chars in Windows
    # self.shortened_path = None


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


def walk_directory(path):
    """
    Walk a directory and return all paths in a set.
    """
    
    all_paths_set = set()

    max_len = 0

    for root_dir, subdirs, files in os.walk(path):
        # print(f"Root dir: {root_dir}\t(Len: {len(root_dir)})")
        all_paths_set.add(root_dir)
        max_len = max(max_len, len(root_dir))
        
        for dirname in subdirs:
            subdir_path = os.path.join(root_dir, dirname)
            # print(f"  Subdir: {subdir_path}\t(Len: {len(subdir_path)})")
            all_paths_set.add(subdir_path)
            max_len = max(max_len, len(subdir_path))

        for filename in files:
            file_path = os.path.join(root_dir, filename)
            # print(f"  File:   {file_path}\t(Len: {len(file_path)})")
            all_paths_set.add(file_path)
            max_len = max(max_len, len(file_path))

    return all_paths_set, max_len


def parse_args():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description=textwrap.dedent("""\
            Shorten long paths to make them accessible on Windows.
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
        exit(1)
    elif not os.path.isdir(args.dir):
        print("Error: path is not a directory.")
        exit(1)
    elif not os.access(args.dir, os.R_OK):
        print("Error: read permission denied.")
        exit(1)

    # Ensure we can execute (cd into) and write to the parent directory
    if not os.access(args.parent_dir, os.X_OK):
        print("Error: execute permission denied, so we cannot 'cd' into the parent dir.")
        exit(1)
    elif not os.access(args.parent_dir, os.W_OK):
        print("Error: write permission denied in the parent dir.")
        exit(1)

    os.chdir(args.parent_dir)

    print()

    return args


def main():
    args = parse_args()
    print_global_variables(config)

    all_paths_set, max_len = walk_directory(args.base_dir)
    pprint.pprint(all_paths_set)
    print(f"\nMax path length used: {max_len}")

    if (max_len < (config.MAX_ALLOWED_PATH_LEN - len("_shortened"))):
        print("All paths are already short enough. Nothing to do.")
        exit(0)
    
    print(f"Paths are too long. MAX_ALLOWED_PATH_LEN = {config.MAX_ALLOWED_PATH_LEN}. " 
        + f"Shortening paths...")

    print("Copying files to a new directory...")
    copy_directory(args.base_dir, args.base_dir + "_shortened")






if __name__ == "__main__":
    main()

