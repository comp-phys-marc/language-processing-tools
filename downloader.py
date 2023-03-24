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
import requests


def download_file(url, filename, data_dir='.'):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(os.path.join(data_dir, filename), 'wb') as f:
            for i, chunk in enumerate(r.iter_content(chunk_size=1024*1024)):
                f.write(chunk)
                if i % 10 == 0:
                    print(f'Downloaded {i} megabytes', end='\r')

    return os.path.join(data_dir, filename)


def fetch(url):
    res = ''
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        for i, chunk in enumerate(r.iter_content(chunk_size=1024*1024)):
            res += chunk.decode('utf-8')
            if i % 10 == 0:
                print(f'Downloaded {i} megabytes', end='\r')

    return res
