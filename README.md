

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

#### Design notes 6 Sept. 2024:

Consider using pandas. I need to possibly columnize the data by considering paths as columns.  
Nah...just manually do it with splitting into lists instead! Convert paths to lists and lists back to paths.  
Remove bad chars in filenames. Then in dirs one at a time, renaming the entire column with that dir name as you go. 


**Example name reduction:**  

12 chars + `...` + 4 numbers 0-9999 (19 chars + 5 chars for `_NAME`, so find only names longer than this (24 chars)). 

Ex: 
`Abcdefghijklmnopqrstuvwxyz0123456789.txt` (36 chars + extension) turns into:  
`Abcdefghijkl...0001.txt` - 19 chars + extension, and:  
`Abcdefghijkl...0001_NAME.txt` - 24 chars + extension.

The additional filename called `Abcdefghijkl...0001_NAME.txt` will contain the full original filename:
```
Full filename:
Abcdefghijklmnopqrstuvwxyz0123456789.txt
```

**Algorithm:**  

Start at the filename, then move left to dir names.  
Once done, if it wasn't enough, reduce 12 to 11 and try again, R to L, down to 1 char + `...` + 9999.

**Dir names:**  

12 chars + `.` + 4 numbers 0-9999 + `...` (20 chars, so find only names longer than this).

`really super very long dir name` -> `really super.0001...`

...followed by a filename to continue the directory name, like this: 

`0...very long dir name`
Then, re-run the file-checker on this new filename. It may get shortened into this, for example:
`0...very lon...0001.txt`  
`0...very lon...0001_NAME.txt`  
...where the latter file contains the full original filename:
```
Full filename:
0...very long dir name
```

Don't do the actual file-system rename of file and dirs R to L until the name is guaranteed to be short enough. Once that occurs, run the actual fileIO call to rename the file or dir.

Then, propagate the changes to all other paths at that same level in the file tree.


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

Fri. 6 Sept. 2024:  <=======
1. [ ] update `generate_test_paths.py` to generate 
    1. [ ] some symlinks
    1. [x] paths with illegal windows chars (all types of chars)
1. [ ] continue work on it

Sat. 7 Sept. 2024
1. [ ] when detecting illegal Windows chars, copy the offending paths into a new sorted list data structure. 
1. [ ] after the copy, deep copy both lists for a before and after effect, and fix root paths in both new lists: illegal Windows chars and too-long paths 
1. [ ] fix illegal chars paths. Parallel make the changes in the too-long paths list 
1. [ ] fix too long paths
1. [ ] print the before and after paths.
1. [ ] produce before and after `tree` lists. `meld` compare the before and after tree lists. When meld is closed, let my program terminate
