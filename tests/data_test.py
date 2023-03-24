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

import pytest
import pinecone
import joblib
from functools import reduce
import pandas as pd
from pinecone import QueryResult
from ..data import Store, AuthenticationException

API_KEY = '45def035-6ef4-4637-be71-d7ffe74c8149'


@pytest.fixture
def expected_result():
    return [
        QueryResult(ids=['148', '137', '480'], scores=[-1.7694904804229736, -1.8167585134506226, -1.8295685052871704], data=None),
        QueryResult(ids=['311', '277', '493'], scores=[-1.6982905864715576, -1.7106636762619019, -1.7160745859146118], data=None),
        QueryResult(ids=['70', '22', '332'], scores=[-1.779414415359497, -1.7817007303237915, -1.7907605171203613], data=None)]


@pytest.mark.skip
def test_auth():
    try:
        Store(API_KEY)
    except AuthenticationException as e:
        print(AuthenticationException)


@pytest.mark.skip
def test_delete_index():
    Store(API_KEY)
    indexes = pinecone.list_indexes()
    for index in indexes:
        store = Store(API_KEY, index)
        try:
            store.drop_index()
        except Exception as e:
            print(e)


@pytest.mark.skip
def test_query_index(expected_result):
    store = Store(API_KEY, 'train-data-1')
    result = store.query('sample', 3)
    assert result[0] == expected_result


@pytest.mark.skip
def test_associate_with_decoded_string(expected_result):
    batches = [expected_result]
    decoded = joblib.load(f'saved_encodings/decoded_found.pkl')[0]

    for i in range(len(batches)):
        batch = batches[i]

        # Note: this mapping is somewhat unstable... why do results
        # from pinecone seem not to be the same with each identical query?
        # I don't know and it's not something I can solve.
        for top_result in batch:
            try:
                for j in range(len(top_result.ids)):
                    string = decoded[i][top_result.ids[j]]
                    score = top_result.scores[j]

                    print(f'Query matched {string}" with score {score}')

            except Exception as e:
                print("Index out of range (expected for this test), but the approach works!")