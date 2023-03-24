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
from data import Store

HELP_STRING = """
This command line utility enables a user perform transactions with the data store.

USAGE:

    store.py -c <compare> -s <save> -d <delete> -k <api_key> -i <index>

    <compare> is the name of a locally persisted result that you wish to compare to
    prior results which have been saved to the cloud.

    <save> is the name of a locally persisted result that you wish to save to the cloud.

    <delete> is the name of an index to delete.

    <top> is the number of top matches to return from a compare (defaults to 1).

    <api_key> is the api key you will use to authenticate with the cloud data store.

    <index> is the name of the index at which to to compare or save data.

LICENSE:

    This program comes with ABSOLUTELY NO WARRANTY.
    This is free software, and you are welcome to redistribute it.
    To see the full license, use "-h license".
"""

import joblib


def main(argv):
    index = None
    api_key = None
    compare = None
    save = None
    delete = None
    top_k = 1

    try:
        opts, args = getopt.getopt(
            argv,
            "c:s:d:t:k:i",
            ["compare=", "save=", "delete=", "top=", "api_key=", "index="]
        )
    except getopt.GetoptError:
        print(HELP_STRING)
        sys.exit(2)

    for opt, arg in opts:
        if opt in ["-h", "--help"]:
            print(HELP_STRING)
            sys.exit()
        elif opt in ["-c", "--compare"]:
            compare = arg
        elif opt in ["-s", "--save"]:
            save = arg.split(",")
        elif opt in ["-d", "--delete"]:
            delete = arg
        elif opt in ["-t", "--top"]:
            top_k = arg
        elif opt in ["-k", "--api_key"]:
            api_key = arg
        elif opt in ["-i", "--index"]:
            index = arg

    if index is not None and api_key is not None:
        if delete is not None:
            print(f'\x1b[34m Deleting "{delete}" index. \x1b[37m')
            store = Store(api_key, delete)
            store.drop_index()
            print(f'\x1b[34m Deletion successful. \x1b[37m')

        if save is not None:
            store = Store(api_key, index)
            for file in save:
                print(f'\x1b[34m Saving encoding "{file}" to {index}. \x1b[37m')
                data = joblib.load(f'saved_encodings/encoded_{file}.pkl')
                store.insert(data)
                print(f'\x1b[34m Uploaded encoding "{file}" successfully. \x1b[37m')

        if compare is not None:
            print(f'\x1b[34m Comparing "{compare}" to stored values in index {index}. \x1b[37m')
            store = Store(api_key, index)
            decoded = joblib.load(f'saved_encodings/decoded_{compare}.pkl')
            results = store.query(compare, top_k)

            print(f'\x1b[34m Matches found: \x1b[37m')
            print(results)

            # Note: this mapping is somewhat unstable... why do results
            # from pinecone seem not to be the same with each identical query?
            # I don't know and it's not something I can solve.
            for i in range(len(results)):
                batch = results[i]

                for top_result in batch:
                    for j in range(len(top_result.ids)):
                        string = decoded[i][top_result.ids[j]]
                        score = top_result.scores[j]

                        print(f'\x1b[34m Query matched "{string}" with score {score} \x1b[37m')

    else:
        print('\x1b[34m In order to store an encoding, ' + \
              'you must provide an --api_key and --index at minimum. \x1b[37m')


if __name__ == "__main__":
    main(sys.argv[1:])