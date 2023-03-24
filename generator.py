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
import time
from random import randint
import tensorflow as tf
from tensorflow.keras.layers.experimental import preprocessing


class ModelNotFoundException(BaseException):
    pass


def run_generation(model, sentence_seeds, chars_from_ids, ids_from_chars):
    results = []

    for i in range(len(sentence_seeds)):
        sentence_seed = sentence_seeds[i]
        text = generate(model, chars_from_ids, ids_from_chars, sentence_seed, loops=50, one_step_model='test')

        results.append(text)

    return results


def run_batched_training(batched_data, sentence_seeds, file_set_name, training_set_base):
    model = None
    ids_from_chars = None
    chars_from_ids = None

    for i in range(len(batched_data)):
        file_set = batched_data[i]

        model, ids_from_chars, chars_from_ids = \
            train_model(file_set + training_set_base, f'{file_set_name}_{i}', persist=True, model=model)

    results = run_generation(model, sentence_seeds, chars_from_ids, ids_from_chars)

    return results


def pseudo_random_training_set_from_json(objects, size, directory='training_data/0', name='0', randomize=False):
    """
    Builds a set of training questions from a set of subjects
    and generic questions.
    """
    subjects = []
    questions = []
    seeds = []

    for object in objects:
        subject = object['question']['question_concept']
        question = object['question']['stem']
        subjects.append(subject)
        questions.append(question)

    results = []

    while len(results) < size:
        q = questions[randint(0, len(questions))]
        results.append(q)
        seeds.append(q[0:len(question) // 2])

    file = open(os.path.join(directory, f'{name}.txt'), 'w')
    file.write(str('  '.join(results)))

    return os.path.join(directory, f'{name}.txt'), seeds


def pseudo_random_training_set(directory, sample_delta):
    """
    Builds a training set from pseudo-randomly chosen text
    files from the provided directory.
    """

    # get the number of files in the provided directory
    num_files = len(next(os.walk(directory))[2])

    # choose a random file to train on
    m = randint(0, num_files)
    n = m

    training_set = [f'{directory}/{m}.txt']

    # add files to create a full, unique training set
    while m > sample_delta:
        m = m - sample_delta
        training_set.append(f'{directory}/{m}.txt')

    return training_set, n


def _text_to_ids(training_data_files):
    raw_data_ds = tf.data.TextLineDataset(training_data_files)

    text = ''
    for elem in raw_data_ds:
        text = text + (elem.numpy().decode('utf-8'))

    # length of text is the number of characters in it
    print(f'Length of text: {len(text)} characters')

    # The unique characters in the file
    vocab = sorted(set(text))
    print(f'{len(vocab)} unique characters')

    example_texts = [''.join(vocab)]
    chars = tf.strings.unicode_split(example_texts, input_encoding='UTF-8')
    ids_from_chars = preprocessing.StringLookup(vocabulary=list(vocab), mask_token=None)
    ids = ids_from_chars(chars)

    return ids, ids_from_chars


def text_from_ids(ids, chars_from_ids):
    return tf.strings.reduce_join(chars_from_ids(ids), axis=-1)


def _text_from_ids(ids, ids_from_chars):
    chars_from_ids = tf.keras.layers.experimental.preprocessing.StringLookup(
        vocabulary=ids_from_chars.get_vocabulary(), invert=True, mask_token=None)
    chars = chars_from_ids(ids)
    tf.strings.reduce_join(chars, axis=-1).numpy()
    text = tf.strings.reduce_join(chars_from_ids(ids), axis=-1)

    return text, chars_from_ids


def split_input_target(sequence):
    input_text = sequence[:-1]
    target_text = sequence[1:]
    return input_text, target_text


def create_training_batches(training_data_files, configuration):
    ids, ids_from_chars = _text_to_ids(training_data_files)
    text, chars_from_ids = _text_from_ids(ids, ids_from_chars)

    input = ""

    for file in training_data_files:
        input += open(file).read() + "\n"

    all_ids = ids_from_chars(tf.strings.unicode_split(input, 'UTF-8'))
    ids_dataset = tf.data.Dataset.from_tensor_slices(all_ids)
    sequences = ids_dataset.batch(configuration.seq_length + 1, drop_remainder=True)

    dataset = sequences.map(split_input_target)

    return dataset, ids, ids_from_chars, chars_from_ids


class MyModel(tf.keras.Model):
    def __init__(self, vocab_size, embedding_dim, rnn_units):
        super().__init__(self)
        self.embedding = tf.keras.layers.Embedding(vocab_size, embedding_dim)
        self.gru = tf.keras.layers.GRU(rnn_units,
                                       return_sequences=True,
                                       return_state=True)
        self.dense = tf.keras.layers.Dense(vocab_size)

    def call(self, inputs, states=None, return_state=False, training=False):
        x = inputs
        x = self.embedding(x, training=training)
        if states is None:
          states = self.gru.get_initial_state(x)
        x, states = self.gru(x, initial_state=states, training=training)
        x = self.dense(x, training=training)

        if return_state:
          return x, states
        else:
          return x


class OneStep(tf.keras.Model):
    def __init__(self, model, chars_from_ids, ids_from_chars, temperature=1.0):
        super().__init__()
        self.temperature = temperature
        self.model = model
        self.chars_from_ids = chars_from_ids
        self.ids_from_chars = ids_from_chars

    @tf.function
    def generate_one_step(self, inputs, states=None):
        input_chars = tf.strings.unicode_split(inputs, 'UTF-8')
        input_ids = self.ids_from_chars(input_chars).to_tensor()

        predicted_logits, states = self.model(inputs=input_ids, states=states,
                                              return_state=True)
        predicted_logits = predicted_logits[:, -1, :]
        predicted_logits = predicted_logits/self.temperature
        predicted_logits = predicted_logits

        predicted_ids = tf.random.categorical(predicted_logits, num_samples=1)
        predicted_ids = tf.squeeze(predicted_ids, axis=-1)

        predicted_chars = self.chars_from_ids(predicted_ids)

        return predicted_chars, states


def _create_model(training_data_files, model, configuration):
    dataset, ids, ids_from_chars, chars_from_ids = create_training_batches(training_data_files)

    if model is None:
        model = MyModel(
            vocab_size=len(ids_from_chars.get_vocabulary()),
            embedding_dim=configuration.embedding_dim,
            rnn_units=configuration.rnn_units)

    return model, dataset, ids_from_chars, chars_from_ids


def train_model(training_data_files, name, configuration, persist=False, model=None):
    loss = tf.losses.SparseCategoricalCrossentropy(from_logits=True)

    model, dataset, ids_from_chars, chars_from_ids = _create_model(training_data_files, model)

    model.compile(optimizer='adam', loss=loss)

    checkpoint_dir = './training_checkpoints'
    checkpoint_prefix = os.path.join(checkpoint_dir, "ckpt_{epoch}")

    checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
        filepath=checkpoint_prefix,
        save_weights_only=True)

    model.fit(dataset, epochs=configuration.epochs, callbacks=[checkpoint_callback])

    model.summary()

    if persist:
        tf.saved_model.save(model, f'saved_models/{name}')

    return model, ids_from_chars, chars_from_ids


def generate(model, chars_from_ids, ids_from_chars, initial_string, loops=50, one_step_model=None):
    """
    Generates text using a OneStep model. If a model is given by name, the method checks if the
    model has been saved. If it exists, the model is loaded and used. If a name is given but
    the model does not yet exist, it is created and saved. If no name is given, a new model is created
    but not saved.
    """
    if one_step_model is None:
        one_step_model = OneStep(model, chars_from_ids, ids_from_chars)
    else:
        try:
            one_step_model = get_saved_model(one_step_model)
        except ModelNotFoundException as e:
            one_step_model = OneStep(model, chars_from_ids, ids_from_chars)

    start = time.time()
    states = None
    next_char = [initial_string]
    result = [next_char]

    for n in range(loops):
        next_char, states = one_step_model.generate_one_step(next_char, states=states)
        result.append(next_char)

    result = tf.strings.join(result)
    end = time.time()
    print(result[0].numpy().decode('utf-8'), '\n\n' + '_' * 80)
    print('\nRun time:', end - start)

    if isinstance(one_step_model, str):
        tf.saved_model.save(one_step_model, f'saved_models/one_step_{one_step_model}')

    return result


def get_saved_model(name):
    try:
        model_reloaded = tf.saved_model.load(f'saved_models/{name}')
        return model_reloaded
    except OSError as e:
        raise ModelNotFoundException(str(e))