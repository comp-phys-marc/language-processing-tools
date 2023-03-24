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
import copy
from ..extractor import extract, MODEL_FUNCTIONS, BadFileException


@pytest.fixture
def text_test_data():
    return [
        open('sample_business_plan.txt', 'r').read(),
        open('file.html', 'r').read()
    ]


@pytest.fixture
def markup_test_data():
    return [
        'file.html'
    ]


@pytest.fixture
def expected_text_results():
    return {'PhoneNumber': [{'value': '780-232-0275', 'score': '0.9'}], 'Email': [{'value': 'fred@spaghettificationtechnology.com'}], 'URL': [{'value': 'https://www.spaghetti.org'}], 'Mention': [], 'Hashtag': [], 'IpAddress': [], 'Age': [], 'Currency': [{'value': '39200000', 'unit': 'Dollar'}, {'value': '2200000000', 'unit': 'Dollar'}, {'value': '2464000000', 'unit': 'Dollar'}, {'value': '1100000000', 'unit': 'Dollar'}, {'value': None, 'unit': 'Dollar'}], 'Temperature': [], 'Dimension': [{'value': '2200000000', 'unit': 'Inch'}, {'value': '10', 'unit': 'Inch'}, {'value': '562000000', 'unit': 'Inch'}], 'Number': [{'value': '780'}, {'value': '232'}, {'value': '275'}, {'value': '3'}, {'value': '4'}, {'value': '5'}, {'value': '6'}, {'value': '7'}, {'value': '14'}, {'value': '17'}, {'value': '18'}, {'value': '19'}, {'value': '20'}, {'value': '23'}, {'value': '24'}, {'value': '2'}, {'value': '5'}, {'value': '39200000'}, {'value': '2200000000'}, {'value': '2025'}, {'value': '24'}, {'value': '2464000000'}, {'value': '2022'}, {'value': '2018'}, {'value': '10'}, {'value': '0.5'}, {'value': '1'}, {'value': '0.333333333333333'}, {'value': '94'}, {'value': '21'}, {'value': '117'}, {'value': '31'}, {'value': '112'}, {'value': '2018'}, {'value': '2018'}, {'value': '1100000000'}, {'value': '4'}, {'value': '15000000'}, {'value': '2015'}, {'value': '2018'}, {'value': '1'}, {'value': '72'}, {'value': '2018'}, {'value': '80000'}, {'value': '3000000'}, {'value': '3'}, {'value': '1'}, {'value': '1'}, {'value': '1'}, {'value': '5'}, {'value': '0.333333333333333'}, {'value': '1'}, {'value': '4'}, {'value': '2'}, {'value': '2'}, {'value': '3'}, {'value': '3'}, {'value': '2'}, {'value': '1'}, {'value': '5'}, {'value': '1'}, {'value': '1'}, {'value': '5'}, {'value': '3'}, {'value': '5'}, {'value': '1'}, {'value': '1'}, {'value': '5'}, {'value': '1'}, {'value': '7000000'}, {'value': '2'}, {'value': '3'}, {'value': '3'}, {'value': '1'}, {'value': '2'}, {'value': '4'}, {'value': '1'}, {'value': '1'}, {'value': '5'}, {'value': '2'}, {'value': '2'}, {'value': '4'}, {'value': '4'}, {'value': '1'}, {'value': '5'}, {'value': '2'}, {'value': '1'}, {'value': '5'}, {'value': '2'}, {'value': '5'}, {'value': '1'}, {'value': '1000'}, {'value': '300'}, {'value': '1'}, {'value': '19'}, {'value': '562000000'}, {'value': '2017'}, {'value': '4'}, {'value': '540000000'}, {'value': '12'}, {'value': '4'}, {'value': '12'}, {'value': '1'}, {'value': '12'}, {'value': '12'}, {'value': '12'}, {'value': '12'}, {'value': '1'}, {'value': '1'}, {'value': '1'}, {'value': '12'}, {'value': '12'}, {'value': '4'}, {'value': '12'}, {'value': '2'}, {'value': '5'}, {'value': '1'}, {'value': '2'}, {'value': '1'}, {'value': '2'}, {'value': '3'}, {'value': '4'}], 'Ordinal': [{'value': '0'}, {'value': '0'}, {'value': '1'}, {'value': '1'}, {'value': '3'}, {'value': '1'}, {'value': '0'}, {'value': '0'}, {'value': '3'}, {'value': '0'}, {'value': '1'}, {'value': '0'}, {'value': '0'}, {'value': '3'}, {'value': '3'}, {'value': '1'}, {'value': '0'}, {'value': '1'}, {'value': '1'}], 'Percent': [{'value': '24%'}], 'DateTime': ['now'], 'Boolean': [{'value': False, 'score': 0.0}], 'market': ['market', 'market', 'market', 'market', 'market'], 'potato': []}


