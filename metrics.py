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

from io import StringIO
from extractor import extract


def parse_resolved_values(values):
    results = ''
    results = parse_resolved_values_helper(values, results)

    return results


def parse_resolved_values_helper(values, results):
    for i in range(len(values)):
        obj = values[i]
        if isinstance(obj, list):
            results += parse_resolved_values_helper(values[i], results)
        elif hasattr(obj, 'resolution'):
            results += ' ' + obj.resolution['value']

    return results


class IncompatibleException(Exception):
    pass


class Metric:
    """
    Metrics allow a user to specify those attributes of a dataset that are meaningful to them.
    """

    def __init__(self, features: list, feature_types: list, values: list = None, proximity: int = 1):
        """
        Features are the attributes that are interesting,
        values are the values we would like them the attributes to take,
        features and values are related by proximity within a source text.
        """

        self.proximity = proximity
        self.features = features
        self.feature_types = feature_types
        if values is not None and len(values) == len(features):
            self.values = values
        else:
            self.values = [0 for i in range(len(features))]

    def __eq__(self, other):
        """
        This allows us to check whether an idealized metric
        is equal to a given measurement.
        """
        return self.features == other.features \
               and self.values == other.values \
               and self.feature_types == other.feature_types

    def difference(self, other):
        """
        The difference between two metrics in terms of matched
        and mismatched values.
        """

        if self.features != other.features:
            raise IncompatibleException("Trying to compare two incompatible metrics.")

        similarity = 0

        for i in range(len(self.values)):
            if self.values[i] == other.values[i] and self.feature_types[i] == other.feature_types[i]:
                similarity += 1

        return len(self.features) - similarity

    def export(self):
        result = '<xml>\n'
        for i in range(len(self.features)):
            values = self.values[i]
            if isinstance(values, list):
                for value in values:
                    if self.features[i] == 'any':
                        feature = self.feature_types[i]
                    else:
                        feature = self.features[i]
                    result += f'<{feature}>{value}</{feature}>\n'
        result += '</xml>'

        return result

    def populate_from_source(self, source: str, file_type="text", context=None):
        """
        Populates the values from a source.
        """

        stream = StringIO(source)

        i = 0
        for feature in self.features:

            if feature == 'any':
                feature = None

            lines = []
            j = 0

            for line in stream:
                j += 1

                if line == '\n':
                    continue

                line = line.replace('\n', ' ')
                line = line.replace('\u2003', ' ')
                lines.append(line)

                # if it is markup, we use tags to reference specific values instead of proximity within text
                if j > self.proximity or file_type == 'XML' or file_type == 'HTML':
                    found, matcher = extract(feature, ' '.join(lines), None, file_type, context)

                    if found:

                        feature_type = self.feature_types[i]
                        if feature_type == 'any':
                            feature_type = None

                        values, matcher = extract(feature_type, ' '.join(lines), matcher, file_type, context)

                        if values and (file_type == 'XML' or file_type == 'HTML'):
                            self.values[i] = [parse_resolved_values(value) for value in values.values()]
                        elif values:
                            self.values[i] = [value.resolution for value in values]

                    lines = lines[1:]

            i += 1