#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# LICENSE
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
# END_OF_LICENSE
#
#
# Dependencies:
#   - docopt:  pip install docopt
#   - sh:      pip install sh
#   - strings: pacman -S binutils   or   apt-get install binutils

"""
Textfext: Text File Extractor - extract text files from binaries

Usage: textfext.py [-h] [-s SIZE] [-p] FILE

Arguments:
    FILE    the file to extract text from

Options:
    -h, --help          Print this help and exit
    -s, --size SIZE     Set the lower limit for valid files (default is 30)
    -p, --preserve      Do not remove files under the size limit
"""

import os
import re
from sh import strings
from docopt import docopt


def main():
    args = docopt(__doc__)

    path       = args["FILE"]
    filename   = path.split("/")[-1]
    preserve   = args["--preserve"]
    size_limit = args["--size"] or 30
    size_limit = int(size_limit)

    num = re.compile(r"^\s*([0-9]+)")
    txt = re.compile(r"^\s*[0-9]+ (.*)$")

    in_txt   = False
    line_num = 0
    line_txt = ""

    for line in strings(path, "-td").splitlines():
        new_line_num = int(num.findall(line)[0])
        new_line_txt = txt.findall(line)[0]
        difference   = new_line_num - line_num

        if difference == len(line_txt) + 1 + (not in_txt):
            if not in_txt:
                print("Writing", filename + '_' + str(line_num))
                f = open(filename + '_' + str(line_num), "w")
                in_txt = True

            f.write(line_txt + '\n')

        elif difference - (len(line_txt) + 1) <= 5 and in_txt:
            f.write(line_txt + '\n')
            f.write('\n' * (difference - (len(line_txt) + 1)))

        else:
            if in_txt:
                f.write(line_txt + '\n')
                f.close()
                in_txt = False

        line_num = new_line_num
        line_txt = new_line_txt

    if in_txt:
        f.write(line_txt + '\n')
        f.close()

    if not preserve:
        for f in [ x for x in os.listdir()
                     if filename + "_" in x
                     if os.stat(x).st_size < size_limit ]:
            print("Deleting", f)
            os.remove(f)

if __name__ == "__main__":
    main()
