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


References:

1. https://docs.python.org/3/library/pathlib.html
1. VSCode Python tutorial, incl. debugging Python!: 
   https://code.visualstudio.com/docs/python/python-tutorial
1. 


"""

# Local imports
import ansi_colors as colors
import config
import paths
import Tee

# Third party imports
from sortedcontainers import SortedList

# Python imports
import argparse
import copy
import hashlib
import inspect 
import os
import pprint
import re  # regular expressions
import shutil
import subprocess
import sys
import textwrap

from pathlib import Path 


# See my answer: https://stackoverflow.com/a/74800814/4561887
FULL_PATH_TO_SCRIPT = os.path.abspath(__file__)
SCRIPT_DIRECTORY = str(os.path.dirname(FULL_PATH_TO_SCRIPT))
SCRIPT_FILENAME = str(os.path.basename(FULL_PATH_TO_SCRIPT))
EXECUTABLE_FULL_PATH = sys.argv[0]
EXECUTABLE_NAME = os.path.basename(EXECUTABLE_FULL_PATH)

EXIT_SUCCESS = 0
EXIT_FAILURE = 1


def copy_directory(src, dst, args):
    src_path = Path(src)
    dst_path = Path(dst)

    original_src = src
    original_dst = dst
    
    if not src_path.exists():
        colors.print_red(f"Error: Source directory \"{src}\" does not exist. Exiting.")
        exit(EXIT_FAILURE)
    
    if dst_path.exists():
        colors.print_red(f"Error: Destination directory \"{dst}\" already exists.\n"
                       + f"You may need to manually remove that directory. Exiting.")
        exit(EXIT_FAILURE)
    
    # symlinks which have a missing or broken target path they point to
    broken_symlinks_list_of_tuples = []
    
    # Do the copy! Handle broken symlinks or missing src files which somehow got deleted or moved
    # during the copy. 

    try:
        shutil.copytree(
            src_path, dst_path, symlinks=args.keep_symlinks, ignore_dangling_symlinks=False)

    # Handle errors with missing files or broken symlinks
    # - NB: `shutil.Error`'s exception argument at index 0 (`shutil.Error.args[0]`) contains
    #   "a list of 3-tuples (srcname, dstname, exception)".
    # - See: https://docs.python.org/3/library/shutil.html#shutil.Error
    except shutil.Error as e:
        errors_list_of_tuples = e.args[0]
        for src, dst, error_str in errors_list_of_tuples:
            
            # debugging
            # Example debugging output:
            #   
            #   src: test_paths/broken_symlink2
            #   dst: test_paths_shortened/broken_symlink2
            #   error: [Errno 2] No such file or directory: 'test_paths/broken_symlink2'
            #   
            colors.print_yellow(f"\nWARNING:")
            colors.print_yellow(f"error: {error_str}")
            colors.print_yellow(f"src: {src}")
            colors.print_yellow(f"dst: {dst}")

            # Ensure that all errors are Error numbers I have seen before and know how to handle.
            match_obj = re.search(r"^\[Errno (\d+)\]", error_str)
            errno = int(match_obj.group(1))

            if errno == 2:
                # Check if the error is a missing file or a broken symlink, and save them
                is_broken_symlink = False
                if os.path.islink(src):
                    is_broken_symlink = True
                    broken_symlinks_list_of_tuples.append((src, dst, error_str))
                else:
                    print_red("Error: missing file. This is unexpected. I only expected "
                            "broken symlinks. Somehow a file was moved or deleted during the copy.")
                    colors.print_red(f"  error: {error_str}")
                    colors.print_red(f"  src: {src}")
                    colors.print_red(f"  dst: {dst}")
                    exit(EXIT_FAILURE)

            # TODO: run the `find` command below automatically to look for circular symlinks BEFORE
            # the copy! And...probably handle them gracefully automatically too. <==================
            #
            # This warning (errno 40) happens when there are circular symlinks and it copies
            # circular symlinks repeatedly.
            # - TODO: figure out how to handle this one automatically instead of requiring user
            #   intervention.  
            elif errno == 40:
                command_to_run = f"find \"{original_src}\" -follow -printf \"\""
                colors.print_red()
                colors.print_red(
                    f"Error in {SCRIPT_FILENAME}: errno {errno}: circular "
                    f"symlinks detected. This is a known issue with `shutil.copytree()`. "
                    f"Run:"
                )
                colors.print_blue(f"{command_to_run}")
                colors.print_red(f"...to find the circular symlinks. Then, **manually fix "
                    f"them**, remove \"{original_dst}\", and try again."
                )
                colors.print_red("OR, use the `--keep_symlinks` flag to keep symlinks as symlinks "
                    "instead of copying them as files or folders.")
                colors.print_red("Exiting.")

                # TODO: get our script to do this. Meanwhile, just print the find command for us to
                # run manually.
                # result = subprocess.run(command_to_run, shell=True, check=True, 
                #     capture_output=True, text=True)
                # colors.print_blue(result.stdout)
                # colors.print_red(result.stderr)

                exit(EXIT_FAILURE)
            
            else:
                colors.print_yellow(f"error: {error_str}")
                colors.print_yellow(f"src: {src}")
                colors.print_yellow(f"dst: {dst}")
                colors.print_red(f"Error in {SCRIPT_FILENAME}: Unexpected errno: {errno}. Exiting.")
                exit(EXIT_FAILURE)


    # For each broken symlink, create a file with this name at the destination location, containing
    # appropriate error messages
    for src, dst, error_str in broken_symlinks_list_of_tuples:
        with open(dst, "w") as file:
            alignment_spaces = " "*31
            file.write(f"Error: this file was auto-generated by `{SCRIPT_FILENAME}` from the "
                       f"following broken symlink:\n\n"
                       f"source location: {alignment_spaces}'{src}'\n\n"
                       f"error_str: {error_str}\n")

    print()
    print(f"Copied \"{src}\" to \"{dst}\".")

    color = colors.FGR  # green
    if len(broken_symlinks_list_of_tuples) > 0:
        color = colors.FBY  # bright yellow

    print(f"* {color}{len(broken_symlinks_list_of_tuples)} broken symlinks were found."
          f"{colors.END}")

    if len(broken_symlinks_list_of_tuples) > 0:
        print(f"* {color}For your convenience, plain text files were autogenerated "
            f"in the new directory in place of the symlinks, with corresponding error "
            f"messages written into these autogenerated files.{colors.END}")
    
    print(f"* Note: if valid symlinks were in the source directory, their targets were "
          f"copied as real files instead of as symlinks.")

    return broken_symlinks_list_of_tuples


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


# def install():
#     """
#     Install this script into ~/bin for the user.
#     """
#     print("Installing this script into ~/bin for you via a symlink...")

