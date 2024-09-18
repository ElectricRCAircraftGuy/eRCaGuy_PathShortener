#!/usr/bin/env python3

"""
Custom path manipulation library. 
"""

import os
import pathlib


def list_to_path(path_elements_list):
    # NB: `*` here is the unpacking operator, and it's used to pass the unpacked individual elements
    # of the list as arguments to this func.
    path = pathlib.Path(*path_elements_list)
    return path


def path_to_list(path):
    path_elements_list = list(path.parts)
    return path_elements_list


def get_len(path_elements_list):
    """
    Get the path length (number of characters) in the reconstructed path which is made up of 
    this passed-in list of path elements. 

    Ex: List ["aaa", "bb", "c"] would turn into path "aaa/bb/c", and therefore the length would be
    8. 
    """
    num_chars = len(str(pathlib.Path(*path_elements_list)))
    return num_chars


def is_dir(path_elements_list):
    """
    Determine if the right-most element in the path (ie: the path as a whole) is a directory or not. 
    """
    path = list_to_path(path_elements_list)
    is_dir = path.is_dir()
    return is_dir


def make_namefile_name(file_or_dir_name, is_dir):
    """
    Make a namefile filename for the given original name. 
    
    For files:
    If the original name is "file@ABCD.doc", then the namefile name will be "file@ABCD_NAME.txt". 

    For directories:
    If the original name is "dir@ABCD", then the namefile name will be "!dir@ABCD_NAME.txt".
    """

    if is_dir:
        # Is a directory
        namefile_name =  os.path.join(file_or_dir_name, "!" + file_or_dir_name + "_NAME.txt")
    else:
        # Is a file
        path = pathlib.Path(file_or_dir_name)
        namefile_name = path.stem + "_NAME.txt"

    return namefile_name


##########
# def get_max_namefiles_len(
#         path_elements_list, right_most_column_original_name, right_most_column_is_dir):
#     """
#     Get the maximum path length based either on the current path length, *or* the namefile path 
#     length for the right-most column of the path if that segment was renamed, requiring that a 
#     namefile be created to store its original name.
#     """

#     right_most_column_new_name = path_elements_list[-1]

#     if right_most_column_new_name != right_most_column_original_name:
#         # If the right-most column was renamed, then it will need a namefile to store its original
#         # name.
#         path_elements_list_copy = path_elements_list.copy()

#         namefile = make_namefile_name(right_most_column_new_name, right_most_column_is_dir)
#         path_elements_list_copy[-1] = namefile
#         max_len = get_len(path_elements_list_copy)

#     else:
#         # If the right-most column was not renamed, then the path length is the same as the current
#         # path length.
#         max_len = get_len(path_elements_list)

#     return max_len


# Example usage
if __name__ == "__main__":

    path_elements_list = ['home', 'user', 'documents', 'file.txt']
    path = list_to_path(path_elements_list)
    print(f"Path: {path}")

    path_elements_list2 = path_to_list(path)
    print(f"path_elements_list2: {path_elements_list2}")

"""
Run & output:
```
eRCaGuy_PathShortener$ ./paths.py
Path: home/user/documents/file.txt
path_elements_list2: ['home', 'user', 'documents', 'file.txt']
```
"""
