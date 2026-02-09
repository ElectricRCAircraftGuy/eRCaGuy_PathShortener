#!/usr/bin/env python3

"""
User configuration and default settings for the path shortening tool.
"""

# Specify the maximum number of chars permitted in a path.
# - Example, if your root path on Windows where you want to unzip some content from a Linux user is
#   "C:\Users\some_username\Documents\My Long Business Name\this one particular client\2024\something else long\",
#   then that path is already 107 chars long, so you will only have ~255 - 107 = 148 chars left
#   for the rest of the path.

WINDOWS_MAX_PATH_LEN = 255  # approximate Windows limit

EXAMPLE_BASE_PATH_STR = r"\\networkshare1\sharedarea\My Documents\Client Folders\ACTIVE REPORTS 1\Last, First 1234\Client Documents\some long name that I have_shortened"
EXAMPLE_BASE_PATH_STR += "\\"  # add a trailing backslash to the path

PATH_LEN_ALREADY_USED = len(EXAMPLE_BASE_PATH_STR)  # 143 chars
PATH_LEN_ALREADY_USED = 55  # USER OVERRIDE

# The remaining chars we can use for the path. This tool will shorten paths to this length.
MAX_ALLOWED_PATH_LEN = WINDOWS_MAX_PATH_LEN - PATH_LEN_ALREADY_USED

# don't include / in this list since it's part of valid Linux paths
ILLEGAL_WINDOWS_CHARS = "<>:\"\\|?*"

# Length of the hash to append to the end of a file name to make it unique.
# - If you get name collisions when running this program, **increase this number** until they stop.
# - If you need to shorten the path further, **decrease this number**.
HASH_LEN = 3  # Default: 3

# The character or string to prefix hashes in shortened paths.
# Ex: prefix of "@" --> "@ABCD" at the end of a shortened file or dir name.
HASH_PREFIX_FOR_SHORTENED = "@"
# The character or string to prefix hashes in paths which had Windows-illegal chars in them removed.
# Ex: prefix of "#" --> "#ABCD" at the end of a fixed file or dir name.
HASH_PREFIX_FOR_ILLEGALS = "#"

# Suffix to add to the output shortened directory name.
# - To further shorten the output dir, use "_" instead of `_short`.
# - WARNING: NEVER use "" (empty string) as the suffix, as that (I haven't tested this yet though)
#   may cause the program to overwrite the original files!
SHORT_DIR_SUFFIX = "_short"  # Default: "_short".


if __name__ == "__main__":
    print(f"WINDOWS_MAX_PATH_LEN:       {WINDOWS_MAX_PATH_LEN}")
    print(f"EXAMPLE_BASE_PATH_STR:      {EXAMPLE_BASE_PATH_STR}")
    print(f"PATH_LEN_ALREADY_USED:      {PATH_LEN_ALREADY_USED}")
    print(f"MAX_ALLOWED_PATH_LEN:       {MAX_ALLOWED_PATH_LEN}")
    print(f"ILLEGAL_WINDOWS_CHARS:      {ILLEGAL_WINDOWS_CHARS}")
    print(f"HASH_LEN:                   {HASH_LEN}")
    print(f"HASH_PREFIX_FOR_SHORTENED:  {HASH_PREFIX_FOR_SHORTENED}")
    print(f"HASH_PREFIX_FOR_ILLEGALS:   {HASH_PREFIX_FOR_ILLEGALS}")


"""
Example run and output:

eRCaGuy_PathShortener$ ./config.py
WINDOWS_MAX_PATH_LEN:       255
EXAMPLE_BASE_PATH_STR:      \\networkshare1\sharedarea\My Documents\Client Folders\ACTIVE REPORTS 1\Last, First 1234\Client Documents\some long name that I have_shortened\
PATH_LEN_ALREADY_USED:      143
MAX_ALLOWED_PATH_LEN:       112
ILLEGAL_WINDOWS_CHARS:      <>:"\|?*
HASH_LEN:                   4
HASH_PREFIX_FOR_SHORTENED:  @
HASH_PREFIX_FOR_ILLEGALS:   #
"""
