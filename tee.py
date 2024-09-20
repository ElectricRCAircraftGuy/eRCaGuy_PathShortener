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
    def __init__(self, *files):
        self.files = files

    def write(self, obj):
        for f in self.files:
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
        for f in self.files:
            f.flush()

    def begin(self):
        """
        Begin tee-ing stdout to the console and to a log file.
        """
        self.stdout_bak = sys.stdout
        # Replace sys.stdout with the Tee object
        sys.stdout = self

    def end(self):
        """
        End tee-ing stdout to the console and to a log file.
        """
        # Restore sys.stdout
        sys.stdout = self.stdout_bak


def main():
    # Open the file in write mode
    logpath = os.path.join(SCRIPT_DIRECTORY, "temp", "output.log") 
    os.makedirs(os.path.dirname(logpath), exist_ok=True)

    logfile = open(logpath, "w")

    # Create a Tee object that writes to both stdout and the logfile
    tee = Tee(sys.stdout, logfile)

    # Replace sys.stdout with the Tee object
    tee.begin()

    # Example usage
    print("This will be printed to the console and written to the file.")
    print("Another line of output.")
    colors.print_red("This will be printed to the console and written to the file. It is red.")

    # Restore sys.stdout
    tee.end()

    # Close the logfile when done
    logfile.close()


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
