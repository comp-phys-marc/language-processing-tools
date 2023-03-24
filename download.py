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
from downloader import download_file

HELP_STRING = """
This command line utility enables a user to download files from the internet for use in the workspace.

USAGE:

    download.py -u <url> -f <filename>

    <url> is the url of the desired resource.

    <filename> is the name of the destination in the local filesystem.

LICENSE:

    This program comes with ABSOLUTELY NO WARRANTY.
    This is free software, and you are welcome to redistribute it.
    To see the full license, use "-h license".
"""


def main(argv):
    url = None
    file_name = None

    try:
        opts, args = getopt.getopt(
            argv,
            "u:f:h",
            ["url=", "filename=", "help="]
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
        elif opt in ["-u", "--url"]:
            url = arg
        elif opt in ["-f", "--filename"]:
            file_name = arg

    if url is not None and file_name is not None:
        print(f'\x1b[34m Beginning download of {url} to {file_name}. \x1b[34m')
        download_file(url, file_name)
        print(f'\x1b[34m Download written to {file_name}. \x1b[34m')

    else:
        print('\x1b[34m In order to download a file, you must provide a --url and --filename. \x1b[34m')


if __name__ == "__main__":
    main(sys.argv[1:])