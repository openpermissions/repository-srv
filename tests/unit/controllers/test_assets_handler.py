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

from koi import exceptions
from koi.test_helpers import gen_test, make_future

from repository.controllers.assets_handler import _validate_body, AssetsHandler


TEST_NAMESPACE = 'c8ab01'
TOKEN = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbGllbnQiOnsic2VydmljZV90eXBlIjoiaW5kZXgiLCJvcmdhbmlzYXRpb25faWQiOiJ0Z' \
        'XN0Y28iLCJpZCI6IjQyMjVmNDc3NGQ2ODc0YTY4NTY1YTA0MTMwMDAxMTQ0In0sImRlbGVnYXRlIjpmYWxzZSwiYXVkIjoibG9jYWxob3N0Ojg' \
        'wMDcvYXV0aG9yaXplIiwiZXhwIjoxNDU2OTM5NDk0LCJpc3MiOiJsb2NhbGhvc3Q6ODAwNy90b2tlbiIsInNjb3BlIjoicmVhZCIsImdyYW50X' \
        '3R5cGUiOiJjbGllbnRfY3JlZGVudGlhbHMiLCJzdWIiOiI0MjI1ZjQ3NzRkNjg3NGE2ODU2NWEwNDEzMDAwMTE0NCJ9.J4gFHMU-v_1f5xgWjd' \
        '42JaZhHpYfaccPtvq5uZMox3jvcs2A7q1exI3YIB75x589wp6QRpChr5C-If4bR71vpZ09cSMoX4UKR5WOaMDAMeMh2QPEHYUCE1VWEyrr_o1i' \
        'ljSk-bNfo8Mpufl67NL0J7rU7ZJ-o3ZwgoPIDTA1x1utcrvlLKTlWkmYGqEEBXxuL0V_vOGHW6UohXAA87jdMlgQRNTaZo75ETqbKp4sPIuiXz' \
        'OoidEPjbvZpo7LkAfAea9Js-B6muWWaI_i2FO2K3c6XJvxZAiyufL-nE-fx1vSJQeOixEr6zbnOF_s7byETxHKlCwOrxpx0wqPrE0ttw'


class PartialMockedHandler(AssetsHandler):
    def __init__(self, content_type=None):
        super(PartialMockedHandler, self).__init__(application=MagicMock(),
                                                   request=MagicMock())
        self.finish = MagicMock()
        self.token = {'sub': 'client1', 'client': {'id': 'testco'}}
        self.request.headers = {}

        if content_type:
            self.request.headers['Content-Type'] = content_type


def test__validate_body():
    request = MagicMock()
    request.body = 'test'
    _validate_body(request)


def test__validate_body_no_body():
    request = MagicMock()
    request.body = None
    with pytest.raises(exceptions.HTTPError) as exc:
        _validate_body(request)
    assert exc.value.status_code == 400
    assert exc.value.errors == 'No Data in Body'


def test__validate_body_empty_body():
    request = MagicMock()
    request.body = ''
    with pytest.raises(exceptions.HTTPError) as exc:
        _validate_body(request)
    assert exc.value.status_code == 400
    assert exc.value.errors == 'Body is empty string'


@patch('repository.controllers.assets_handler._validate_body', return_value=None)
@patch('repository.controllers.assets_handler.helper')
@patch('repository.controllers.assets_handler.audit')
@patch('repository.controllers.assets_handler.asset')
@gen_test
def test_repository_assets_handler_post(assets, audit, helper, _validate_body):
    helper.validate.return_value = None
    assets.store.return_value = make_future('asset data')
    audit.log_added_assets.return_value = make_future(None)

    handler = PartialMockedHandler()
    yield handler.post(TEST_NAMESPACE)

    assert assets.store.call_count == 1
    audit.log_added_assets.assert_called_once_with(
        {'sub': 'client1', 'client': {'id': 'testco'}},
        'asset data',
        repository_id='c8ab01')
    handler.finish.assert_called_once_with({"status": 200})


@patch('repository.controllers.assets_handler._validate_body', return_value=None)
@patch('repository.controllers.assets_handler.helper')
@patch('repository.controllers.assets_handler.asset')
def test_repository_assets_handler_post_error(assets, helper, _validate_body):
    helper.validate.return_value = None

    def mock_store(body, namespace, content_type):
        raise exceptions.HTTPError(400, 'errormsg')
    assets.store.side_effect = mock_store

    handler = PartialMockedHandler()

    with pytest.raises(exceptions.HTTPError) as exc:
        yield handler.post(TEST_NAMESPACE)

    assert exc.value.status_code == 400


@gen_test
def test_repository_assets_handler_post_invalid_content_type():
    def mock_validate(_):
        raise exceptions.HTTPError(415, 'errormsg')

    handler = PartialMockedHandler(content_type='application/json')

    with pytest.raises(exceptions.HTTPError) as exc:
        yield handler.post(TEST_NAMESPACE)

    assert exc.value.status_code == 415


@patch('repository.controllers.assets_handler._validate_body')
@gen_test
def test_repository_assets_handler_post_invalid_body(_validate_body):
    def mock_validate(_):
        raise exceptions.HTTPError(400, 'errormsg')
    _validate_body.side_effect = mock_validate

    handler = PartialMockedHandler()

    with pytest.raises(exceptions.HTTPError) as exc:
        yield handler.post(TEST_NAMESPACE)

    assert exc.value.status_code == 400


@patch('repository.controllers.assets_handler._validate_body', return_value=None)
@patch('repository.controllers.assets_handler.helper')
@gen_test
def test_repository_assets_handler_post_invalid_body_xml(helper, _validate_body):
    def mock_validate(data, format=None):
        raise exceptions.HTTPError(400, 'errormsg')
    helper.validate.side_effect = mock_validate

    handler = PartialMockedHandler()

    with pytest.raises(exceptions.HTTPError) as exc:
        yield handler.post('repository1')

    assert exc.value.status_code == 400