#     # Nevermind. Just have them run `./INSTALL.sh` directly instead.
    
#     exit(EXIT_SUCCESS)


def parse_args():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(f"""\
            Fix and shorten long paths to make them accessible on Windows.
                                    
            This script makes a full copy of the passed-in 'dir' to a new dir called
            'dir_shortened', and performs the following on the copy:
              1. Removes illegal Windows characters from paths, 
                 including: <>:\"\\|?*
              2. Shortens all paths to a length that is acceptable on Windows, as specified by
                 you inside 'config.py'.
              3. Copies symlinks as files, so they are not broken on Windows.
            
            You may change other settings inside `config.py`.
                                    
            Example usage:
                # Fix and shorten all paths in the directory 'Taxes/2023', timing how long it takes
                time {EXECUTABLE_NAME} --meld path/to/Taxes/2023
                                    
            Source code: https://github.com/ElectricRCAircraftGuy/eRCaGuy_PathShortener
            {colors.FBB}Sponsor me:  https://github.com/sponsors/ElectricRCAircraftGuy{colors.END}
        """)
    )

    parser.add_argument("dir", type=str, nargs='?', help="Path to directory to operate on")
    # `action="store_true"` means that if the flag is present, the value will be set to `True`. 
    # Otherwise, it will be `False`.
    # parser.add_argument("-F", action="store_true", help="Force the run to NOT be a dry run")
    # parser.add_argument("-I", '--install', action="store_true", 
    #                     help="Install this program into ~/bin for you.")
    parser.add_argument("-m", "--meld", action="store_true", help="Use 'meld' to compare "
                        "the original paths with the new paths when done. Requires meld "
                        "to be installed.")
    parser.add_argument("-k", "--keep_symlinks", action="store_true", help="Keep all symlinks as "
        "symlinks rather than copying them as files or folders. This can help if you have "
        "circular symlink issues. **TODO:** rather than keeping symlinks as symlinks, find "
        "a better way to handle circularly-linked symlinks to folders.")

    # Parse arguments; note: this automatically exits the program here if the arguments are invalid
    # or if the user requested the help menu.
    args = parser.parse_args()

    # debugging
    # print(f"args.keep_symlinks = {args.keep_symlinks}")
    # print(f"args = {args}")
    # exit()

    # if args.F:
    #     print("Force flag is set.")

    # if args.install:
    #     install()

    if not args.dir:
        # Print the short help menu and an error message, and exit. 
        # - Note: the default behavior if the positional argument is missing and `nargs` is NOT set
        #   to `?` is to print the following:
        #
        #   eRCaGuy_PathShortener$ ./path_shortener.py 
        #   usage: path_shortener.py [-h] [-I] dir
        #   path_shortener.py: error: the following arguments are required: dir
        #
        parser.print_usage()
        colors.print_red("Error: missing required argument 'dir'")
        exit(EXIT_FAILURE)

    # Strip any trailing slashes from the directory path
    # print(f"args.dir before: {args.dir}")  # debugging 
    args.dir = args.dir.rstrip("/")
    # print(f"args.dir after:  {args.dir}")  # debugging

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
        colors.print_red("Error: directory not found.")
        exit(EXIT_FAILURE)
    elif not os.path.isdir(args.dir):
        colors.print_red("Error: path is not a directory.")
        exit(EXIT_FAILURE)
    elif not os.access(args.dir, os.R_OK):
        colors.print_red("Error: read permission denied.")
        exit(EXIT_FAILURE)

    # Ensure we can execute (cd into) and write to the parent directory
    if not os.access(args.parent_dir, os.X_OK):
        colors.print_red("Error: execute permission denied, so we cannot 'cd' into the parent dir.")
        exit(EXIT_FAILURE)
    elif not os.access(args.parent_dir, os.W_OK):
        colors.print_red("Error: write permission denied in the parent dir.")
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


