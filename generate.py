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
import tensorflow as tf
from generator import train_model, generate, get_saved_model

HELP_STRING = """
This command line utility enables a user to generate text files using an NLP generator
that may be trained on any other sets of text files.

USAGE:

    generate.py -i <input_files> -s <sentence_seeds> -n <name> -p <persist>

    <input_files> is the list of files to use to train the model.

    <sentence_seeds> is the list of sentence fragments to have the NLP complete.

    <name> is the name of the output file data.

    <persist> is whether the model should be saved.

LICENSE:

    This program comes with ABSOLUTELY NO WARRANTY.
    This is free software, and you are welcome to redistribute it.
    To see the full license, use "-h license".
"""


def main(argv):
    input_files = None
    sentence_seeds = None
    name = None
    persist = None
    model = None
    output_file = None

    try:
        opts, args = getopt.getopt(
            argv,
            "i:s:n:p:h:m:o",
            ["input_files=", "sentence_seeds=", "name=", "persist=", "help=", "model=", "output_file="]
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
        elif opt in ["-i", "--input_files"]:
            input_files = arg.split(',')
        elif opt in ["-s", "--sentence_seeds"]:
            sentence_seeds = arg.split(',')
        elif opt in ["-n", "--name"]:
            name = arg
        elif opt in ["-p", "--persist"]:
            persist = int(arg)
        elif opt in ["-m", "--model"]:
            model = arg
        elif opt in ["-o", "--output_file"]:
            output_file = arg

    if input_files is not None and sentence_seeds is not None:
        print('\x1b[34m Beginning training of new text generator using training set: \n' + \
              f'{input_files} \nand sentence seeds: \n{sentence_seeds}. \x1b[37m')

        model, ids_from_chars, chars_from_ids = train_model(input_files, name, persist, model=None)

        results = ""

        for string in sentence_seeds:
            results += str(generate(model, chars_from_ids, ids_from_chars, string).numpy()[0]) + '\n'

        file = open(f'{name}.txt', "w")
        file.write(results)
        file.close()

    elif model is not None and sentence_seeds is not None:
        print('\x1b[34m Beginning generation of sentences using trained model' + \
              f'{model} and sentence seeds {sentence_seeds}. \x1b[37m')

        if output_file is not None:
            output = open(output_file, 'w')

        one_step_model = get_saved_model(model)

        for initial_string in sentence_seeds:
            states = None
            next_char = [initial_string]
            result = [next_char]

            for n in range(100):
                next_char, states = one_step_model.generate_one_step(next_char, states=states)
                result.append(next_char)

            result = tf.strings.join(result)

            if output_file is None:
                print(result)
            else:
                output.write(result)

        print('\x1b[34m Text generation complete. \x1b[37m')

    else:
        print('\x1b[34m In order to generate text using a new model, ' + \
              'you must provide --input_files for training and ' + \
              '--sentence_seeds at minimum. \x1b[37m')

        print('\x1b[34m In order to generate text using an existing model, ' + \
              'you must provide the model name --model and' + \
              '--sentence_seeds at minimum. \x1b[37m')


if __name__ == "__main__":
    main(sys.argv[1:])