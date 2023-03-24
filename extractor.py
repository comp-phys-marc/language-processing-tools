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

# This entity extractor will be used to present the user with options for specific data.
# This data an then be used again, if the user so chooses, in the generation of text.

# If a metric is defined over a feature set, and the feature space of that set can be populated
# by the entities extracted here, then these can be used to evaluate how an feature space changes over
# time.

# We use Microsoft's Recognizers-Text library since it is a free and open source component which
# we would otherwise have to develop.

import importlib
from lxml import etree

from recognizers_text import Culture
from recognizers_text.matcher.string_matcher import StringMatcher
from recognizers_sequence.sequence.sequence_recognizer import recognize_phone_number, recognize_email, recognize_url, \
    recognize_hashtag, recognize_mention, recognize_ip_address
from recognizers_number_with_unit.number_with_unit.number_with_unit_recognizer import recognize_age, \
    recognize_currency, recognize_dimension, recognize_temperature
from recognizers_number.number.number_recognizer import recognize_number, recognize_ordinal, recognize_percentage
from recognizers_date_time import recognize_datetime
from recognizers_choice import recognize_boolean


def _handle_xml_parse_errors(parser):
    while True:
        try:
            yield next(parser)
        except StopIteration:
            return
        except etree.XMLSyntaxError as e:
            print(f'Skipping line because of syntax error: {e}')


def _recognize_xml(model, source, context, tag_indexed=False, array_wrap=False):
    results = {}

    for _, element in _handle_xml_parse_errors(etree.iterparse(source, events=('end',), tag=context)):
        if hasattr(element, 'text') and element.text is not None:
            result = model(element.text, Culture.English)
            element.clear()

            if result is not None and result != []:
                if tag_indexed and hasattr(element, 'tag'):
                    if not array_wrap:
                        results[element.tag] = result
                    else:
                        results[element.tag] = [result]
                else:
                    if not array_wrap:
                        results[len(results.keys())] = result
                    else:
                        results[len(results.keys())] = [result]

    return results


MODEL_FUNCTIONS = {
    'PhoneNumber': recognize_phone_number,  # the extractor can target this kind of data...
    'Email': recognize_email,
    'URL': recognize_url,
    'Mention': recognize_mention,
    'Hashtag': recognize_hashtag,
    'IpAddress': recognize_ip_address,
    'Age': recognize_age,
    'Currency': recognize_currency,
    'Temperature': recognize_temperature,
    'Dimension': recognize_dimension,
    'Number': recognize_number,
    'Ordinal': recognize_ordinal,
    'Percent': recognize_percentage,
    'DateTime': recognize_datetime,
    'Boolean': recognize_boolean
}


class BadFileException(BaseException):
    pass


def _get_class(module_name, class_name):
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        return None
    return getattr(module, class_name) if hasattr(module, class_name) else None


def _create_extractor(language, model):
    """
    This function determines what datetime extractor to load from the library.
    """
    extractor = _get_class(
        'recognizers_date_time',
        f'{language}{model}Extractor')

    if extractor:
        return extractor()

    extractor = _get_class(
        f'recognizers_date_time.date_time.{language.lower()}.{model.lower()}',
        f'{language}{model}Extractor')

    if extractor:
        return extractor()

    extractor = _get_class(
        f'recognizers_date_time.date_time.base_{model.lower()}',
        f'Base{model}Extractor')
    configuration = _get_class(
        f'recognizers_date_time.date_time.{language.lower()}.{model.lower()}_extractor_config',
        f'{language}{model}ExtractorConfiguration')

    return extractor(configuration())


def extract(model, source, matcher=None, file_type='text', context=None, array_wrap=False):
    """
    This function uses the entity extractor provided by Microsoft's Recognizers-Text open source
    library that corresponds to the given model name to extract entities from the provided source
    text.
    """
    if model == 'DateTime':
        language = 'English'
        extractor = _create_extractor(language, model)
        if file_type.upper() == 'MARKUP':
            result = _recognize_xml(extractor.extract, source, context, array_wrap)
        else:
            result = extractor.extract(source)
    elif model in MODEL_FUNCTIONS.keys():
        if file_type.upper() == 'MARKUP':
            result = _recognize_xml(MODEL_FUNCTIONS[model], source, context, array_wrap)
        else:
            result = MODEL_FUNCTIONS[model](source, Culture.English)
    elif model is not None:
        if not matcher:
            matcher = StringMatcher()
            matcher.init(source.split(' '))
        if file_type.upper() == 'MARKUP':
            def find_string(string, language):  # matcher.find does not take a language like the rest
                return matcher.find(string)
            result = _recognize_xml(find_string, source, context, array_wrap)
        else:
            result = matcher.find(model)
    elif model == 'tag':
        if file_type.upper() == 'MARKUP':
            def pass_through(text):
                return text
            result = _recognize_xml(pass_through, source, None, tag_indexed=True, array_wrap=array_wrap)
        else:
            result = source
    else:
        if file_type.upper() == 'MARKUP':
            def pass_through(text, language):
                return text
            result = _recognize_xml(pass_through, source, None, tag_indexed=False, array_wrap=array_wrap)
        else:
            result = source

    return result, matcher