def get_paths_to_fix(all_paths_set, max_path_len_already_used=0):
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

    path_stats.max_allowed_path_len = config.MAX_ALLOWED_PATH_LEN - max_path_len_already_used
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


def print_paths_list(paths_TO_list):
    print("\nIndex: Len: Path element list")

    for i, path_list in enumerate(paths_TO_list):
        path = paths.list_to_path(path_list)
        path_str = str(path)
        print(f"{i:4}: {len(path_str):4}: {path_list}")


def replace_chars(input_string, chars_to_replace, replacement_char):
    # Create a translation table
    translation_table = str.maketrans(chars_to_replace, replacement_char * len(chars_to_replace))
    # Translate the input string using the translation table
    return input_string.translate(translation_table)


def hash_to_hex(input_string, hex_len):
    """
    Create a hexadecimal hash of a string, returning only the first `hex_len` characters
    of the hex hash string.

    Note that uniqueness is not guaranteed, but is likely. A reasonable yet still very
    small `hex_len` to use is 4.
    """

    # Create a SHA-256 hash object
    hash_object = hashlib.sha256()
    
    # Update the hash object with the bytes of the input string
    hash_object.update(input_string.encode('utf-8'))
    
    # Get the hexadecimal digest of the hash
    hex_digest = hash_object.hexdigest().upper()
    hex_digest = hex_digest[:hex_len]
    
    return hex_digest


