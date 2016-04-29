# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

from __future__ import unicode_literals
from mock import MagicMock, patch
import pytest
import urllib
import tornado.httpclient

from koi.exceptions import HTTPError
from koi.test_helpers import gen_test, make_future

from repository.controllers.base import RepoBaseHandler


class PartialMockedHandler(RepoBaseHandler):
    def __init__(self):
        super(PartialMockedHandler, self).__init__(application=MagicMock(),
                                                   request=MagicMock())
        self.finish = MagicMock()
        self.request.method = 'GET'
        self.path_kwargs = {'repository_id': 'repo1'}


@patch('repository.controllers.base.options')
@patch('repository.controllers.base.API')
@gen_test
def test_verify_repository_token_true(API, options):
    options.service_id = 'service1'
    options.secret_id = 'secret1'
    client = API().auth.verify
    client.post.return_value = make_future({'status': 200, 'has_access': True})

    handler = PartialMockedHandler()
    result = yield handler.verify_repository_token('token1', 'r', 'repo1')

    headers = {'Content-Type': 'application/x-www-form-urlencoded',
               'Accept': 'application/json'}
    body = urllib.urlencode({
        'token': 'token1',
        'requested_access': 'r',
        'resource_id': 'repo1'
    })

    client.prepare_request.assert_called_with(
        request_timeout=180,
        headers=headers
    )
    client.post.assert_called_once_with(body=body)
    assert result is True


@patch('repository.controllers.base.options')
@patch('repository.controllers.base.API')
@gen_test
def test_verify_repository_token_false(API, options):
    options.service_id = 'service1'
    options.secret_id = 'secret1'
    client = API().auth.verify
    client.post.return_value = make_future({'status': 200, 'has_access': False})

    handler = PartialMockedHandler()
    result = yield handler.verify_repository_token('token1', 'r', 'repo1')

    headers = {'Content-Type': 'application/x-www-form-urlencoded',
               'Accept': 'application/json'}
    body = urllib.urlencode({
        'token': 'token1',
        'requested_access': 'r',
        'resource_id': 'repo1'
    })

    client.prepare_request.assert_called_with(
        request_timeout=180,
        headers=headers
    )
    client.post.assert_called_once_with(body=body)
    assert result is False


@patch('repository.controllers.base.options')
@patch('repository.controllers.base.API')
@gen_test
def test_verify_repository_token_no_repo_id(API, options):
    options.service_id = 'service1'
    options.secret_id = 'secret1'
    client = API().auth.verify
    client.post.return_value = make_future({'status': 200, 'has_access': True})

    handler = PartialMockedHandler()
    result = yield handler.verify_repository_token('token1', 'r', None)

    headers = {'Content-Type': 'application/x-www-form-urlencoded',
               'Accept': 'application/json'}
    body = urllib.urlencode({
        'token': 'token1',
        'requested_access': 'r'
    })

    client.prepare_request.assert_called_with(
        request_timeout=180,
        headers=headers
    )
    client.post.assert_called_once_with(body=body)
    assert result is True


@patch('repository.controllers.base.options')
@patch('repository.controllers.base.API')
@gen_test
def test_verify_repository_token_http_error(API, options):
    options.service_id = 'service1'
    options.secret_id = 'secret1'
    client = API().auth.verify
    client.post.side_effect = tornado.httpclient.HTTPError(403, 'errormsg')

    handler = PartialMockedHandler()

    with pytest.raises(HTTPError) as exc:
        yield handler.verify_repository_token('token1', 'r', 'repo1')

    headers = {'Content-Type': 'application/x-www-form-urlencoded',
               'Accept': 'application/json'}
    body = urllib.urlencode({
        'token': 'token1',
        'requested_access': 'r',
        'resource_id': 'repo1'
    })

    client.prepare_request.assert_called_with(
        request_timeout=180,
        headers=headers
    )
    client.post.assert_called_once_with(body=body)
    assert exc.value.status_code == 500


@patch('repository.controllers.base.options')
@patch('repository.controllers.base.RepoBaseHandler.verify_repository_token')
@patch('repository.controllers.base.jwt')
@gen_test
def test_prepare_no_repository_id(jwt, verify_repository_token, options):
    jwt.decode.return_value = {
        "client": {
            "service_type": "external",
            "organisation_id": "developerco",
            "id": "client3"
        },
        "sub": "client1"
    }
    verify_repository_token.return_value = make_future(True)

    options.use_oauth = True
    handler = PartialMockedHandler()
    handler.request.headers = {'Authorization': 'Bearer token1234'}
    handler.path_kwargs = {}

    yield handler.prepare()

    verify_repository_token.assert_called_once_with('token1234', 'r', None)
    assert handler.client_organisation == 'client1'
    assert handler.on_behalf_of == 'client3'


