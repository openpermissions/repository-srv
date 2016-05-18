# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

from __future__ import unicode_literals

import logging
import os
import pytest
from koi.exceptions import HTTPError
from koi.test_helpers import make_future, gen_test
from mock import patch
from tornado import httpclient

from repository.models.framework.db import (load_data, load_directory, DatabaseConnection, _initialise_namespace, INITIAL_DATA,
                                            _namespace_url, _set_accept_header, request, NAMESPACE_ASSET, create_namespace
                                            )
from ..util import create_mockdb

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), '../../..', 'data')
FIXTURE_FILE_COUNT = 5
TEST_NAMESPACE = 'c8ab01'


@gen_test
def test_load_data_valid_ttl():
    db = create_mockdb()
    yield load_data(os.path.abspath(os.path.join(FIXTURE_DIR, 'sample.ttl')), db)
    assert db.store.call_count == 1


@gen_test
def test_load_data_valid_xml():
    db = create_mockdb()
    yield load_data(os.path.abspath(os.path.join(FIXTURE_DIR, 'sample.xml')), db)
    assert db.store.call_count == 1


@patch('repository.models.framework.db.logging')
@gen_test
def test_load_data_invalid_file_type(logging):
    db = create_mockdb()
    yield load_data(os.path.abspath(os.path.join(FIXTURE_DIR, 'invalid_data.txt')), db)
    assert logging.error.called
    assert not db.store.call_count


# FIXME: AGAIN DON'T LIKE THIS TEST - FAILS BUT DON'T BRING MUCH
@patch('repository.models.framework.db.logging')
@patch('repository.models.framework.db.load_data', return_value=make_future(None))
@gen_test
def test_load_directory_valid(load_data, logging):
    yield load_directory(FIXTURE_DIR, 'c8ab01')

    assert logging.info.call_count >= FIXTURE_FILE_COUNT
    assert load_data.call_count >= FIXTURE_FILE_COUNT


@patch('repository.models.framework.db.load_data')
@gen_test
def test_load_directory_invalid(load_data):
    yield load_directory(os.path.join(FIXTURE_DIR, 'dir_does_not_exist'), 'c8ab01')
    assert load_data.call_count == 0


@patch('repository.models.framework.db.AsyncHTTPClient.fetch', return_value=make_future(None))
@patch('repository.models.framework.db.options')
@gen_test
def test__initialise_namespace_retrieves_query(options, fetch):
    options.url_repo_db = 'https://localhost'
    options.repo_db_port = '8080'
    options.repo_db_path = '/bigdata/namespace/'

    yield _initialise_namespace('foo')
    assert NAMESPACE_ASSET.format('foo').strip() == fetch.call_args[1]['body']


@patch('repository.models.framework.db.AsyncHTTPClient.fetch', return_value=make_future(None))
@patch('repository.models.framework.db.options')
@gen_test
def test__initialise_namespace_creates_namespace(options, fetch):
    options.url_repo_db = 'https://localhost'
    options.repo_db_port = '8080'
    options.repo_db_path = '/bigdata/namespace/'

    yield _initialise_namespace('foo')
    fetch.assert_called_once_with(
        'https://localhost:8080/bigdata/namespace',
        method='POST',
        body=NAMESPACE_ASSET.format('foo').strip(),
        headers={'Content-Type': 'application/xml'})


@patch('repository.models.framework.db.logging.warning', return_value=True)
@patch('repository.models.framework.db.AsyncHTTPClient.fetch')
@patch('repository.models.framework.db.options')
@gen_test
def test__initialise_namespace_http_conflict(options, fetch, warning):
    options.url_repo_db = 'https://localhost'
    options.repo_db_port = '8080'
    options.repo_db_path = '/bigdata/namespace/'

    fetch.side_effect = httpclient.HTTPError(409, 'Namespace already exists')

    yield _initialise_namespace('foo')

    assert warning.called


@patch('repository.models.framework.db.logging.error', return_value=True)
@patch('repository.models.framework.db.AsyncHTTPClient.fetch')
@patch('repository.models.framework.db.options')
@gen_test
def test__initialise_namespace_http_error(options, fetch, error):
    options.url_repo_db = 'https://localhost'
    options.repo_db_port = '8080'
    options.repo_db_path = '/bigdata/namespace/'

    fetch.side_effect = httpclient.HTTPError(500, 'Internal Server Error')
    yield _initialise_namespace('foo')
    assert error.called