shorten_segment_call_cnt = 0
def shorten_segment_and_update_longest_namefiles_list(i_row, i_column,
                    paths_original_list, paths_FROM_list, 
                    paths_TO_list, paths_longest_namefiles_list, 
                    allowed_segment_len):
    """
    Shorten the segment in-place inside the paths_TO_list, while also updating the
    paths_longest_namefiles_list.
    
    OLD PLACEHOLDER CODE:
    Trivial example to just return a 0-prefixed, fixed-len incrementing number as a string:
    ```py
    global shorten_segment_call_cnt
    shorten_segment_call_cnt += 1
    str = f"{shorten_segment_call_cnt:0{allowed_segment_len}d}"
    return str
    ```
    """

    # 1. Shorten the segment in the paths_TO_list

    segment_long = paths_TO_list[i_row][i_column]
    path_TO = Path(segment_long)

    i_last_column = len(paths_TO_list[i_row]) - 1

    is_dir = True
    if i_column == i_last_column:
        is_dir = paths.is_dir(paths_FROM_list[i_row])
    
    # Only files have stems; Ex: "file.txt" is in format "stem.suffix"
    if not is_dir:
        # For files        
        stem_old = path_TO.stem        # ex: "some_file"
    else:
        # For directories
        stem_old = str(path_TO)
    
    stem_new = stem_old

    # NB: +1 for the char before the hash. Ex: "@abcd"
    if len(stem_old) > allowed_segment_len + config.HASH_LEN + 1:  
        # Hash the full original path to better ensure uniqueness
        full_path_original = str(Path(*(paths_original_list[i_row][0:i_column + 1])))
        # print(f"full_path_original: {full_path_original}")  # debugging

        # Shorten the stem
        stem_new = (stem_old[:allowed_segment_len] + config.HASH_PREFIX_FOR_SHORTENED 
                    + hash_to_hex(full_path_original, config.HASH_LEN))
    
    # Only files have stems; Ex: "file.txt" is in format "stem.suffix"
    if not is_dir:
        # For files
        segment_short = str(path_TO.with_stem(stem_new))
    else:
        # For directories
        segment_short = stem_new

    paths_TO_list[i_row][i_column] = segment_short

    if i_column < len(paths_longest_namefiles_list[i_row]):
        paths_longest_namefiles_list[i_row][i_column] = segment_short

    # debugging
    # print(f"\nallowed_segment_len: {allowed_segment_len}")
    # print(f"stem_old:       {stem_old}")
    # print(f"stem_new:       {stem_new}")
    # print(f"segment_long:   {segment_long}")
    # print(f"segment_short:  {segment_short}")

    # 2. Update the paths_longest_namefiles_list if we are at the right-most column only, since
    #    that is the namefile whose path will determine the max path length for this path
    #    shortening operation.

    if (segment_short != segment_long 
        or segment_short != paths_original_list[i_row][i_column]):
        # Recalculate the namefile for this segment, and compare it to the old namefile, and
        # keep whichever one has the longest path length.

        namefile_path = paths.make_namefile_name(segment_short, is_dir)
        # debugging [ENABLE TO SHOW THE PATH SHORTENING TAKE PLACE]
        # print(f"namefile_path: {namefile_path}")  

        if i_column == i_last_column:
            # We are at the right-most column, so also capture the namefile path into its list
            # at this column. 
            if i_column < len(paths_longest_namefiles_list[i_row]):
                paths_longest_namefiles_list[i_row][i_column] = namefile_path
        else:
            # We are in any other column, so let's construct a new total namefile path to this
            # column and compare it to the old one and keep whichever is longer.
            len_old = paths.get_len(paths_longest_namefiles_list[i_row])

            i_right = min(i_column, len(paths_longest_namefiles_list[i_row]) - 1)
            namefile_full_path_new = paths_longest_namefiles_list[i_row][0:i_right + 1]
            namefile_full_path_new[i_right] = namefile_path
            len_new = paths.get_len(namefile_full_path_new)

            if len_new > len_old:
                # TODO: come up with a test that will properly test this when I run
                # `./path_shortener_demo.sh`. Currently, I know this works just from testing it on
                # some personal lawyer docs paths manually where the code failed until I did this.
                
                # Replace the normal namefile path with the new one since this one is longer
                paths_longest_namefiles_list[i_row] = namefile_full_path_new

                # debugging
                colors.print_yellow("NOTE: USING NON-RIGHT-MOST-COLUMN NAMEFILE PATH since "
                                    "this one is longer!")
                print(f"len_old: {len_old}")
                print(f"len_new: {len_new}")
                print(f"namefile_full_path_new: {namefile_full_path_new}")

    path_len = paths.get_len(paths_longest_namefiles_list[i_row])

    return path_len


def update_paths_in_list(paths_to_update_list, path, path_chunk_list_old, i_column):
    """
    Update all paths in a list to reflect a change in a path chunk.

    Inputs:
    - paths_to_update_list: the list of paths to update
    TODO...
    """
    for path2 in paths_to_update_list:
        path2_chunk_list = path2[0:i_column + 1]
        if path2_chunk_list == path_chunk_list_old:
            # update this path in the list
            path2[0:i_column + 1] = path[0:i_column + 1]


HASH_LEN_RECOMMENDATION = ("  Increase the `HASH_LEN` in 'config.py' to reduce the chance of\n"
                         + "  name collisions, and try again. You may also need to manually fix\n"
                         + "  this in your original directory.")


def write_namefile_to_disk(namefiles_list, namefile_path, name_old, is_dir):
    """
    Write a namefile to the disk.
    """
    if namefile_path.exists():
        colors.print_red(f"Error: Namefile \"{namefile_path}\" already exists.")
        colors.print_red(HASH_LEN_RECOMMENDATION)
        # TODO: consider gracefully handling these name collisions instead of exiting here.
        colors.print_red("Exiting.")
        exit(EXIT_FAILURE)
    else:
        # Create the namefile on the disk
        with open(namefile_path, "w") as file:
            file_or_dir = "directory" if is_dir else "file"
            file.write(f"Original {file_or_dir} name:\n"
                     + f"{name_old}\n")
            
    namefiles_list.append(namefile_path)


