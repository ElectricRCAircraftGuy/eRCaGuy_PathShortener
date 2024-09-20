

# See also

1. Main [README.md](README.md)


# Design notes and TODOs


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
`Abcdefghijkl.0001.txt` - 12 + 5 chars + extension, and:  
`Abcdefghijkl.0001_NAME.txt` - 12 + 10 chars + extension.

UPDATE: use `@` instead of `.` as the separator, because `.` is used to separate the path stem from the extension, which confuses the `pathlib` library when fixing names otherwise. <===

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
Full, original filename on Linux:
really super very long dir name
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
1. [x] update `generate_test_paths.py` to generate 
    1. [x] some symlinks
    1. [x] paths with illegal windows chars (all types of chars)
1. [x] continue work on it

Sat. 7 Sept. 2024
1. [x] when detecting illegal Windows chars, copy the offending paths into a new sorted list data structure. 
    It is called `sorted_illegal_paths_list`
1. [x] after the copy, deep copy both lists for a before and after effect
1. [x] ...and fix root paths in both new lists: illegal Windows chars and too-long paths 
1. [x] fix illegal chars paths. Parallel make the changes in the too-long paths list if the path was in that list too (find a way to search for it, using its length as the index key) 
1. [x] fix too long paths
1. [x] print the before and after paths.
1. [x-did file paths instead] produce before and after `tree` lists. `meld` compare the before and after tree lists. When meld is closed, let my program terminate

Sun. 8 Sept. 2024
1. [x] Index into a sorted list. Can you? yes!
1. [x] Try to index into a path object too. Can you?
    Yes!
    ```py
    from pathlib import Path
    p = Path('test_paths/phi_mu_shines_sky_iota/alpha_waves_eta_phi_phi/omega_sun_forest_wind_nu/bright_iota_sky_omicron_dog/<>:"\|?*_forest_lambda_tau_chi/delta_lambda_sky_wind_sky/waves_lazy_wind_psi_ocean/zeta_quick_xi_whisper_xi/nu_omega_gamma_brown_lazy<_symlink.txt')

    p.parts
    len(p.parts)
    ```
1. [x] Algorithm to implement:
    Don't fix names beforehand. Instead:
    Start at top and go down the path list.

    For a given path:

    Iterate over all columns, beginning at the far right. For a given column, Replace illegal chars, then shorten it. Make that change to the disk. Propagate it across all other paths in the list at this column index IF IT IS A DIR NOT A FILE, including the path we are currently on. Go to the column to the left. Repeat.

    When done with all columns, check the path length. If still too long, shorten paths even more, starting at the right-most column.

    Done.

Tue. 10 Sept. 2024
1. [x] Continue work in `fix_paths()` and `shorten_segment()` functions. 
1. [x] figure out where to actually make the changes onto the disk, too, including after replacing
    illegal chars. Probably make a new function for this, and call it after shortening the paths,
    comparing the new to the old paths and only making changes in the list of paths and on the disk
    if they differ. 
    - See "# Propagate the change across all paths in the list" for where to pick back up.
1. [x] Add/fix these:
    paths_original_list  # how the paths first were before doing any renaming
    paths_from_list      # rename paths FROM this 
    paths_to_list        # rename paths TO this
1. [x] begin with 24 chars shortened segment length, not 12 chars?

Sun. 15 Sept. 2024
1. [x] finish `meld` comparison of before and after paths 
1. [x] In `fix_paths()`, double-check that all paths are short enough by walking the directory tree again and checking lengths one last time 
1. [wip] Write the `shorten_segment()` function [this is a lot of work!]

Mon. 16 Sept. 2024
1. [x] path_shortener.py: `shorten_segment()`: 
    Store new max path length into a global, or passed-out, list of lists here based on
    the fact that for dirs you will also get a file named "000@dir_name@abcd_NAME" stored inside
    the dir, and for files you will get a file named "file_name@abcd_NAME.txt" stored in the same
    dir as the original file.
    - Then use that list of lists of lengths outside this func to see if you need to shorten the
      path even more, or if we are done.
1. [x] Have a list of name files. EVERY row needs a single name file. Because it wouldn't be in the list if it wasn't too long or named wrong, right??
    Done: `paths_longest_namefiles_list`
1. [nah] Also check for duplicates rows/paths in the list! If there are any duplicates we need to deconflict them. 
1. [nah--I look for collision avoidance when I create the namefiles. If there are collisions, tell the user to increase the hash_len in the config file instead] Add collision avoidance
    Add collision detection as I go to do the renames. For each row and [0:i_row+1] column, see if the path_TO is already on the disk by checking for it in a full path set which we got by first walking the directory tree. If it already exists, then find my hash number and increment it by one until it doesn't collide. 
    [nah] if you get increment up to 0xffff in the hash and still are colliding, error out.

Tue. 17 Sept. 2024
1. [x] Make the quantity of hash chars a user configuration parameter! Comment in the error messages to increase it if path conflicts arise and the program exits early.
1. [x] BUG FIX!: `paths_TO_list` is sorted out of order! Sometimes the trailing `hello` dir sorts as the first (longest) dir in the list, which is wrong, and sometimes `hel\o` sorts as the first (longest) dir in the list, which is right, since it will require a namefile at `hel_o/!hel_o_NAME.txt`, making it the longest path. 
    So, fix this by re-sorting the list based on the length of the path considering any namefiles that need to be created. <===
    [x-yes: this worked] EVEN BETTER PERHAPS: don't resort the list. Instead, simply avoid making the namefiles until the end, since they could change.
---
1. [x] Copy the output dir to Windows and look at it. Does `!` sort to the top? I think so. Consider making it `0!` instead, so it sorts to the top on Linux too.
    Yes, `!` sorts to the top on Windows, and `!!` sorts even higher on Windows. So, let's make the main dir's namefile begin with `!!` instead.
1. [x] Add a hash (of the original name) to the names of files renamed due to illegal chars, too. This will help avoid name collisions and make it more obvious that these files have been renamed.
    - Consider using a hash of 3 chars instead of 4? Nah, just use 4.

Fri. 20 Sept. 2024
1. [x] Store output files into dir_shortened/.path_shortener/ instead of in dir_shortened_OUTPUT/
1. [x] Add a list and file to store all created namefiles too.
        Store it into that output dir as "namefiles_created.txt"
1. [x] Save the "Before and after paths" output to a file called "before_and_after_paths.txt" in the same dir as the output files. Use my `tee` library to make this easier since I want it to go to stdout too.
1. [not needed; just increase the hash length to avoid name collisions instead, if they occur] Maybe store final, shortened values in a set? 
How can I guarantee no duplicate path names??
    Maybe check the disk at the time of renaming, and if a file already exists, convert the hash to a number and increment it until it decollides??
1. [x] Consider moving directory namefiles up one level to be at the same level as the dir they are in, or, even better, putting them in BOTH locations so we can quickly and easily find the original directory name easily. <==
1. [x] review and fix the program arguments and help menu
1. [x] Write user documentation about the program, its output, and how to use it in the main README.md file.
1. [ ] restore `meld` comparison at the end of the program
    Add a `-m` or `--meld` option to enable it.
1. [ ] post it to https://news.ycombinator.com/show
1. [ ] post it to LinkedIn
