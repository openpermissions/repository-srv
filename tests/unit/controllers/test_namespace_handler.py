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

import tornado.httpclient
from repository.controllers.namespace_handler import NamespaceHandler


TEST_NAMESPACE = 'c8ab01'


class PartialMockedHandler(NamespaceHandler):
    def __init__(self):
        super(PartialMockedHandler, self).__init__(application=MagicMock(), request=MagicMock())
        self.finish = MagicMock()


@patch('repository.controllers.namespace_handler.create_namespace', return_value = make_future(True))
def test_namespace_handler_post(create_namespace):
    handler = PartialMockedHandler()
    handler.post(TEST_NAMESPACE).result()

    create_namespace.assert_called_once_with(TEST_NAMESPACE)
    handler.finish.assert_called_once_with({"status": 200})


@patch('repository.controllers.namespace_handler.create_namespace', return_value = make_future(True))
def test_namespace_handler_http_error(create_namespace):
    create_namespace.side_effect = tornado.httpclient.HTTPError(404, "Error")

    handler = PartialMockedHandler()
    with pytest.raises(exceptions.HTTPError) as exc:
        handler.post(TEST_NAMESPACE).result()

    assert exc.value.status_code == 500


@patch('repository.controllers.namespace_handler.create_namespace', return_value = make_future(True))
def test_namespace_handler_http_conflict(create_namespace):
    create_namespace.side_effect = tornado.httpclient.HTTPError(409, "Error")

    handler = PartialMockedHandler()
    with pytest.raises(exceptions.HTTPError) as exc:
        handler.post(TEST_NAMESPACE).result()

    assert exc.value.status_code == 400