@patch('repository.models.framework.db.load_directory', return_value=make_future(None))
@patch('repository.models.framework.db._initialise_namespace', return_value=make_future(None))
@gen_test
def test_create_namespace(_initialise_namespace, load_directory):
    yield create_namespace('foo')
    _initialise_namespace.assert_called_once_with('foo')
    load_directory.assert_called_once_with(INITIAL_DATA, 'foo')


@patch('repository.models.framework.db.load_directory', side_effect=HTTPError(400, ""))
@patch('repository.models.framework.db._initialise_namespace', return_value=make_future(None))
@gen_test
def test_create_namespace_error_initialise_err_code(_initialise_namespace, load_directory):
    with pytest.raises(HTTPError) as exc:
        yield create_namespace('foo')
    assert exc.value.status_code == 400


@patch('repository.models.framework.db.options')
@gen_test
def test_url_contains_url_repo_db(options):
    options.url_repo_db = 'https://localhost'
    result = _namespace_url('namespace01')
    assert 'https://localhost' in result


@patch('repository.models.framework.db.options')
@gen_test
def test_url_contains_db_port(options):
    options.repo_db_port = '8080'
    result = _namespace_url('namespace01')
    assert '8080' in result


@patch('repository.models.framework.db.options')
@gen_test
def test_url_contains_db_path(options):
    options.repo_db_path = '/bigdata/namespace/'
    result = _namespace_url('namespace01')
    assert '/bigdata/namespace' in result


@patch('repository.models.framework.db.options')
@gen_test
def test_url_contains_namespace(options):
    result = _namespace_url('namespace01')
    assert 'namespace01' in result


@patch('repository.models.framework.db.options')
@gen_test
def test_url(options):
    options.url_repo_db = 'https://localhost'
    options.repo_db_port = '8080'
    options.repo_db_path = '/bigdata/namespace/'
    result = _namespace_url('namespace01')
    assert result == 'https://localhost:8080/bigdata/namespace/namespace01'


@patch('repository.models.framework.db.options')
def test_url_empty_namespace(options):
    options.url_repo_db = 'https://localhost'
    options.repo_db_port = '8080'
    options.repo_db_path = '/bigdata/namespace/'
    result = _namespace_url('')
    assert result == 'https://localhost:8080/bigdata/namespace'


def test__set_accept_header_csv():
    result = _set_accept_header('csv')
    assert result == {'Accept': 'text/csv'}


def test__set_accept_header_xml():
    result = _set_accept_header('xml')
    assert result == {'Accept': 'application/sparql-results+xml'}


def test__set_accept_header_json():
    result = _set_accept_header('json')
    assert result == {'Accept': 'application/sparql-results+json'}


def test__set_accept_header_none():
    result = _set_accept_header(None)
    assert result == {}


def test__set_accept_header_invalid():
    with pytest.raises(Exception) as exc:
        _set_accept_header('foobar')
    assert exc.value.message == "unexpected type: foobar"


@patch('repository.models.framework.db._namespace_url', return_value='https://localhost:8000/bigdata/namespace/c8ab01')
@patch('repository.models.framework.db.AsyncHTTPClient.fetch', return_value=make_future('my response'))
@gen_test
def test_request_uses_generated_db_url(fetch, url):
    yield request('body type', 'c8ab01', 'pay load')
    assert fetch.call_args[0][0] == 'https://localhost:8000/bigdata/namespace/c8ab01'


@patch('repository.models.framework.db._namespace_url', return_value='https://localhost:8000/bigdata/namespace/c8ab01')
@patch('repository.models.framework.db.AsyncHTTPClient.fetch', return_value=make_future('my response'))
@gen_test
def test_request_has_content_type(fetch, url):
    yield request('body type', 'c8ab01', 'pay load', content_type='application/json')
    assert fetch.call_args[1]['headers'] == {'Content-Type': 'application/json'}


@patch('repository.models.framework.db._namespace_url', return_value='https://localhost:8000/bigdata/namespace/c8ab01')
@patch('repository.models.framework.db.AsyncHTTPClient.fetch', return_value=make_future('my response'))
@gen_test
def test_request_no_content_type(fetch, url):
    yield request('body type', 'c8ab01', 'pay load')
    assert fetch.call_args[1]['headers'] == {}


@patch('repository.models.framework.db._namespace_url', return_value='https://localhost:8000/bigdata/namespace/c8ab01')
@patch('repository.models.framework.db._set_accept_header', return_value={'Accept': 'text/csv'})
@patch('repository.models.framework.db.AsyncHTTPClient.fetch', return_value=make_future('my response'))
@gen_test
def test_request_has_response_type(fetch, _set_accept_header, url):
    yield request('body type', 'c8ab01', 'pay load', response_type='csv')
    _set_accept_header.assert_called_once_with('csv')
    assert fetch.call_args[1]['headers'] == {'Accept': 'text/csv'}


