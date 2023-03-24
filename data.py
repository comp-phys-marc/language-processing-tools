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

import pinecone
import joblib


class NoIndexException(BaseException):
    pass


class AuthenticationException(BaseException):
    pass


class Store:

    def __init__(self, api_key, index_name=None):
        self.index_name = index_name
        self.index = None
        self.decoded = {}
        self.init_index(api_key, index_name)

    def init_index(self, api_key, index_name=None):
        pinecone.init(api_key)

        try:
            indexes = pinecone.list_indexes()
            print(f'\x1b[34m Successfully authenticated. Your api key grants access to indexes {indexes}. \x1b[37m')
        except Exception as e:
            raise AuthenticationException(str(e))

        if index_name is not None:
            if index_name in indexes:
                index = pinecone.Index(index_name)
            else:
                pinecone.create_index(index_name)
                index = pinecone.Index(index_name)

            self.index = index
            return index

    def insert(self, batches):
        max_id = 0
        if self.index:
            for batch in batches:
                ids = [i + max_id for i in range(len(batch))]
                max_id = max_id + len(ids)
                self.index.upsert(items=zip(ids, batch))
        else:
            raise NoIndexException

    def drop_index(self):
        if self.index:
            return pinecone.delete_index(self.index_name)

    def list_indexes(self):
        return pinecone.list_indexes()

    def try_query(self, value, count, attempts, retries, results):
        try:
            results.append(self.index.query(value, count))
        except ConnectionError as e:
            print(f'Connection error {attempts} of {retries}.')
            if attempts < retries:
                results.append(self.try_query(value, count, attempts + 1, retries, results))
            else:
                raise ConnectionError(f'Failed all {retries} connection attempts. Check your internet connection.')

        return results

    def query(self, encoded, count, persisted=True, retries=3):
        results = []
        if persisted:
            encoded = joblib.load(f'saved_encodings/encoded_{encoded}.pkl')
        for value in encoded:
            attempts = 0
            results = self.try_query(value.numpy(), count, attempts, retries, results)

        return results