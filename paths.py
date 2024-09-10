#!/usr/bin/env python3

"""
Custom path manipulation library. 
"""

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


# def path_read_element(path, index):
    # path_elements_list = path_to_list(path)
    # return path_elements_list[index]


# def fix_root_path(sorted_paths_dict_of_lists, sorted_illegal_paths_list, new_root_path):
#     # Fix the root path of all the paths in the dict and list
#     for key, paths_list in sorted_paths_dict_of_lists.items():
#         for i, path in enumerate(paths_list):
#             new_path = path_replace(path, )

#             new_path = path.replace(sorted_illegal_paths_list[key], new_root_path)
#             paths_list[i] = new_path

#     for i, path in enumerate(sorted_illegal_paths_list):
#         new_path = path.replace(sorted_illegal_paths_list[i], new_root_path)
#         sorted_illegal_paths_list[i] = new_path

#     return sorted_paths_dict_of_lists, sorted_illegal_paths_list


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