@pytest.fixture
def expected_markup_results():
    return {'PhoneNumber': [], 'Email': [], 'URL': [{'value': 'XML.com'}, {'value': 'www.google-analytics.com/analytics.js'}], 'Mention': [], 'Hashtag': [], 'IpAddress': [], 'Age': [], 'Currency': [], 'Temperature': [{'value': '32676', 'unit': 'F'}, {'value': '484', 'unit': 'F'}], 'Dimension': [{'value': None, 'unit': 'Meter'}], 'Number': [{'value': '1'}, {'value': '0'}, {'value': '1'}, {'value': '-79723435'}, {'value': '1'}, {'value': '21754636678'}, {'value': '-1'}, {'value': '160'}, {'value': '600'}, {'value': '120'}, {'value': '240'}, {'value': '300'}, {'value': '250'}, {'value': '-1550450394815'}, {'value': '0'}, {'value': '21754636678'}, {'value': '-2'}, {'value': '300'}, {'value': '250'}, {'value': '-1550513522284'}, {'value': '0'}, {'value': '0'}, {'value': '0'}, {'value': '-8458'}, {'value': '-1550450394815'}, {'value': '0'}, {'value': '-1475102693815'}, {'value': '0'}, {'value': '21754636678'}, {'value': '-1'}, {'value': '12345'}, {'value': '-1'}, {'value': '160600'}, {'value': '300250'}, {'value': '120400'}, {'value': '300250'}, {'value': '300600'}, {'value': '-1550513522284'}, {'value': '0'}, {'value': '-1475185990716'}, {'value': '0'}, {'value': '21754636678'}, {'value': '-2'}, {'value': '12345'}, {'value': '-1'}, {'value': '300250'}, {'value': '728.9'}, {'value': '2000'}], 'Ordinal': [{'value': '1'}], 'Percent': [], 'DateTime': [], 'Boolean': [], 'market': []}

@pytest.mark.skip
def test_text_extractor_models(text_test_data, expected_text_results):
    i = 0

    for data in text_test_data:
        results = dict()
        matcher = None

        # target values' types
        models = copy.deepcopy(MODEL_FUNCTIONS)

        # features
        models['market'] = 'market'
        models['potato'] = 'potato'

        if i == 0:
            type = 'text'
        else:
            type = 'XML'

        for model in models:
            results[model] = []
            try:
                entities, matcher = extract(model, data, matcher, file_type=type, context='doc')

                for entity in entities:
                    if model == 'DateTime':
                        results[model].append(data[entity.start:entity.end + 1])
                    elif model not in MODEL_FUNCTIONS.keys():
                        results[model] += entity.canonical_values
                    else:
                        results[model].append(entity.resolution)

            # The markup parser accepts filenames rather than file contents
            except OSError as e:
                if (model.upper() == 'MARKUP') and ('File name too long' in str(e)):
                    print(f'Extractor test found expected error: {e}')
                else:
                    raise e

            except BadFileException as e:
                if model.upper() == 'MARKUP':
                    print(f'Extractor test found expected error: {e}')
                else:
                    raise e

        i += 1

        for key in results:
            assert results[key] == expected_text_results[key]


def test_markup_extractor_models(markup_test_data, expected_markup_results):
    i = 0

    for data in markup_test_data:
        results = dict()
        matcher = None

        # target values' types
        models = copy.deepcopy(MODEL_FUNCTIONS)

        # features
        models['market'] = 'market'

        type = 'MARKUP'

        for model in models:
            results[model] = []
            entities, matcher = extract(model, data, matcher, file_type=type)

            for k in entities.keys():
                result = entities[k]
                for entity in result:
                    if model == 'DateTime':
                        results[model].append(data[entity.start:entity.end + 1])
                    elif model not in MODEL_FUNCTIONS.keys():
                        results[model] += entity.canonical_values
                    else:
                        results[model].append(entity.resolution)

        i += 1

        for key in results:
            assert results[key] == expected_markup_results[key]