#!/usr/bin/env python3

"""
Shorten long paths to make them accessible on Windows.
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


def get_paths(path):
    """
    Placeholder function to simulate getting paths.
    """
    # Implement your logic to get paths here
    return [path]


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

    # Parse arguments
    args = parser.parse_args()

    if args.F:
        print("Force flag is set.")

    return args


def main():
    args = parse_args()
    print_global_variables(config)

    # Get paths and perform operations
    paths_list = get_paths(args.directory_path)
    print(f"Paths to operate on: {paths_list}")


if __name__ == "__main__":
    main()

