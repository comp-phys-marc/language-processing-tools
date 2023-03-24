"""
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the “Software”), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
"""

import sys
import getopt
from encoder import encode, encode_markup

HELP_STRING = """
This command line utility enables a user to encode and persist files as vector representations.

USAGE:

    encode.py -n <run_name> -f <files> -t <type> -d <directory> -s <seperator> -p <persist>

    <run_name> is a name that should uniquely name this execution.

    <files> is the comma seperated list of files to encode.

    <type> gives how the files will be treated (defaults to 'text'). Set as 'XML' or 'HTML' to 
    encode text by tag name indexes.

    <directory> is the location of the files.

    <seperator> is the seperator style used by the files.

    <persist> is whether the results should be persisted so that they can be used in subsequent operations,
    or just printed (defaults to true).

LICENSE:

    This program comes with ABSOLUTELY NO WARRANTY.
    This is free software, and you are welcome to redistribute it.
    To see the full license, use "-h license".
"""


def main(argv):
    files = None
    name = None
    directory = './'
    seperator = '\s{2,}'
    type = "text"
    persist = True
    encoding = None
    decoded_strings = None

    try:
        opts, args = getopt.getopt(
            argv,
            "n:f:t:d:s:p:k:i",
            ["run_name=", "files=", "type=", "directory=", "seperator=", "persist=", "api_key=", "index="]
        )
    except getopt.GetoptError:
        print(HELP_STRING)
        sys.exit(2)

    for opt, arg in opts:
        if opt in ["-h", "--help"]:
            if arg == 'license':
                print(open('LICENSE.txt').read())
            print(HELP_STRING)
            sys.exit()
        elif opt in ["-n", "--run_name"]:
            name = arg
        elif opt in ["-f", "--files"]:
            files = arg.split(",")
        elif opt in ["-t", "--type"]:
            type = arg
        elif opt in ["-d", "--direcrtory"]:
            directory = arg
        elif opt in ["-s", "--seperator"]:
            seperator = arg
        elif opt in ["-p", "--persist"]:
            persist = int(arg)

    if name is not None and files is not None:
        print(f'\x1b[34m Creating encoding "{name}" of {files}. \x1b[37m')

        if type == 'text':
            encoding, decoded_strings = encode(name, files, directory, seperator, persist)
        elif type == 'XML' or type == 'HTML':
            encoding, decoded_strings = encode_markup(name, files, directory, persist)

        print(f'\x1b[34m Encoded {len(decoded_strings)} batches of strings. \x1b[37m')

    else:
        print('\x1b[34m In order to encode a set of files ' + \
              'you must provide a --name and the list of --files at minimum. \x1b[37m')


if __name__ == "__main__":
    main(sys.argv[1:])