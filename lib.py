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

import os
from datetime import datetime
from downloader import download_file, fetch
from encoder import encode, encode_markup
from generator import train_model, generate, get_saved_model, \
    pseudo_random_training_set_from_json, pseudo_random_training_set
from metrics import Metric
from data import Store


class FileReference:

    def __init__(self, url, name, type):
        self.url = url
        self.name = name
        self.type = type


class Configuration:

    def __init__(self, batch_size=64, buffer_size=10000, epochs=200, seq_length=100, embedding_dim=256, rnn_units=1024):
        self.batch_size = batch_size
        self.buffer_size = buffer_size
        self.epochs = epochs
        self.seq_length = seq_length
        self.embedding_dim = embedding_dim
        self.rnn_units = rnn_units


class ResourceProcessor:

    def __init__(self, data_dir='', configuration=Configuration(), text_files=[], markup_files=[]):
        self.data_dir = data_dir
        self.configuration = configuration
        self._text_files = text_files
        self._markup_files = markup_files
        self._temp_text_files = []
        self._temp_markup_files = []

    def download(self, file_references, persist=False):
        for file_ref in file_references:
            if persist:
                file_path = download_file(file_ref.url, file_ref.name)

                if file_ref.type.upper() == 'MARKUP':
                    self._markup_files.append(file_path)
                else:
                    self._text_files.append(file_path)
            else:
                contents = fetch(file_ref.url)

                if file_ref.type.upper() == 'MARKUP':
                    self._temp_markup_files.append(contents)
                else:
                    self._temp_text_files.append(contents)

    def encode(self, persist=False):

        temp_text_file_name = os.path.join(self.data_dir, 'text_files', f'temp_text_{str(datetime.now())}')

        temp_text_file = open(temp_text_file_name, 'w')
        for string in self._temp_text_files:
            temp_text_file.write(string + '\n')

        encoding, decoded_strings = encode(
            f'{str(datetime.now())}',
            self._text_files + [temp_text_file_name],
            self.data_dir,
            persist=persist
        )

        temp_markup_file = open(os.path.join(self.data_dir, f'temp_markup_{str(datetime.now())}'), 'w')
        for string in self._temp_text_files:
            temp_markup_file.write(string + '\n')

        encoding, decoded_strings = encode_markup(
            f'{str(datetime.now())}',
            self._markup_files + [os.path.join(self.data_dir, f'temp_markup_{str(datetime.now())}')],
            self.data_dir,
            persist=persist
        )

    def generate(self):
        sets = []
        training_set = []
        sentence_seeds = []
        for set in range(10):  # training sets
            for i in range(20):  # training set size
                training_file, sentence_seeds = pseudo_random_training_set_from_json(
                    training_objects,
                    5,
                    directory='training_data/5',
                    name=f'{i}'
                )
                training_set.append(training_file)
            sets.append(training_set)
        try:
            base, n = pseudo_random_training_set('training_data/0', 10)
            run_batched_training(sets, sentence_seeds, f'test_data_{n}', base)
        except Exception as e:
            print(str(e))