def fix_paths(args, max_path_len_already_used):
    """
    Fix the paths in `paths_to_fix_sorted_list`: 

    1. Replace symlinks with real files. 
    2. Replace illegal Windows characters with valid ones.
    3. Shorten the paths to a length that is acceptable on Windows.

    all_paths_set: a set of all original paths in the directory

    paths_original_list   # how the paths first were before doing any renaming
    paths_FROM_list       # rename paths FROM this 
    paths_TO_list         # rename paths TO this
    # (removed) paths_noillegals_list # how the paths will look after removing illegal chars, 
                          # but withOUT shortening
    paths_longest_namefiles_list # A list of the right-most namefiles ONLY, where namefiles are the 
                          #   "my_file_name@ABCD_NAME.txt" and 
                          #   "my_dir_name@ABCD/!my_dir_name@ABCD_NAME.txt" type 
                          #   files which will store the full name of the original 
                          #   file or dir prior to removing illegal chars or shortening.
                          # - Only the right-most namefiles are needed in this list since 
                          #   they are the longest ones in any given path which will 
                          #   determine the max path length for that path.
                          # - The path is still stored as a list of path elements, same as the 
                          #   other lists above. 
    
    """

    # Note: this also automatically fixes the symlinks by replacing them with real files. 
    print("\nCopying files to a new directory...")
    shortened_dir = args.base_dir + "_shortened"
    broken_symlinks_list_of_tuples = copy_directory(args.base_dir, shortened_dir, args)

    paths_all_set, paths_to_fix_sorted_list, path_stats = walk_dir_and_exit_if_done(shortened_dir)

    # TODO: `paths_all_set` can later be used to avoid path collisions
    # as new, corrected paths are generated. For now, though, it isn't being used. 

    output_dir = os.path.join(shortened_dir, ".eRCaGuy_PathShortener")
    os.makedirs(output_dir, exist_ok=True)
    
    # Write the broken symlinks to a file
    with open (os.path.join(output_dir, "broken_symlinks.txt"), "w") as file:
        if (len(broken_symlinks_list_of_tuples) > 0):
            file.write(f"{len(broken_symlinks_list_of_tuples)} broken symlinks found:\n\n")
            
            i = 0
            for src, dst, error_str in broken_symlinks_list_of_tuples:
                file.write(f"{i}:\n")
                file.write(f"  - src:   {src}\n")
                file.write(f"  - dst:   {dst}\n")
                file.write(f"  - error: {error_str}\n")
                file.write("\n")
                i += 1
                
        else:
            file.write("No broken symlinks found.\n")

    # # debugging
    # print("\nPaths all set:")
    # for path in paths_all_set:
    #     print(path)

    # Copy the sorted list into a regular list of parts (lists) to operate on. 
    # - Paths will be renamed TO this.
    paths_TO_list = [list(Path(path).parts) for path in paths_to_fix_sorted_list]

    # fix the root path

    for path in paths_TO_list:
        path[0] = shortened_dir

    # # debugging
    # print("\nPaths TO list:", end="")
    # print_paths_list(paths_TO_list)  

    # Store the original paths for later.
    # This is how the paths first were before doing any renaming.
    paths_original_list = copy.deepcopy(paths_TO_list)
    # Other lists: see descriptions above. 
    paths_FROM_list = copy.deepcopy(paths_TO_list)
    paths_longest_namefiles_list = copy.deepcopy(paths_TO_list)


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

    print()

    # 1. Fix paths in the FROM and TO lists, and on the disk
    for i_row, path in enumerate(paths_TO_list):
        num_columns = len(path)
        i_last_column = num_columns - 1
        path_longest = paths_longest_namefiles_list[i_row]
        path_len = paths.get_len(path_longest)

        # debugging
        print(f"\nPath: {i_row:4}: {path_len:4}:       {path}")
        print(f"  num_columns: {num_columns}")
        print(f"  i_last_column: {i_last_column}")
        print(f"  path_len: {path_len}")

        # 1. Replace illegal Windows characters for ALL columns, adding a namefile for each
        #    right-most column if a rename is needed.
        i_column = i_last_column
        while i_column >= 0:
            name_old = path[i_column]
            path[i_column] = replace_chars(path[i_column], config.ILLEGAL_WINDOWS_CHARS, "_")
            name_new = path[i_column]

            # Add hashes to all renamed paths
            if name_old != name_new:
                full_path_original = str(Path(*(paths_original_list[i_row][0:i_column + 1])))

                # # debugging
                # print(f"name_old: {name_old}")
                # print(f"name_new: {name_new}")
                # print(f"full_path_original: {full_path_original}")

                # Assume it's a directory, as it can only possibly be a file if it's the right-most
                # column.  
                is_dir = True  
                if i_column == i_last_column:
                    is_dir = paths.is_dir(paths_FROM_list[i_row])  # will store False for files

                if not is_dir: 
                    # It's a file, so handle stems (where "file.txt" is in format "stem.suffix")
                    stem_new = Path(name_new).stem
                    stem_new += (config.HASH_PREFIX_FOR_ILLEGALS
                                    + hash_to_hex(full_path_original, config.HASH_LEN))
                    path_new = Path(name_new).with_stem(stem_new)
                    path[i_column] = str(path_new)
                else:
                    # It's a directory, so even if it has periods in the dir name, it has no stems
                    # to handle!
                    path[i_column] = name_new

                # Create a namefile for the right-most column if it was renamed to remove illegal 
                # Windows characters. 
                # - If the path was renamed, then it will need a namefile to store its original
                #   name.
                # - NB: nearly this same logic is also inside of
                #   `shorten_segment_and_update_longest_namefiles_list()`
                if i_column == i_last_column: 
                    namefile_path = paths.make_namefile_name(path[i_column], is_dir)
                    paths_longest_namefiles_list[i_row][i_column] = namefile_path

            i_column -= 1


        # 2. Shorten the path until it is short enough OR until we cannot shorten the segments any
        #    further
        #
        # Allow up to this many chars in a given file or folder segment, + the extra chars used to
        # identify the segment. 
        # - The shortening process below will continually shorten `allowed_segment_len` until the
        #   path is short enough, OR until this value reaches 0, at which point it cannot be
        #   shortened any further.
        max_segment_len = max(len(segment) for segment in path)
        print(f"  max_segment_len: {max_segment_len}") # debugging
        allowed_segment_len = max_segment_len
        # Always run at least once in order to check namefiles for names that were fixed above
        path_len = config.MAX_ALLOWED_PATH_LEN + 1  
        while (path_len > config.MAX_ALLOWED_PATH_LEN 
               and allowed_segment_len > 0):
            i_column = i_last_column
            # Use `> 0` so that we do NOT shorten the base dir; ex: "whatever_shortened/" 
            while i_column > 0:
                # Shorten the segment in-place inside the paths_TO_list
                path_len = shorten_segment_and_update_longest_namefiles_list(
                    i_row, i_column,
                    paths_original_list, paths_FROM_list, 
                    paths_TO_list, paths_longest_namefiles_list, 
                    allowed_segment_len)
                
                if path_len <= config.MAX_ALLOWED_PATH_LEN:
                    break

                i_column -= 1

            allowed_segment_len -= 1

        # debugging
        print(f"  Original path:        {paths_original_list[i_row]}")
        print(f"  FROM path:            {paths_FROM_list[i_row]}")
        print(f"  TO (shortened) path:  {path}")
        
        if path_len > config.MAX_ALLOWED_PATH_LEN:
            colors.print_red(f"Error: Path is still too long after shortening.")
            
            colors.print_red(f"  Original path:        {paths_original_list[i_row]}")
            colors.print_red(f"  FROM path:            {paths_FROM_list[i_row]}")
            colors.print_red(f"  TO (shortened) path:  {path}")
            
            # TODO: consider not exiting here. Perhaps I want to keep on going and let the user
            # manually fix any insufficiently-shortened paths themselves afterwards. 
            colors.print_red("Exiting.")
            exit(EXIT_FAILURE)

        # Propagate the path changes across all paths in the FROM, TO, and namefiles lists, AND ON
        # THE DISK, from L to R in the columns. 
        # - Also look for name collisions. 
        # - And create namefiles for any files or dirs that were renamed.

        # For all columns in this path, from L to R
        for i_column in range(num_columns):
            path_chunk_list_new = path[0:i_column + 1]
            path_chunk_list_old = paths_FROM_list[i_row][0:i_column + 1]

            path_chunk_new = Path(*path_chunk_list_new)
            path_chunk_old = Path(*path_chunk_list_old)

            if path_chunk_new != path_chunk_old:

                # Fix it (for both files *and* folders!) on the disk

                # 1. Check for name collisions
                if path_chunk_new.exists():
                    colors.print_red(f"Error: Path chunk \"{path_chunk_new}\" already exists. "
                            + f"Cannot perform the rename.")
                    colors.print_red(HASH_LEN_RECOMMENDATION)
                    # TODO: consider gracefully handling these name collisions instead of exiting
                    # here.
                    colors.print_red("Exiting.")
                    exit(EXIT_FAILURE)

                # 2. Perform the actual rename **on the disk!**
                path_chunk_old.rename(path_chunk_new)

                # Do NOT create namefiles here. Do it below, instead, after ALL paths have been
                # shortened sufficiently, and renamed on the disk. 

                # 3. If the path chunk is a directory, it could exist in other paths in the list, 
                # so fix (rename) it in all other places in these lists:
                if path_chunk_new.is_dir():
                    update_paths_in_list(paths_FROM_list, path, path_chunk_list_old, i_column)
                    update_paths_in_list(paths_TO_list, path, path_chunk_list_old, i_column)
                    update_paths_in_list(
                        paths_longest_namefiles_list, path, path_chunk_list_old, i_column)
                    
    # 2. AFTER shortening & renaming all paths above on the disk, write the namefiles to the disk. 
    # - This copies a lot of the logic from just above, but must be done last to avoid this bug:
    # - Ths is a bug fix for the bug described in commit 1c373ffe3640eef5ee422b0e6e42d7f1513634c6: 
    #   > path_shortener.py et al: identify & reproduce a bug!
    namefiles_list = []  # a list of all namefiles written to disk
    paths_FROM_list2 = copy.deepcopy(paths_original_list)
    for i_row, path in enumerate(paths_TO_list):
        num_columns = len(path)
        
        # For all columns in this path, from L to R
        for i_column in range(num_columns):
            path_chunk_list_new = path[0:i_column + 1]
            path_chunk_list_old = paths_FROM_list2[i_row][0:i_column + 1]

            path_chunk_new = Path(*path_chunk_list_new)
            path_chunk_old = Path(*path_chunk_list_old)

            if path_chunk_new != path_chunk_old:

                name_new = path[i_column]  # Same as `paths_TO_list[i_row][i_column]`
                name_old = paths_FROM_list2[i_row][i_column]
                namefile = paths.make_namefile_name(name_new, path_chunk_new.is_dir())
                base_dir = path_chunk_new.parent

                # 1) For all files, and for directories inside the shortened dir
                # - Ex path: "base_dir/shortened_dir@ABCD/!!shortened_dir@ABCD_NAME.txt"
                namefile_path1 =  base_dir / namefile
                # 2) Valid for directories only: at the same level as the shortened dir
                # - Ex path: "base_dir/!shortened_dir@ABCD_NAME.txt"
                # Remove one of the two `!!` chars from the front of the namefile, inside the dir.
                namefile = Path(namefile).name[1:]  # the [1:] removes one of the leading `!` chars
                namefile_path2 =  base_dir / namefile

                # # debugging
                # print(f"namefile_path1: {namefile_path1}")
                # print(f"namefile_path2: {namefile_path2}")

                write_namefile_to_disk(
                    namefiles_list, namefile_path1, name_old, path_chunk_new.is_dir())
                # The second namefile is only valid for directories
                if path_chunk_new.is_dir():
                    write_namefile_to_disk(
                        namefiles_list, namefile_path2, name_old, path_chunk_new.is_dir())

                # If the path chunk is a directory, it could exist in other paths in the list, 
                # so fix (rename) it in all other places in these lists:
                if path_chunk_new.is_dir():
                    update_paths_in_list(paths_FROM_list2, path, path_chunk_list_old, i_column)

    # Write the list of namefiles to a logfile 
    with open(os.path.join(output_dir, "namefiles_created.txt"), "w") as file:
        file.write("List of auto-created namefiles:\n\n")
        for namefile_path in namefiles_list:
            file.write(f"{namefile_path}\n")

    print("\n")

    # debugging
    print("\nPrinting paths_longest_namefiles_list:")
    print_paths_list(paths_longest_namefiles_list)
    print()


    # 3. Double-check that all paths are now valid and short enough by walking the directory tree
    #    and checking each path length one last time.
    # - also log some of the stats
    
    all_paths_set2 = walk_directory(shortened_dir)
    paths_to_fix_sorted_list2, path_stats2 = get_paths_to_fix(all_paths_set2)

    before_and_after_filename = os.path.join(output_dir, "before_and_after_paths.txt")
    
    # begin tee-ing the output to a file
    tee = Tee.Tee(before_and_after_filename)
    tee.begin()

    print("BEFORE fixing and shortening paths:")
    path_stats.print()
    print()
    print("AFTER fixing and shortening paths:")
    path_stats2.print()
    print()

    if len(paths_to_fix_sorted_list2) == 0:
        print("Path fixing and shortening has been successful!\n"
            + "All paths are now fixed for Windows (illegal chars removed, no symlinks, "
            + "and short enough).")    
    else:
        colors.print_red("Error: some paths are still too long after shortening.")
        print_paths_to_fix(paths_to_fix_sorted_list2)
        colors.print_red("Saying again: Error: some paths are still too long after shortening.")
        colors.print_blue("As an intermedite work-around until I can fix this better, run "
            "this tool again on the shortened directory.")
        # colors.print_blue("OR use the `--keep_symlinks` flag to keep symlinks as symlinks, on the "
        #     "first run, to avoid this issue until I can fix it properly.")
        colors.print_blue("TODO: gracefully handle this instead of exiting here.")
        colors.print_red("Exiting.")
        exit(EXIT_FAILURE)

    print("\nMore length stats:")
    print(f"  Max allowed path len:   {path_stats2.max_allowed_path_len} chars")
    print(f"  Max len BEFORE:         {path_stats.max_len} + {max_path_len_already_used} = "
        + f"{path_stats.max_len + max_path_len_already_used}")
    print(f"  Max len AFTER:          {path_stats2.max_len}")
    # Get the max length of the namefiles
    max_namefile_len = max([len(str(Path(*path))) for path in paths_longest_namefiles_list])
    print(f"  Max namefile len AFTER: {max_namefile_len}")
    

    # 4. Print before and after paths. Also write them to files for later `meld` comparison.

    # Write some "about" info
    with open(os.path.join(output_dir, "about.txt"), "w") as file:
        file.write("Paths shorted and fixed by \"eRCaGuy_PathShortener\":\n"
            "https://github.com/ElectricRCAircraftGuy/eRCaGuy_PathShortener\n\n"
            "Sponsor me for more: https://github.com/sponsors/ElectricRCAircraftGuy\n")

    paths_before_filename = os.path.join(output_dir, "paths_list_1_before.txt")
    paths_after_filename  = os.path.join(output_dir, "paths_list_2_after.txt")

    print("\nBefore and after paths:\n"
        + "Index:        Len: Original path\n"
        + "   ->         Len: Shortened path\n"
        + "   namefile:  Len: Longest namefile path, OR the same as the \"shortened path\" if "
        + "there is no namefile\n")
    
    # Write the before and after paths to files
    with (open(paths_before_filename, "w") as file_before, 
          open(paths_after_filename, "w") as file_after):    
        
        file_before.write("BEFORE (original) paths:\n")
        file_after.write("AFTER (fixed & shortened) paths:\n")
        
        str_to_write = "Index: Len: Path\n\n"
        file_before.write(str_to_write)
        file_after.write(str_to_write)

        # 1. The standard path view
        str_to_write = "Standard path view:\n"
        file_before.write(str_to_write)
        file_after.write(str_to_write)
        for i_path in range(len(paths_original_list)):
            original_path_str = str(Path(*paths_original_list[i_path]))
            TO_path_str = str(Path(*paths_TO_list[i_path]))
            longest_namefile_str = str(Path(*paths_longest_namefiles_list[i_path]))

            print(f"{i_path:4}:        {len(original_path_str):4}: {original_path_str}\n"
                + f"   ->        {len(TO_path_str):4}: {TO_path_str}\n"
                + f"   namefile: {len(longest_namefile_str):4}: {longest_namefile_str}\n")
            
            file_before.write(f"{i_path:4}: {len(original_path_str):4}: {original_path_str}\n")
            file_after.write(f"{i_path:4}: {len(TO_path_str):4}: {TO_path_str}\n")

        # 2. The list view
        str_to_write = "\nList path view:\n"
        file_before.write(str_to_write)
        file_after.write(str_to_write)
        for i_path in range(len(paths_original_list)):
            original_path_str = str(Path(*paths_original_list[i_path]))
            TO_path_str = str(Path(*paths_TO_list[i_path]))

            file_before.write(f"{i_path:4}: {len(original_path_str):4}: {paths_original_list[i_path]}\n")
            file_after.write(f"{i_path:4}: {len(TO_path_str):4}: {paths_TO_list[i_path]}\n")

    # The above files opened via `with` are closed automatically when the `with` block is exited.

    tee.end()  # end tee-ing the output to a file


    # 5. Perform the `meld` comparison
    
    if args.meld:
        print("\n'meld'-comparing the original and shortened directories...\n"
        + f"  Original:  {args.base_dir}/\n"
        + f"  Shortened: {shortened_dir}/\n"
        + f"NB: IN MELD, BE SURE TO CLICK THE \"Keep highlighting\" BUTTON AT THE TOP!\n"
        + f"Manually close 'meld' to continue.\n"
        )
        subprocess.run(["meld", paths_before_filename, paths_after_filename], check=True)


    return output_dir


