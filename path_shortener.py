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
import textwrap


# See my answer: https://stackoverflow.com/a/74800814/4561887
FULL_PATH_TO_SCRIPT = os.path.abspath(__file__)
SCRIPT_DIRECTORY = str(os.path.dirname(FULL_PATH_TO_SCRIPT))


class global_vars: #/////////////
    pass


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
        "MAX_PATH_LEN",
    ]
    
    print(f"Global variables in module: {module.__name__}:")
    for name in global_vars:
        value = getattr(module, name)
        print(f"  {name}: {value}")

    print()


# def get_paths(path):
#     """
#     Obtain all paths in the directory `path`. 
#     """

#     if os.path.isdir(path):
#         paths = [os.path.join(path, f) for f in os.listdir(path)]
#         return paths
    
#     return None

def walk_directory(path):
    """
    Walk a directory and return all paths. ///////////
    """
    
    for root_dir, subdirs, files in os.walk(path):
        # Measure the path length of the current directory
        root_dir_len = len(root_dir)
        print(f"Root dir: {root_dir}\t(Len: {root_dir_len})")
        
        # Measure the path length of each subdirectory
        for dirname in subdirs:
            subdir_path = os.path.join(root_dir, dirname)
            subdir_path_len = len(subdir_path)
            print(f"  Subdir: {subdir_path}\t(Len: {subdir_path_len})")
        
        # Measure the path length of each file
        for filename in files:
            file_path = os.path.join(root_dir, filename)
            file_path_len = len(file_path)
            print(f"  File:   {file_path}\t(Len: {file_path_len})")





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

    walk_directory(args.base_dir)


    # Get paths and perform operations
    # paths_list = get_paths(args.dir)
    # print(paths_list)



if __name__ == "__main__":
    main()

