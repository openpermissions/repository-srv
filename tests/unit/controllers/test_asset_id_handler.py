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
from koi.test_helpers import make_future

from repository.controllers.assets_handler import AssetIDHandler


TEST_NAMESPACE = 'c8ab01'


class PartialMockedHandler(AssetIDHandler):
    def __init__(self):
        super(PartialMockedHandler, self).__init__(application=MagicMock(), request=MagicMock())
        self.finish = MagicMock()
        self.client_organisation = 'client1'


@patch('repository.controllers.assets_handler.audit')
@patch('repository.controllers.assets_handler.asset')
def test_assets_handler_post(assets, audit):
    assets.exists.return_value = make_future(True)
    assets.add_ids.return_value = make_future([])

    handler = PartialMockedHandler()
    handler.request.headers = {'Content-Type': 'application/json'}
    handler.request.body = '{"ids": ["id1"]}'
    handler.post(TEST_NAMESPACE, 'asset1').result()

    audit.log_asset_ids.assert_called_once_with('client1', 'asset1', ['id1'])
    assets.add_ids.call_count == 1
    handler.finish.assert_called_once_with({"status": 200})


@patch('repository.controllers.assets_handler.asset')
def test_assets_handler_post_asset_doesnt_exists(assets):
    assets.exists.return_value = make_future(False)
    assets.add_ids.return_value = make_future([])

    handler = PartialMockedHandler()
    handler.request.headers = {'Content-Type': 'application/json'}
    handler.request.body = '{"ids": ["id1"]}'

    with pytest.raises(exceptions.HTTPError) as exc:
        handler.post(TEST_NAMESPACE, 'asset1').result()

    assert exc.value.status_code == 404


@patch('repository.controllers.assets_handler.asset')
def test_assets_handler_post_no_headers(assets):
    assets.exists.return_value = make_future(True)
    assets.add_ids.return_value = make_future([])

    handler = PartialMockedHandler()
    handler.request.body = '{"ids": ["id1"]}'

    with pytest.raises(exceptions.HTTPError) as exc:
        handler.post(TEST_NAMESPACE, 'asset1').result()

    assert exc.value.status_code == 415


@patch('repository.controllers.assets_handler.asset')
def test_assets_handler_post_no_body(assets):
    assets.exists.return_value = make_future(True)
    assets.add_ids.return_value = make_future([])

    handler = PartialMockedHandler()
    handler.request.headers = {'Content-Type': 'application/json'}
    handler.request.body = ''

    with pytest.raises(exceptions.HTTPError) as exc:
        handler.post(TEST_NAMESPACE, 'asset1').result()

    assert exc.value.status_code == 400


@patch('repository.controllers.assets_handler.asset')
def test_assets_handler_post_has_errors(assets):
    assets.exists.return_value = make_future(True)
    assets.add_ids.return_value = make_future(['errormsg1'])

    handler = PartialMockedHandler()
    handler.request.headers = {'Content-Type': 'application/json'}
    handler.request.body = '{"ids": ["id1"]}'

    with pytest.raises(exceptions.HTTPError) as exc:
        handler.post(TEST_NAMESPACE, 'asset1').result()

    assert exc.value.status_code == 400