def print_sponsor_message():
    print(f"{colors.FBB}Sponsor me for more: https://github.com/sponsors/ElectricRCAircraftGuy{colors.END}")


def walk_dir_and_exit_if_done(dir_to_walk):
    """
    Walk the directory and exit if there is nothing to do.
    """
    all_paths_set = walk_directory(dir_to_walk)
    # pprint.pprint(all_paths_set)
    paths_to_fix_sorted_list, path_stats = get_paths_to_fix(
        all_paths_set, max_path_len_already_used=len("_shortened"))
    path_stats.print()
    print()

    if len(paths_to_fix_sorted_list) == 0:
        colors.print_green("Nothing to do. Exiting...")
        print_sponsor_message()
        exit(EXIT_SUCCESS)

    print_paths_to_fix(paths_to_fix_sorted_list)

    return all_paths_set, paths_to_fix_sorted_list, path_stats


def main():
    args = parse_args()
    print_global_variables(config)

    walk_dir_and_exit_if_done(args.base_dir)

    output_dir = fix_paths(args, len("_shortened"))

    print(f"{colors.FGR}Completed successfully.{colors.END}")
    print(f"{colors.FGR}See the log files in \"{output_dir}\" for more details.{colors.END}")
    print_sponsor_message()


if __name__ == "__main__":
    main()

