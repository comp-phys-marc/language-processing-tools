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
from ..encoder import encode, encode_markup


class EncoderException(BaseException):
    pass


def test_encode_short_text():
    try:
        encode('short_text', ['1.txt'], directory='training_data/0', seperator='\s{2,}', persist=True)
    except Exception as e:
        raise EncoderException(str(e))


@pytest.mark.skip
def test_encode_text():
    try:
        encode('test_text', [f'{i}.txt' for i in range(39)], directory='training_data/0', seperator='\s{2,}', persist=False)
    except Exception as e:
        raise EncoderException(str(e))

@pytest.mark.skip
def test_encode_xml():
    try:
        encode_markup('test_xml', ['found.xml'])
    except Exception as e:
        raise EncoderException(str(e))