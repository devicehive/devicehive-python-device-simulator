# Copyright (C) 2018 DataArt
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================


import json
import threading
from collections import OrderedDict

import re
from configargparse import ConfigFileParserException, ConfigFileParser


__all__ = ['AtomicCounter', 'JSONConfigFileParser', 'Template']


class AtomicCounter(object):
    def __init__(self, initial=0):
        self._value = initial
        self._lock = threading.Lock()

    @property
    def value(self):
        with self._lock:
            return self._value

    def increment(self, num=1):
        with self._lock:
            self._value += num
            return self._value


class JSONConfigFileParser(ConfigFileParser):

    def get_syntax_description(self):
        msg = 'The config file uses JSON syntax. (for details, see ' \
              'https://www.json.org/).'
        return msg

    def parse(self, stream):
        try:
            parsed_obj = json.load(stream)
        except Exception as e:
            raise ConfigFileParserException(
                "Couldn't parse config file: %s" % e)

        result = OrderedDict()
        for key, value in parsed_obj.items():
            if isinstance(value, list):
                result[key] = value
            elif isinstance(value, dict):
                result[key] = json.dumps(value)
            else:
                result[key] = str(value)

        return result

    def serialize(self, items):
        items = dict(items)
        return json.dumps(items)


class Template(object):
    pattern = re.compile(r'"\$(?P<named>[_a-z][_a-z0-9]*)"', re.VERBOSE)

    def __init__(self, template):
        self._template = template

    def render(self, **mapping):
        def convert(mo):
            named = mo.group('named')
            if named is not None and named in mapping:
                value = mapping[named]
                if callable(value):
                    value = value()

                return str(value)

            return mo.group()
        return self.pattern.sub(convert, self._template)
