# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

from functools import partial
from mock import MagicMock, patch
import pytest
from koi.test_helpers import make_future, gen_test
from koi.exceptions import HTTPError
from tornado.ioloop import IOLoop
from repository.controllers import sets_handler

TEST_NAMESPACE = 'c8ab01'


def PartialMockedHandler(handler):
    class PartialMocked(handler):
        def __init__(self):
            super(PartialMocked, self).__init__(application=MagicMock(), request=MagicMock())
            self.finish = MagicMock()
            self.client_organisation = 'client1'
            self.request.headers = {}

    return PartialMocked()


@patch("repository.controllers.sets_handler.audit")
@patch("repository.controllers.sets_handler.Set")
@patch("repository.controllers.sets_handler.DatabaseConnection", return_value=TEST_NAMESPACE)
@gen_test
def test_sets_handler_post(DatabaseConnection, Set, audit):
    """
    Test asset post lead to Set new_set
    """
    handler = PartialMockedHandler(sets_handler.SetsHandler)
    handler.request.body = '{"title": "test"}'
    handler.request.headers = {"Content-Type": "application/json"}

    set_id = "504504"
    Set.new_set.return_value = make_future(set_id)
    yield handler.post(TEST_NAMESPACE)

    assert (audit.log.call_count == 1)
    assert (Set.new_set.call_count == 1)
    handler.finish.assert_called_once_with({'status': 200, 'data': {'id': set_id}})


@patch("repository.controllers.sets_handler.audit")
@patch("repository.controllers.sets_handler.Set")
@patch("repository.controllers.sets_handler.DatabaseConnection", return_value=TEST_NAMESPACE)
@gen_test
def test_sets_handler_get(DatabaseConnection, Set, audit):
    """
    Test assets get lead to Set _retrieve_paged_ids
    """
    """
    Test asset post lead to Set new_set
    """
    handler = PartialMockedHandler(sets_handler.SetsHandler)

    set_id = '342394'
    updated = "now"
    set_title = "test set"
    dummy_reply = [(set_id, set_title, updated)]
    Set._retrieve_paged_ids.return_value = make_future(dummy_reply)
    Set.exists.return_value = make_future(True)
    yield handler.get(TEST_NAMESPACE)

    assert (audit.log.call_count == 0)
    assert (Set._retrieve_paged_ids.call_count == 1)
    handler.finish.assert_called_once_with({'status': 200, 'data': {'sets': [{'last_modified': updated, 'title': set_title, 'id': set_id}]}})


@patch("repository.controllers.sets_handler.audit")
@patch("repository.controllers.sets_handler.Set")
@patch("repository.controllers.sets_handler.DatabaseConnection", return_value=TEST_NAMESPACE)
@gen_test
def test_set_handler_get(DatabaseConnection, Set, audit):
    """
    Test assets get lead to Set retrieve
    """
    """
    Test asset post lead to Set new_set
    """
    handler = PartialMockedHandler(sets_handler.SetHandler)

    set_id = '342394'
    dummy_reply = {'dummy': 'object'}
    Set.retrieve.return_value = make_future(dummy_reply)
    Set.exists.return_value = make_future(True)
    yield handler.get(TEST_NAMESPACE, set_id)

    assert (audit.log.call_count == 0)
    assert (Set.retrieve.call_count == 1)
    handler.finish.assert_called_once_with({'status': 200, 'data': dummy_reply})


@patch("repository.controllers.sets_handler.audit")
@patch("repository.controllers.sets_handler.Set")
@patch("repository.controllers.sets_handler.DatabaseConnection", return_value=TEST_NAMESPACE)
@gen_test
def test_set_assets_handler_get(DatabaseConnection, Set, audit):
    """
    Check set assset element get the elements
    """
    handler = PartialMockedHandler(sets_handler.SetAssetsHandler)
    handler.request.body = '{"title": "test"}'
    handler.request.headers = {"Content-Type": "application/json"}

    set_id = "504504"
    Set.get_elements.return_value = make_future(map(str, range(10)))
    Set.exists.return_value = make_future(True)
    yield handler.get(TEST_NAMESPACE, set_id)

    assert (audit.log.call_count == 0)
    assert (Set.get_elements.call_count == 1)
    handler.finish.assert_called_once_with({'status': 200, 'data': {'assets': map(str, range(10))}})

@patch("repository.controllers.sets_handler.audit")
@patch("repository.controllers.sets_handler.Asset")
@patch("repository.controllers.sets_handler.Set")
@patch("repository.controllers.sets_handler.DatabaseConnection", return_value=TEST_NAMESPACE)
@gen_test
def test_set_asset_handler_get(DatabaseConnection, Set, Asset, audit):
    handler = PartialMockedHandler(sets_handler.SetAssetHandler)
    handler.request.body = '{"title": "test"}'
    handler.request.headers = {"Content-Type": "application/json"}

    set_id = "504504"
    asset_id = "a55e4"
    Set.has_element.return_value = make_future(True)
    Asset.exists.return_value = make_future(True)
    Set.exists.return_value = make_future(True)
    yield handler.get(TEST_NAMESPACE, set_id, asset_id)

    assert (audit.log.call_count == 0)
    assert (Set.has_element.call_count == 1)
    handler.finish.assert_called_once_with({'status': 200, 'data': {'is_member': True}})


@patch("repository.controllers.sets_handler.audit")
@patch("repository.controllers.sets_handler.Asset")
@patch("repository.controllers.sets_handler.Set")
@patch("repository.controllers.sets_handler.DatabaseConnection", return_value=TEST_NAMESPACE)
@gen_test
def test_set_asset_handler_post(DatabaseConnection, Set, Asset, audit):
    handler = PartialMockedHandler(sets_handler.SetAssetHandler)
    handler.request.body = '{"title": "test"}'
    handler.request.headers = {"Content-Type": "application/json"}

    set_id = "504504"
    asset_id = "a55e4"
    Set.append_elements.return_value = make_future(True)
    Asset.exists.return_value = make_future(True)
    Set.exists.return_value = make_future(True)
    yield handler.post(TEST_NAMESPACE, set_id, asset_id)

    assert (audit.log.call_count == 0)
    assert (Set.append_elements.call_count == 1)
    handler.finish.assert_called_once_with({'status': 200})


@patch("repository.controllers.sets_handler.audit")
@patch("repository.controllers.sets_handler.Asset")
@patch("repository.controllers.sets_handler.Set")
@patch("repository.controllers.sets_handler.DatabaseConnection", return_value=TEST_NAMESPACE)
@gen_test
def test_set_asset_handler_delete(DatabaseConnection, Set, Asset, audit):
    handler = PartialMockedHandler(sets_handler.SetAssetHandler)
    handler.request.body = '{"title": "test"}'
    handler.request.headers = {"Content-Type": "application/json"}

    set_id = "504504"
    asset_id = "a55e4"
    Set.exists.return_value = make_future(True)
    Asset.exists.return_value = make_future(True)
    Set.remove_elements.return_value = make_future(True)
    yield handler.delete(TEST_NAMESPACE, set_id, asset_id)

    assert (audit.log.call_count == 0)
    assert (Set.remove_elements.call_count == 1)
    handler.finish.assert_called_once_with({'status': 200})
