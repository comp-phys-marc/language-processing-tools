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
from ..metrics import Metric


@pytest.fixture
def test_data():
    return [open('sample_business_plan.txt', 'r').read()]  # TODO: add xml and html examples


@pytest.fixture
def markup_data():
    return ['file.html']


@pytest.fixture
def expected_result():
    return Metric(
        features=['market'],
        feature_types=['Currency'],
        values=[[{'value': '39200000', 'unit': 'Dollar'},
                 {'value': '2200000000', 'unit': 'Dollar'},
                 {'value': '2464000000', 'unit': 'Dollar'}
                ]])


@pytest.fixture
def expected_markup_exports():
    return ['<xml>\n<URL> XML.com</URL>\n<URL> www.google-analytics.com/analytics.js</URL>\n</xml>']


@pytest.fixture
def expected_scoped_exports():
    return ['<xml>\n<URL> www.google-analytics.com/analytics.js</URL>\n</xml>']


def test_generic_url_metric(markup_data, expected_markup_exports):
    results = []

    for data in markup_data:
        metric = Metric(['URL'], ['URL'])
        metric.populate_from_source(data, 'XML')
        results.append(metric.export())

    for i in range(len(results)):
        assert results[i] == expected_markup_exports[i]


def test_context_scoped_url_metric(markup_data, expected_scoped_exports):
    results = []
    context = 'script'  # search within JS
    for data in markup_data:
        metric = Metric(['any'], ['URL'])
        metric.populate_from_source(data, 'XML', context)
        results.append(metric.export())

    for i in range(len(results)):
        assert results[i] == expected_scoped_exports[i]


def test_populate_metric(test_data, expected_result):
    for data in test_data:
        metric = Metric(features=['market'], feature_types=['Currency'])
        metric.populate_from_source(data)

        assert metric.difference(expected_result) == 0
