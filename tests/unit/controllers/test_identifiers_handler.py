# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

import pytest
from mock import MagicMock, patch

from koi.test_helpers import make_future
from koi.exceptions import HTTPError
from datetime import datetime

from repository.controllers.assets_handler import IdentifiersHandler


class PartialMockedHandler(IdentifiersHandler):
    def __init__(self):
        super(PartialMockedHandler, self).__init__(application=MagicMock(), request=MagicMock())
        self.finish = MagicMock()
        self.client_organisation = 'foo'


@pytest.mark.parametrize('param_name, param_value', [('from', 0), ('to', 1)])
def test__get_time_arguments_valid_time(param_name, param_value):
    handler = PartialMockedHandler()
    handler.request.arguments = {param_name: ['2015-01-01T00:00:00']}
    result = handler._get_time_arguments()
    assert result[param_value] == datetime(2015, 1, 1, 0, 0)


@pytest.mark.parametrize('param_name', ['from', 'to'])
def test__get_time_arguments_invalid_time(param_name):
    handler = PartialMockedHandler()
    handler.request.arguments = {param_name: ['foobar']}
    with pytest.raises(HTTPError) as exc:
        handler._get_time_arguments()

    assert exc.value.status_code == 400
    assert exc.value.errors == 'Invalid format'


@pytest.mark.parametrize('param_name', ['from', 'to'])
def test__get_time_arguments_time_out_of_range(param_name):
    handler = PartialMockedHandler()
    handler.request.arguments = {param_name: ['100000000000000']}
    with pytest.raises(HTTPError) as exc:
        handler._get_time_arguments()

    assert exc.value.status_code == 400
    assert exc.value.errors == 'Date out of range'


def test__get_time_arguments_no_time():
    handler = PartialMockedHandler()
    result = handler._get_time_arguments()
    assert isinstance(result[0], datetime)
    assert isinstance(result[1], datetime)


@patch('repository.controllers.assets_handler.options')
def test__get_page_arguments_valid_page(options):
    options.max_page_size = 1000
    handler = PartialMockedHandler()
    handler.request.arguments = {'page': ['10']}

    result = handler._get_page_arguments()
    assert result[0] == 10


@patch('repository.controllers.assets_handler.options')
def test__get_page_arguments_invalid_page(options):
    options.max_page_size = 1000
    handler = PartialMockedHandler()
    handler.request.arguments = {'page': ['foo']}

    with pytest.raises(HTTPError) as exc:
        handler._get_page_arguments()
    assert exc.value.status_code == 400
    assert exc.value.errors == 'Invalid page'


@patch('repository.controllers.assets_handler.options')
def test__get_page_arguments_page_out_of_range(options):
    options.max_page_size = 1000
    handler = PartialMockedHandler()
    handler.request.arguments = {'page': ['0']}

    with pytest.raises(HTTPError) as exc:
        handler._get_page_arguments()
    assert exc.value.status_code == 400
    assert exc.value.errors == 'page must be >= 1'


@patch('repository.controllers.assets_handler.options')
def test__get_page_arguments_no_page(options):
    options.max_page_size = 1000
    handler = PartialMockedHandler()

    result = handler._get_page_arguments()
    assert result[0] == 1


@patch('repository.controllers.assets_handler.options')
def test__get_page_arguments_valid_page_size(options):
    options.max_page_size = 1000
    handler = PartialMockedHandler()
    handler.request.arguments = {'page_size': ['10']}

    result = handler._get_page_arguments()
    assert result[1] == 10


@patch('repository.controllers.assets_handler.options')
def test__get_page_arguments_invalid_page_size(options):
    options.max_page_size = 1000
    handler = PartialMockedHandler()
    handler.request.arguments = {'page_size': ['foo']}

    with pytest.raises(HTTPError) as exc:
        handler._get_page_arguments()
    assert exc.value.status_code == 400
    assert exc.value.errors == 'Invalid page_size'


@pytest.mark.parametrize('param_value', ['-1', '1001'])
@patch('repository.controllers.assets_handler.options')
def test__get_page_arguments_page_size_out_of_range(options, param_value):
    options.max_page_size = 1000
    handler = PartialMockedHandler()
    handler.request.arguments = {'page_size': [param_value]}

    with pytest.raises(HTTPError) as exc:
        handler._get_page_arguments()
    assert exc.value.status_code == 400
    assert exc.value.errors == 'page_size must be between 0 and 1000'


@patch('repository.controllers.assets_handler.options')
def test__get_page_arguments_no_page_size(options):
    options.max_page_size = 1000
    handler = PartialMockedHandler()

    result = handler._get_page_arguments()
    assert result[1] == 1000


@patch('repository.models.framework.db._namespace_url')
@patch('repository.controllers.assets_handler.options')
@patch('repository.models.asset')
def test_handler_get(assets, options, url):
    options.service_id = 'service_id'
    repository_id = 'c8ab01'
    assets.retrieve_paged_ids.return_value = make_future(
        (['id1'], (datetime(2015, 01, 01, 0, 0, 0), datetime(2015, 01, 02, 0, 0, 0))))
    url.return_value = yield make_future('https://localhost:8000/bigdata/namespace/c8ab01')

    handler = PartialMockedHandler()
    handler.get(repository_id).result()

    assert handler.finish.called
    assert handler.finish.call_args[0][0].keys() == ['status', 'data', 'metadata']


@patch('repository.models.framework.db._namespace_url')
@patch('repository.controllers.assets_handler.options')
@patch('repository.models.asset')
def test_handler_get_no_result(assets, options, url):
    options.service_id = 'service_id'
    assets.retrieve_paged_ids.return_value = make_future(([], ()))
    url.return_value = yield make_future('https://localhost:8000/bigdata/namespace/c8ab01')
    repository_id = 'c8ab01'

    handler = PartialMockedHandler()
    handler.get(repository_id).result()

    assert handler.finish.called
    assert handler.finish.call_args[0][0].keys() == ['status', 'data', 'metadata']
