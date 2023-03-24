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

import json
import pytest
import tensorflow as tf
from ..generator import _text_to_ids, _text_from_ids, create_training_batches, \
    pseudo_random_training_set, pseudo_random_training_set_from_json, get_saved_model, \
    run_batched_training


BOUND = 0.9


@pytest.fixture
def training_set():
    return ['the_count_of_monte_cristo.txt']


@pytest.fixture
def training_objects():
    return json.load(open('training_data/train_rand_split.json', 'r'))


@pytest.fixture
def expected_ids():
    return tf.ragged.constant([[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85]], dtype='int64')


@pytest.fixture
def expected_text():
    return tf.constant([b'\t !"$%&\'(),-./0123456789:;=?@ABCDEFGHIJKLMNOPQRSTUVWXYabcdefghijklmnopqrstuvwxyz\xe2\x80\x83\xe2\x80\x99\xe2\x80\x9c\xe2\x80\x9d\xe2\x80\xa2'], dtype='string')


def test_generate(training_objects):
    """
    Performs a full training and usage of a new NLP model.
    """
    sets = []
    training_set = []
    sentence_seeds = []
    for set in range(10):  # training sets
        for i in range(20):  # training set size
            training_file, sentence_seeds = pseudo_random_training_set_from_json(training_objects, 5, directory='training_data/5', name=f'{i}')
            training_set.append(training_file)
        sets.append(training_set)
    try:
        base, n = pseudo_random_training_set('training_data/0', 10)
        run_batched_training(sets, sentence_seeds, f'test_data_{n}', base)
    except Exception as e:
        print(str(e))


@pytest.mark.skip
def test_training_data_preparation(training_set, expected_ids, expected_text):
    """
    This test walks through each of the function calls involved in
    preparing data for the model, intercepting the returns at each
    step and verifying that they match the results from a successful
    run.
    """
    ids, ids_from_chars = _text_to_ids([training_set[0]])
    assert tf.equal(ids, expected_ids).numpy().all()

    text, chars_from_ids = _text_from_ids(ids, ids_from_chars)
    assert tf.equal(text, expected_text).numpy().all()

    dataset, batches_ids, same_ids_from_chars, same_chars_from_ids = create_training_batches([training_set[0]])
    assert tf.equal(ids, batches_ids).numpy().all()


@pytest.mark.skip
def test_saved_model(sentence_seeds):
    """
    This tests tries to generate some sentences using a saved model.
    """
    one_step_model = get_saved_model('one_step_test')

    for initial_string in sentence_seeds:
        states = None
        next_char = [initial_string]
        result = [next_char]

        for n in range(100):
            next_char, states = one_step_model.generate_one_step(next_char, states=states)
            result.append(next_char)

        result = tf.strings.join(result)
        print(result)
