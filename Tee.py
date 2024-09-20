#!/usr/bin/env python3

"""
Tee all stdout messages to the console and to a log file. 

Gabriel Staples
20 Sep. 2024

Prompt to GitHub Copilot to help: 
> python: tee all stdout output to a file

"""

# local imports
import ansi_colors as colors

# 3rd party imports
# NA

# standard library imports
import os
import sys


# See my answer: https://stackoverflow.com/a/74800814/4561887
FULL_PATH_TO_SCRIPT = os.path.abspath(__file__)
SCRIPT_DIRECTORY = str(os.path.dirname(FULL_PATH_TO_SCRIPT))


class Tee:
    def __init__(self, *paths):
        """
        Create a Tee object that writes to multiple files, as specified by the paths passed in.
        """
        self.paths = paths
        
    def write(self, obj):
        # Write to the original stdout
        self.stdout_bak.write(obj)

        # Write to all the log files
        for f in self.logfiles:
            f.write(obj)
            f.flush()  # Ensure the output is written immediately

    def flush(self):
        """
        This must be defined or else you get this error:
        ```
        Exception ignored in: <__main__.Tee object at 0x7fbeb88cfb20>
        AttributeError: 'Tee' object has no attribute 'flush'
        ```
        """
        for f in self.logfiles:
            f.flush()

    def begin(self):
        """
        Begin tee-ing stdout to the console and to one or more log files.
        """
        # Open all the files for writing
        self.logfiles = []
        for path in self.paths:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            self.logfiles.append(open(path, "w"))

        # Save the original stdout, and replace it with the Tee object
        self.stdout_bak = sys.stdout
        sys.stdout = self

    def end(self):
        """
        End tee-ing stdout to the console and to one or more log files.
        """
        # Close all the files
        for f in self.logfiles:
            f.close()

        # Restore sys.stdout
        sys.stdout = self.stdout_bak


def main():
    logpath = os.path.join(SCRIPT_DIRECTORY, "temp", "tee.log")
    tee = Tee(logpath)

    tee.begin()

    # Example usage
    print("This will be printed to the console and written to the file.")
    print("Another line of output.")
    colors.print_red("This will be printed to the console and written to the file. It is red.")

    tee.end()


if __name__ == "__main__":
    main()


"""
Example output:
- this output goes to both the console **and** to the log file at ""


eRCaGuy_PathShortener$ ./tee.py 
This will be printed to the console and written to the file.
Another line of output.
This will be printed to the console and written to the file. It is red.
"""