@patch('repository.controllers.base.options')
@patch('repository.controllers.base.RepoBaseHandler.verify_repository_token')
@patch('repository.controllers.base.jwt')
@gen_test
def test_prepare_oauth_required_valid(jwt, verify_repository_token, options):
    jwt.decode.return_value = {
        "client": {
            "service_type": "external",
            "organisation_id": "developerco",
            "id": "client3"
        },
        "sub": "client1"
    }

    verify_repository_token.return_value = make_future(True)
    options.use_oauth = True
    handler = PartialMockedHandler()
    handler.request.headers = {'Authorization': 'Bearer token1234'}

    yield handler.prepare()

    verify_repository_token.assert_called_once_with('token1234', 'r', 'repo1')
    assert handler.client_organisation == 'client1'
    assert handler.on_behalf_of == 'client3'


@patch('repository.controllers.base.options')
@patch('repository.controllers.base.RepoBaseHandler.verify_repository_token')
@patch('repository.controllers.base.jwt')
@gen_test
def test_prepare_oauth_required_missing_bearer(jwt, verify_repository_token, options):
    jwt.decode.return_value = {
        "client": {
            "service_type": "external",
            "organisation_id": "developerco",
            "id": "client3"
        },
        "sub": "client1"
    }
    verify_repository_token.return_value = make_future(True)
    options.use_oauth = True
    handler = PartialMockedHandler()
    handler.request.headers = {'Authorization': 'token1234'}

    yield handler.prepare()

    verify_repository_token.assert_called_once_with('token1234', 'r', 'repo1')
    assert handler.client_organisation == 'client1'
    assert handler.on_behalf_of == 'client3'


@patch('repository.controllers.base.options')
@patch('repository.controllers.base.RepoBaseHandler.verify_repository_token')
@gen_test
def test_prepare_oauth_required_invalid(verify_repository_token, options):
    verify_repository_token.return_value = make_future(False)
    options.use_oauth = True
    handler = PartialMockedHandler()
    handler.request.headers = {'Authorization': 'Bearer token1234'}

    with pytest.raises(HTTPError) as exc:
        yield handler.prepare()

    verify_repository_token.assert_called_once_with('token1234', 'r', 'repo1')
    assert exc.value.status_code == 403


@patch('repository.controllers.base.options')
@patch('repository.controllers.base.RepoBaseHandler.verify_repository_token')
@gen_test
def test_prepare_oauth_required_missing_header(verify_repository_token, options):
    options.use_oauth = True
    handler = PartialMockedHandler()
    handler.request.headers = {}

    with pytest.raises(HTTPError) as exc:
        yield handler.prepare()

    assert not verify_repository_token.called
    assert exc.value.status_code == 401


@patch('repository.controllers.base.options')
@patch('repository.controllers.base.RepoBaseHandler.verify_repository_token')
@gen_test
def test_prepare_oauth_required_unauthenticated_endpoint(verify_repository_token, options):
    options.use_oauth = True
    handler = PartialMockedHandler()
    handler.METHOD_ACCESS = {
        'GET': handler.UNAUTHENTICATED_ACCESS
    }

    yield handler.prepare()

    assert not verify_repository_token.called
    assert handler.client_organisation is None
    assert handler.client_organisation is None


@patch('repository.controllers.base.options')
@patch('repository.controllers.base.RepoBaseHandler.verify_repository_token')
@gen_test
def test_prepare_oauth_not_required(verify_repository_token, options):
    options.use_oauth = False
    handler = PartialMockedHandler()

    yield handler.prepare()

    assert not verify_repository_token.called
    assert handler.client_organisation is None
    assert handler.client_organisation is None


@pytest.mark.parametrize('content_type', RepoBaseHandler.ALLOWED_CONTENT_TYPES)
def test_get_content_type(content_type):
    handler = PartialMockedHandler()
    handler.request.headers = {'Content-Type': content_type}

    assert handler.get_content_type() == content_type


def test_default_content_type():
    handler = PartialMockedHandler()
    handler.request.headers = {}

    assert handler.get_content_type() == RepoBaseHandler.DEFAULT_CONTENT_TYPE


def test_invalid_content_type():
    handler = PartialMockedHandler()
    handler.request.headers = {'Content-Type': 'application/json'}

    with pytest.raises(HTTPError) as exc:
        handler.get_content_type()

    assert exc.value.status_code == 415
