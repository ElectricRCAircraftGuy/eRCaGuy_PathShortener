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
import config
import paths

# Third party imports
from sortedcontainers import SortedList

# Python imports
import argparse
import copy
import hashlib
import inspect 
import os
import pprint
import shutil
import subprocess
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
def shorten_segment(i_row, i_column, 
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

    stem_old = path_TO.stem        # ex: "some_file"
    stem_new = stem_old

    HASH_LEN = 4

    # NB: +1 for the char before the hash. Ex: "@abcd"
    if len(stem_old) > allowed_segment_len + HASH_LEN + 1:  
        # Hash the full original path to better ensure uniqueness
        full_path_original = str(Path(*(paths_original_list[i_row][0:i_column + 1])))
        # print(f"full_path_original: {full_path_original}")  # debugging

        # Shorten the stem
        stem_new = stem_old[:allowed_segment_len] + "@" + hash_to_hex(full_path_original, HASH_LEN)
    
    segment_short = str(path_TO.with_stem(stem_new))

    paths_TO_list[i_row][i_column] = segment_short
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

    i_last_column = len(paths_TO_list[i_row]) - 1
    if i_column == i_last_column and (segment_short != segment_long or 
                                      segment_short != paths_original_list[i_row][i_column]):
        # We are at the right-most column, so also capture the namefile path into its list

        is_dir = paths.is_dir(paths_FROM_list[i_row])
        namefile_path = paths.make_namefile_name(segment_short, is_dir)
        paths_longest_namefiles_list[i_row][i_column] = namefile_path


def update_paths_in_list(paths_to_update_list, path, path_chunk_list_old, i_column):
    """
    Update all paths in a list to reflect a change in a path chunk.

    Inputs:
    - paths_to_update_list: the list of paths to update
    ...
    """
    for path2 in paths_to_update_list:
        path2_chunk_list = path2[0:i_column + 1]
        if path2_chunk_list == path_chunk_list_old:
            # update this path in the list
            path2[0:i_column + 1] = path[0:i_column + 1]


def fix_paths(all_paths_set, paths_to_fix_sorted_list, path_stats, args, max_path_len_already_used):
    """
    Fix the paths in `paths_to_fix_sorted_list`: 

    1. Replace symlinks with real files. 
    2. Replace illegal Windows characters with valid ones.
    3. Shorten the paths to a length that is acceptable on Windows.

    all_paths_set: a set of all original paths in the directory

    paths_original_list   # how the paths first were before doing any renaming
    paths_FROM_list       # rename paths FROM this 
    paths_TO_list         # rename paths TO this
    paths_noillegals_list # how the paths will look after removing illegal chars, but withOUT 
                          #   shortening
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
    copy_directory(args.base_dir, shortened_dir)

    ########## fix the first column in each path
    all_paths_list = list(all_paths_set)


    # Copy the sorted list into a regular list of parts (lists) to operate on. 
    # - Paths will be renamed TO this.
    paths_TO_list = [list(Path(path).parts) for path in paths_to_fix_sorted_list]

    # fix the root path

    for path in paths_TO_list:
        path[0] = shortened_dir

    print_paths_list(paths_TO_list)  # debugging

    # Store the original paths for later.
    # This is how the paths first were before doing any renaming.
    paths_original_list = copy.deepcopy(paths_TO_list)
    # Other lists: see descriptions above. 
    paths_FROM_list = copy.deepcopy(paths_TO_list)
    paths_noillegals_list = copy.deepcopy(paths_TO_list) ########## don't need this maybe????
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
        print(f"Path: {i_row:4}: {path_len:4}: {path}")
        print(f"  num_columns: {num_columns}")
        print(f"  i_last_column: {i_last_column}")
        print(f"  path_len: {path_len}")

        # Replace illegal Windows characters for ALL columns, adding a namefile for each right-most
        # column if a rename is needed.
        i_column = i_last_column
        while i_column >= 0:
            path[i_column] = replace_chars(path[i_column], config.ILLEGAL_WINDOWS_CHARS, "_")

            # Create a namefile for the right-most column if it was renamed
            # - NB: nearly this same logic is also inside of `shorten_segment()`
            if (i_column == i_last_column 
                and path[i_column] != paths_original_list[i_row][i_column]):

                # If the path was renamed, then it will need a namefile to store its original name.
                is_dir = paths.is_dir(paths_FROM_list[i_row])
                namefile_path = paths.make_namefile_name(path[i_column], is_dir)
                paths_longest_namefiles_list[i_row][i_column] = namefile_path

            paths_noillegals_list[i_row][i_column] = path[i_column] #### possibly delete 
            i_column -= 1

        # Shorten the path until it is short enough OR until we cannot shorten the segments 
        # any further
        #
        # Allow up to this many chars in a given file or folder segment, + the extra chars used to
        # identify the segment. 
        # - The shortening process below will continually shorten `allowed_segment_len` until the
        #   path is short enough, OR until this value reaches 0, at which point it cannot be
        #   shortened any further.
        allowed_segment_len = config.MAX_ALLOWED_SEGMENT_LEN
        path_len = paths.get_len(path_longest)
        while (path_len > config.MAX_ALLOWED_PATH_LEN 
               and allowed_segment_len > 0):
            i_column = i_last_column
            # Use `> 0` so that we do NOT shorten the base dir; ex: "whatever_shortened/" 
            while i_column > 0:
                # Shorten the path only if the path is still too long
                
                path_len = paths.get_len(path_longest)  # update
                
                if path_len <= config.MAX_ALLOWED_PATH_LEN:
                    break

                # Shorten the segment in-place inside the paths_TO_list
                shorten_segment(
                    i_row, i_column,
                    paths_original_list, paths_FROM_list, 
                    paths_TO_list, paths_longest_namefiles_list, 
                    allowed_segment_len)
                
                i_column -= 1

            allowed_segment_len -= 1
            path_len = paths.get_len(path_longest)  # update

        # debugging
        print(f"  Original path:        {paths_original_list[i_row]}")
        print(f"  FROM path:            {paths_FROM_list[i_row]}")
        print(f"  TO (shortened) path:  {path}")
        
        if path_len > config.MAX_ALLOWED_PATH_LEN:
            print(f"Error: Path is still too long after shortening.")
            
            print(f"  Original path:        {paths_original_list[i_row]}")
            print(f"  FROM path:            {paths_FROM_list[i_row]}")
            print(f"  TO (shortened) path:  {path}")
            
            # TODO: consider not exiting here. Perhaps I want to keep on going and let the user
            # manually fix any insufficiently-shortened paths themselves afterwards. 
            print("Exiting.")
            exit(EXIT_FAILURE)

        # Propagate the path changes across all paths in the FROM, TO, and namefiles lists, AND ON
        # THE DISK, from L to R in the columns. 
        ############### do work here; need to add all namefiles! ###############

        # For all columns in this path, from L to R
        for i_column in range(num_columns):
            path_chunk_list_new = path[0:i_column + 1]
            path_chunk_list_old = paths_FROM_list[i_row][0:i_column + 1]

            path_chunk_new = Path(*path_chunk_list_new)
            path_chunk_old = Path(*path_chunk_list_old)

            if path_chunk_new != path_chunk_old:
                # 1. Fix it (for both files *and* folders!) on the disk
                if path_chunk_new.exists():
                    print(f"Error: Path chunk \"{path_chunk_new}\" already exists. Exiting.")
                    print("  Note: you can try manually fixing this, OR modifying the code to"
                        + "  gracefully handle it.")
                    # TODO: consider gracefully handling this instead of exiting here.
                    exit(EXIT_FAILURE)

                # Perform the actual rename **on the disk!**
                path_chunk_old.rename(path_chunk_new)

                # 2. If the path chunk is a directory, it could exist in other paths in the list, 
                # so fix it in all other places in these lists:
                if path_chunk_new.is_dir():
                    update_paths_in_list(paths_FROM_list, path, path_chunk_list_old, i_column)
                    update_paths_in_list(paths_TO_list, path, path_chunk_list_old, i_column)
                    update_paths_in_list(
                        paths_longest_namefiles_list, path, path_chunk_list_old, i_column)
                    ###### not needed I think:
                    # update_paths_in_list(paths_noillegals_list, path, path_chunk_list_old, i_column)

    print("\n")


    # 2. Double-check that all paths are now valid and short enough by walking the directory tree
    #    and checking each path length one last time.
    
    all_paths_set2 = walk_directory(shortened_dir)
    paths_to_fix_sorted_list2, path_stats2 = get_paths_to_fix(all_paths_set2)
    
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
        print("Error: some paths are still too long after shortening.")
        print_paths_to_fix(paths_to_fix_sorted_list2)
        # TODO: gracefully handle this instead of exiting here.
        print("Exiting.")
        exit(EXIT_FAILURE)

    print("\nMore length stats:")
    print(f"  Max allowed path len:   {path_stats2.max_allowed_path_len} chars")
    print(f"  Max len BEFORE:         {path_stats.max_len} + {max_path_len_already_used} = "
        + f"{path_stats.max_len + max_path_len_already_used}")
    print(f"  Max len AFTER:          {path_stats2.max_len}")
    # Get the max length of the namefiles
    max_namefile_len = max([len(str(Path(*path))) for path in paths_longest_namefiles_list])
    print(f"  Max namefile len AFTER: {max_namefile_len}")
    

    # 3. Print before and after paths. Also write them to files for later `meld` comparison.

    output_dir = os.path.join(shortened_dir + "_OUTPUT")
    os.makedirs(output_dir, exist_ok=True)

    paths_before_filename = os.path.join(output_dir, args.base_dir + "__paths_list_before.txt")
    paths_after_filename  = os.path.join(output_dir, args.base_dir + "__paths_list_after.txt")

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

    # The file is closed automatically when the `with` block is exited.

    print("'meld'-comparing the original and shortened directories...\n"
       + f"NB: IN MELD, BE SURE TO CLICK THE \"Keep highlighting\" BUTTON AT THE TOP!\n"
       + f"  Original:  {args.base_dir}/\n"
       + f"  Shortened: {shortened_dir}/\n"
       + f"Manually close 'meld' to continue.\n"
    )

    ######### uncomment when done 
    # subprocess.run(["meld", paths_before_filename, paths_after_filename], check=True)


    # 4. `meld`-compare the `tree` output of the original and shortened directories
    #
    # UPDATE: I don't like the way the above tree comparison looks! Instead, write the before and
    # after paths to a file and compare them, rather than comparing the tree output! Done above now.
    """
    tree_before = subprocess.run(["tree", args.base_dir], 
                        check=True, text=True, capture_output=True)
    tree_after = subprocess.run(["tree", shortened_dir], 
                        check=True, text=True, capture_output=True)
    
    tree_before_filename = args.base_dir + "_tree_before.txt"
    tree_after_filename  = args.base_dir + "_tree_after.txt"

    # Write the tree outputs to files
    with open(tree_before_filename, "w") as f:
        f.write(tree_before.stdout)
    with open(tree_after_filename, "w") as f:
        f.write(tree_after.stdout)
    
    print("'meld'-comparing the original and shortened directories...\n"
       + f"  Original:  {args.base_dir}\n"
       + f"  Shortened: {shortened_dir}\n")

    subprocess.run(["meld", tree_before_filename, tree_after_filename], check=True)
    """


def main():
    args = parse_args()
    print_global_variables(config)

    all_paths_set = walk_directory(args.base_dir)
    # pprint.pprint(all_paths_set)
    paths_to_fix_sorted_list, path_stats = get_paths_to_fix(
        all_paths_set, max_path_len_already_used=len("_shortened"))
    path_stats.print()
    print()

    if len(paths_to_fix_sorted_list) == 0:
        print("Nothing to do. Exiting...")
        exit(EXIT_SUCCESS)

    print_paths_to_fix(paths_to_fix_sorted_list)
    fix_paths(all_paths_set, paths_to_fix_sorted_list, path_stats, args, len("_shortened"))

    print("Done.")
    print("Sponsor me for more: https://github.com/sponsors/ElectricRCAircraftGuy")


if __name__ == "__main__":
    main()





