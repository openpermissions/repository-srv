# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

from __future__ import unicode_literals

import os
import pytest

from repository.models.framework import helper





FIXTURE_DIR = os.path.join(os.path.dirname(__file__), '../../..', 'data')
valid_examples = [(os.path.abspath(os.path.join(FIXTURE_DIR, 'sample.xml')), 'xml'),
                  (os.path.abspath(os.path.join(FIXTURE_DIR, 'sample.xml')), None),
                  (os.path.abspath(os.path.join(FIXTURE_DIR, 'sample.ttl')), 'turtle')]

invalid_examples = [(os.path.abspath(os.path.join(FIXTURE_DIR, 'invalid_data.txt')), None),
                    (os.path.abspath(os.path.join(FIXTURE_DIR, 'badly_formed_xml.xml')), 'xml'),
                    (os.path.abspath(os.path.join(FIXTURE_DIR, 'badly_formed_ttl.ttl')), 'turtle'),
                    (os.path.abspath(os.path.join(FIXTURE_DIR, 'sample.xml')), 'turtle'),
                    (os.path.abspath(os.path.join(FIXTURE_DIR, 'sample.ttl')), 'xml')]


@pytest.mark.parametrize('file_path, format', valid_examples)
def test_validate(file_path, format):
    with open(file_path, 'r') as f:
        data = f.read()
    helper.validate(data, format=format)


@pytest.mark.parametrize('file_path, format', invalid_examples)
def test_validate_error(file_path, format):
    with open(file_path, 'r') as f:
        data = f.read()

    with pytest.raises(helper.ValidationException) as exc:
        helper.validate(data, format=format)
    assert exc.value.args[0].startswith("error while parsing data")


def test_validate_with_no_request_body_data():
    data = None
    with pytest.raises(helper.ValidationException) as exc:
        helper.validate(data)
    assert exc.value.args[0].startswith("error while parsing data")
