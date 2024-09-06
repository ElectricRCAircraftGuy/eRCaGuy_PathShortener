#!/usr/bin/env python3

"""
Shorten long paths to make them accessible on Windows.

Example usage:
```bash
# General example
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
    Walk a directory and return all paths. ///////
    """

    for dirpath, dirnames, filenames in os.walk('test_paths'):
        # Measure the path length of the current directory
        dirpath_length = len(dirpath)
        print(f"Directory: {dirpath} (Length: {dirpath_length})")
        
        # Measure the path length of each subdirectory
        for dirname in dirnames:
            subdir_path = os.path.join(dirpath, dirname)
            subdir_path_length = len(subdir_path)
            print(f"  Subdirectory: {subdir_path} (Length: {subdir_path_length})")
        
        # Measure the path length of each file
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            file_path_length = len(file_path)
            print(f"  File: {file_path} (Length: {file_path_length})")





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
    parser.add_argument("directory_path", type=str, help="Path to directory to operate on")

    # Parse arguments; note: this automatically exits the program here if the arguments are invalid
    # or if the user requested the help menu.
    args = parser.parse_args()

    if args.F:
        print("Force flag is set.")

    print(f"Directory path: {args.directory_path}\n")

    return args


def main():
    args = parse_args()
    print_global_variables(config)

    # Get paths and perform operations
    # paths_list = get_paths(args.directory_path)
    paths_list = walk_directory(args.directory_path)
    # print(paths_list)



if __name__ == "__main__":
    main()

