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
import joblib
import math
import tensorflow_hub as hub
import tensorflow as tf
import pandas as pd
import numpy as np
from functools import reduce
from extractor import extract
from pandas.errors import ParserError


def embed(input):
    module_url = "https://tfhub.dev/google/universal-sentence-encoder/4"
    model = hub.load(module_url)
    return model(input)


def encode_markup(run_name, files, directory='./', persist=False):
    """
    Encodes and optionally persists data in a set of markup files.
    """
    all_data = []

    for i in range(len(files)):
        file = files[i]
        contents, matcher = extract(None, file, matcher=None, file_type='MARKUP', array_wrap=True)
        all_data.append(pd.DataFrame.from_dict(contents))

    input = reduce(lambda table_zero, table_one: pd.concat([table_zero, table_one]), all_data)
    data = list(input.values[0])

    all_encodings = []
    batched_data = []

    i = 0
    for batch in np.array_split(data, 10):
        if len(batch) != 0:
            encoded = tf.nn.l2_normalize(embed(tf.constant(batch.tolist())), axis=1)
            batched_data.append(batch)
            all_encodings.append(encoded)

    if persist:
        joblib.dump(all_encodings, os.path.join(directory, 'saved_encodings', f'encoded_{run_name}.pkl'))
        joblib.dump(batched_data, os.path.join(directory, 'saved_decodings', f'decoded_{run_name}.pkl'))

    return all_encodings, batched_data


def parse_files(all_data, files, seperator, cols=1):

    if seperator == '\n':
        for i in range(len(files)):
            file = files[i]

            content = open(file).read()
            dt = pd.DataFrame(content.split('\n'))

            all_data.append(dt)

    else:
        for i in range(len(files)):
            file = files[i]

            try:
                if cols == 1:
                    dt = pd.read_csv(
                        file,
                        sep=seperator,
                        header=None  # header could be provided to the function
                    )
                    all_data.append(dt)
                else:
                    dt = pd.read_csv(
                        file,
                        sep=seperator,
                        header=None,
                        usecols=range(cols)
                    )
                    all_data.append(dt)

            except ParserError as e:
                if 'fields in line' in str(e):
                    all_data = parse_files(all_data, files[i:], seperator, cols + 1)

    return all_data


def encode(run_name, files, directory='', seperator='\n', persist=False):
    """
    Encodes and optionally persists data in a set of files.
    """
    all_data = parse_files([], files, seperator)

    input = reduce(lambda table_zero, table_one: pd.concat([table_zero, table_one]), all_data)
    data = list(input[0])

    all_encodings = []
    batched_data = []

    i = 0
    for batch in np.array_split(data, 10):
        if len(batch) != 0:
            encoded = tf.nn.l2_normalize(embed(tf.constant(batch.tolist())), axis=1)
            batched_data.append(batch)
            all_encodings.append(encoded)

    if persist:
        joblib.dump(all_encodings, os.path.join(directory, 'saved_encodings', f'encoded_{run_name}.pkl'))
        joblib.dump(batched_data, os.path.join(directory, 'saved_decodings', f'decoded_{run_name}.pkl'))

    return all_encodings, batched_data


def encode_pair(batch, run_name, directory=".", persist=False):
    """
    Encodes and optionally persists a pair of strings.
    """
    encode1 = tf.nn.l2_normalize(embed(tf.constant(batch['sent_1'].tolist())), axis=1)
    encode2 = tf.nn.l2_normalize(embed(tf.constant(batch['sent_2'].tolist())), axis=1)

    if persist:
        joblib.dump(encode1, os.path.join(directory, 'saved_encodings', f'encoded_{run_name}_1.pkl'))
        joblib.dump(encode2, os.path.join(directory, 'saved_encodings', f'encoded_{run_name}_2.pkl'))

    return [encode1, encode2]


def compare(first_encoded, second_encoded):
    """
    Compares encoded sentences. Should be provided either with the encodings directly,
    or with the names of the files to load.
    """

    if isinstance(first_encoded, str):
        first_encoded = joblib.load(first_encoded)

    if isinstance(second_encoded, str):
        first_encoded = joblib.load(second_encoded)

    cosine_similarities = tf.reduce_sum(tf.multiply(first_encoded, second_encoded), axis=1)
    clip_cosine_similarities = tf.clip_by_value(cosine_similarities, -1.0, 1.0)
    scores = 1.0 - tf.acos(clip_cosine_similarities) / math.pi

    return scores
