"""
module with class definition and methods for reading and writing .grp files
Created on Jun 20, 2012
@author: David Wadden
"""

import os
import re


class GRP:
    """
    class to read .grp files and return a list
    """
    def __init__(self, src):
        # if it"s a file string, check that it exists and read the file
        if type(src) is str:
            assert os.path.exists(src), "{0} is not a valid file path. Use a list to input plate names directly".format(src)
            self.read(src)
        # if it's a list, just read it in
        elif type(src) is list:
            self.grp = src

    def read(self, in_path):
        """
        read a .grp file
        """
        with open(in_path, "r") as f:
            lines = f.readlines()
            # need the second conditional to ignore comment lines
            self.grp = [line.strip() for line in lines if line and not re.match("^#", line)]

    def write(self, out):
        """
        write a .grp file
        """
        with open(out, "w") as f:
            for x in self.grp:
                f.write(str(x) + "\n")


def write_grp(in_list, out):
    """
    standalone methods to write .grp files
    """
    with open(out, "w") as f:
        for x in in_list:
            f.write(str(x) + "\n")


def read_grp(in_path):
    """
    standalone method to read .grp files
    """
    assert os.path.exists(in_path), "The following file can't be found. in_path: {}".format(in_path)
    with open(in_path, "r") as f:
        lines = f.readlines()
        # again, second conditional ignores comment lines
        return [line.strip() for line in lines if line and not re.match("^#", line)]