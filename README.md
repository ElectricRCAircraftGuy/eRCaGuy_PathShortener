

# Status

WIP; not yet functional.


# eRCaGuy_PathShortener

A tool to shorten paths on Linux (4096 chars max path length) &amp; Mac so that they can be unzipped, used, copied, etc. on Windows which has an insanely small max path length of ~256 chars.

Edit `config.py`, then run the program:

```bash
./path_shortener.py
```


# Design notes

Shorten ....

Design

AI PROMPT: 

> Write a python program to shorten paths to 140 chars. For long file or dir names, truncate them as necessary with `...`. Ex: "some long dir" might become "some long...". Then, a file would be created containing the rest of the dir name as "some long.../0...dir.txt". The "0" part just sorts this file to the top. 
> 
> Long filenames might go from "long really super very long filename.txt" to "long really...txt", plus a "name" file called "long really...NAME.txt", and inside that file it would contain "long really super very long filename.txt". 