@patch('repository.models.framework.db._namespace_url', return_value='https://localhost:8000/bigdata/namespace/c8ab01')
@patch('repository.models.framework.db.AsyncHTTPClient.fetch', return_value=make_future('my response'))
@gen_test
def test_request_no_response_type(fetch, url):
    yield request('body type', 'c8ab01', 'pay load')
    assert fetch.call_args[1]['headers'] == {}


@patch('repository.models.framework.db._namespace_url', return_value='https://localhost:8000/bigdata/namespace/c8ab01')
@patch('repository.models.framework.db._set_accept_header', return_value={'Accept': 'text/csv'})
@patch('repository.models.framework.db.AsyncHTTPClient.fetch', return_value=make_future('my response'))
@gen_test
def test_request_has_content_type_and_response_type(fetch, _set_accept_header, url):
    yield request('body type', 'c8ab01', 'pay load', response_type='csv', content_type='application/json')
    _set_accept_header.assert_called_once_with('csv')
    assert fetch.call_args[1]['headers'] == {'Content-Type': 'application/json', 'Accept': 'text/csv'}


@patch('repository.models.framework.db._namespace_url', return_value='https://localhost:8000/bigdata/namespace/c8ab01')
@patch('repository.models.framework.db.AsyncHTTPClient.fetch', return_value=make_future('my response'))
@gen_test
def test_request_has_body_type(fetch, url):
    yield request('body type', 'c8ab01', 'pay load')
    assert fetch.call_args[1]['body'] == 'body+type=pay+load'


@patch('repository.models.framework.db._namespace_url', return_value='https://localhost:8000/bigdata/namespace/c8ab01')
@patch('repository.models.framework.db.AsyncHTTPClient.fetch', return_value=make_future('my response'))
@gen_test
def test_request_no_body_type(fetch, url):
    db = DatabaseConnection(TEST_NAMESPACE)
    yield request(None, 'c8ab01', 'pay load')
    assert fetch.call_args[1]['body'] == 'pay load'


@patch('repository.models.framework.db._namespace_url', return_value='https://localhost:8000/bigdata/namespace/c8ab01')
@patch('repository.models.framework.db.AsyncHTTPClient.fetch', return_value=make_future('my response'))
@gen_test
def test_request_valid_query(fetch, url):
    result = yield request(None, 'c8ab01', 'pay load')
    assert fetch.call_count == 1
    assert result == 'my response'


@patch('repository.models.framework.db.create_namespace')
@patch('repository.models.framework.db._namespace_url', return_value='https://localhost:8000/bigdata/namespace/c8ab01')
@patch('repository.models.framework.db.AsyncHTTPClient.fetch')
@gen_test
def test_request_invalid_query(fetch, url, create_namespace):
    fetch.side_effect = HTTPError(500, 'Internal Server Error')
    with pytest.raises(HTTPError) as exc:
        yield request(None, 'c8ab01', 'pay load')
    assert not create_namespace.called
    assert fetch.call_count == 1
    assert exc.value.status_code == 500


@patch('repository.models.framework.db.create_namespace', return_value=make_future(None))
@patch('repository.models.framework.db._namespace_url', return_value='https://localhost:8000/bigdata/namespace/c8ab01')
@gen_test
def test_request_no_namespace(url, create_namespace):
    with pytest.raises(httpclient.HTTPError) as exc:
        yield request(None, None, 'pay load')
        assert exc.value.code == 400
        assert exc.value.message == "HTTP 400: Namespace/Repository missing"


@patch('repository.models.framework.db.create_namespace', return_value=make_future(None))
@patch('repository.models.framework.db._namespace_url', return_value='https://localhost:8000/bigdata/namespace/c8ab01')
@patch('repository.models.framework.db.AsyncHTTPClient.fetch')
@gen_test
def test_request_no_namespace_then_invalid_query(fetch, url, create_namespace):
    fetch.side_effect = [httpclient.HTTPError(404, 'Not Found'), httpclient.HTTPError(500, 'Internal Server Error')]
    with pytest.raises(httpclient.HTTPError) as exc:
        yield request(None, 'c8ab01', 'pay load')
    assert create_namespace.call_count == 1
    assert fetch.call_count == 2
    assert exc.value.code == 500
