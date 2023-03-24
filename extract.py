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
from metrics import Metric

HELP_STRING = """
This command line utility enables a user to extract features (type, value) from unstructured text or structured
markup language like XML or HTML.

USAGE:

    extract.py -s <source> -c <context> -o <outfile> -f <features> -t <types> -p <proximity>

    <source> is the relative path to the input file from which to extract information.

    <context> is the tag name of the top-level element in an HTML or XML file that is included in the feature extraction.

    <outfile> is the JSON file to which the results should be written.

    <features> is the ordered, comma delimited list of feature names to extract.

    <types> is the ordered, comma delimited list of the features' types. These can include any of the following:

        PhoneNumber, Email, URL, Mention, Hashtag, IpAddress, Age, Currency, 
        Temperature, Dimension, Number, Ordinal, Percent, DateTime, Boolean

    <proximity> features and their values are associated by their proximity to one another in the source file. 
    You may override the default proximity, which assumes they will be found on the same line.

LICENSE:

    This program comes with ABSOLUTELY NO WARRANTY.
    This is free software, and you are welcome to redistribute it.
    To see the full license, use "-h license".
"""


def parse_extracted_values(values):
    results = ''
    results = parse_extracted_values_helper(values, results)

    return results


def parse_extracted_values_helper(values, results):
    for i in range(len(values)):
        obj = values[i]
        if isinstance(obj, list):
            results += parse_extracted_values_helper(values[i], results)
        elif hasattr(obj, 'value'):
            results += ' ' + obj.value

    return results


def main(argv):
    source = None
    file_type = None
    context = None
    outfile = None
    features = None
    feature_types = None
    proximity = 1

    try:
        opts, args = getopt.getopt(
            argv,
            "s:c:o:f:t:p:h",
            ["source=", "context=", "outfile=", "features=", "types=", "proximity=", "help="]
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
        elif opt in ["-s", "--source"]:
            source = arg
            if "." in source:
                file_type = source.split(".")[-1]
            else:
                file_type = "text"
        elif opt in ["-c", "--context"]:
            context = arg
        elif opt in ["-o", "--outfile"]:
            outfile = arg
        elif opt in ["-p", "--proximity"]:
            proximity = int(arg)
        elif opt in ["-f", "--features"]:
            features = arg.split(",")
        elif opt in ["-t", "--types"]:
            feature_types = arg.split(",")

    if source is not None and feature_types is not None:
        print(f'\x1b[34m Beginning extraction of {features} entities with respective ' + \
              f'types {feature_types} from {source}. \x1b[37m')

        if file_type.upper() == 'XML' or file_type.upper() == 'HTML':
            data = source
        else:
            data = open(source).read()
        metric = Metric(features, feature_types, None, proximity)
        metric.populate_from_source(data, file_type.upper(), context)

        result = metric.export()

        if outfile is not None:
            destination = open(outfile, "w")
            destination.writelines(result)

            print(f'\x1b[34m Extracted features written to {outfile}. \x1b[37m')

        else:
            print(result)

    else:
        print('\x1b[34m In order to extract entities from a source file, ' + \
              'you must provide a --source and --feature_types at minimum. \x1b[37m')

if __name__ == "__main__":
    main(sys.argv[1:])