

# Status

WIP; not yet functional.


# eRCaGuy_PathShortener

A tool to shorten paths on Linux (4096 chars max path length) &amp; Mac so that they can be unzipped, used, copied, etc. on Windows which has an insanely small max path length of ~256 chars.

1. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

1. Edit `config.py` as needed. 

1. Run the program:
    ```bash
    ./path_shortener.py
    ```


# Design scratch notes

Shorten ....

Design

AI PROMPT: 

> Write a python program to shorten paths to 140 chars. For long file or dir names, truncate them as necessary with `...`. Ex: "some long dir" might become "some long...". Then, a file would be created containing the rest of the dir name as "some long.../0...dir.txt". The "0" part just sorts this file to the top. 
> 
> Long filenames might go from "long really super very long filename.txt" to "long really...txt", plus a "name" file called "long really...NAME.txt", and inside that file it would contain "long really super very long filename.txt". 


# TODO

Newest on _bottom_:

Tue. 3 Sept. 2024:
1. [x] Create a "test_paths" dir with a bunch of long filenames and directories. 
    1. [x] have a script to auto-generate it. 
1. [x] Get the current dir of the script in order to have access to relative dirs. 
1. [ ] make arg1 the dir to shorten. 
    1. [x] actually, use `argparse` so we can have automatic dry-run mode, and `-F` mode for 'F'orce the changes.
    1. [ ] have the target dir where everything gets copied to be at the same level as the passed-in dir, but named "some_dir_shortened".
1. [ ] step 1: remove illegal chars in Windows from all paths
    1. [ ] to test this, add a bunch of illegal chars into the test_paths generator too
1. [ ] save (by copying into a backup) all paths in that passed-in argument
1. [ ] dry-run shorten all paths in that passed-in argument
1. [ ] when done, print out the result. 
1. [ ] in the real scenario (non-dry-run, via `-F`), copy the target dir to a new location, then apply all of the shortenings

