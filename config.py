
# Specify the maximum number of chars permitted in a path. 
# - Example, if your root path on Windows where you want to unzip some content from a Linux user is
#   "C:\Users\some_username\Documents\My Long Business Name\this one particular client\2024\something else long\", 
#   then that path is already 107 chars long, so you will only have ~255 - 107 = 148 chars left 
#   for the rest of the path.
#
WINDOWS_MAX_PATH_LEN = 255  # approximate Windows limit
PATH_LEN_ALREADY_USED = len('C:\\Users\\some_username\\Documents\\My Long Business Name\\this one particular client\\2024\\something else long\\')  # 107 chars
# The remaining chars we can use for the path. This tool will shorten paths to this length.
MAX_ALLOWED_PATH_LEN = WINDOWS_MAX_PATH_LEN - PATH_LEN_ALREADY_USED
# The initial/max allowed shortened segment length, where a segment is as follows in a path:
# "segment/segment/segment".
MAX_ALLOWED_SEGMENT_LEN = 24

# don't include / in this list since it's part of valid Linux paths
ILLEGAL_WINDOWS_CHARS = "<>:\"\\|?*"  

# Length of the hash to append to the end of a file name to make it unique.
# If you get name collisions when running this program, increase this number until they stop.
# Default: 4
HASH_LEN = 4

