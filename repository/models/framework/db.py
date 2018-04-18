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

from functools import partial
from tornado.gen import coroutine, Return
from tornado.httpclient import AsyncHTTPClient, HTTPError
from tornado.options import options, define
from urllib import urlencode

from ..framework import helper

define("url_repo_db", help='location of database server', default="http://localhost", type=str)
define("repo_db_port", help='port on which the database runs', default="8080", type=str)

# FIXME: This is probably no more necessary
define("repo_db_path", help='path of the default namespace (deprecated)', default="/bigdata/namespace/", type=str)

NAMESPACE_ASSET = """
<?xml version="1.0" standalone="no"?>
<!DOCTYPE properties SYSTEM "http://java.sun.com/dtd/properties.dtd">
<properties>
  <entry key="com.bigdata.rdf.sail.namespace">{}</entry>
</properties>
"""

INITIAL_DATA = os.path.join(os.path.dirname(__file__), '../../../initial_data')


@coroutine
def load_directory(directory, repository_id):
    """
    Recursively walks through a directory and calls load_data on all files in directory
    :param directory: Directory path
    :param repository_id: repository namespace to load the data to
    """
    for dirpath, dnames, file_names in os.walk(directory):
        for file_name in file_names:
            abs_path = os.path.join(dirpath, file_name)
            logging.info("Found file {}".format(abs_path))
            yield load_data(abs_path, repository_id)


@coroutine
def load_data(filename, cdb):
    """
    Validates given file and then loads contents to given repository
    :param filename: filename string
    :param cdb: repository namespace to load the data or connection to database
    """
    if isinstance(cdb, basestring):
        cdb = DatabaseConnection(cdb)

    with open(filename, 'r') as content_file:
        content = content_file.read()

    if filename.endswith('.ttl'):
        helper.validate(content, format='turtle')
        yield cdb.store(
            content,
            content_type='text/turtle')
    elif filename.endswith('.xml') or filename.endswith('.rdf'):
        helper.validate(content, format='xml')
        yield cdb.store(
            content,
            content_type='application/xml')
    else:
        logging.error("File type must be ttl or xml")


@coroutine
def _initialise_namespace(namespace):
    """
    Initialise a new namespace in blazegraph

    :param namespace: name of new namespace
    :raises: HTTPError if problem creating name space
    """
    namespace_query = NAMESPACE_ASSET.format(namespace).strip()
    db_url = _namespace_url('')
    headers = {'Content-Type': 'application/xml'}
    yield AsyncHTTPClient().fetch(db_url, method="POST", body=namespace_query, headers=headers)


@coroutine
def create_namespace(namespace):
    yield _initialise_namespace(namespace)
    yield load_directory(INITIAL_DATA, namespace)


def _namespace_url(namespace):
    """
    Builds blazegraph url based on tornado options and namespace parameter

    :param namespace: Namespace to build url for
    :return: Blazegraph url
    """
    return "{0}:{1}{2}{3}".format(
        options.url_repo_db,
        options.repo_db_port,
        options.repo_db_path,
        namespace
    ).rstrip('/')


def _set_accept_header(accept_type):
    """
    Takes response type and converts to valid sparql accept header

    :param accept_type
    :return: Header dictionary
    """
    headers = {}
    if accept_type == 'csv':
        headers['Accept'] = 'text/csv'
    elif accept_type == 'xml':
        headers['Accept'] = 'application/sparql-results+xml'
    elif accept_type == 'json':
        headers['Accept'] = "application/sparql-results+json"
    elif accept_type is None:
        pass
    elif accept_type == 'wibble':
        headers['Accept'] = "application/sparql-results+json"
    else:
        if len (accept_type) and '#' == accept_type[0]:
            headers['Accept'] = accept_type[1:]
        else:
            raise Exception("unexpected type: " + str(accept_type))
    return headers


@coroutine
def request(body_type, namespace, payload,  response_type=None, content_type=None):
    """
    Makes request to blazegraph

    :param body_type: type of request (e.g: 'query', 'update' or None)
    :param payload: request body
    :param namespace: namespace of request
    :param response_type: Accept type for header ('csv', 'xml', 'json' or None)
    :param content_type: Content type for header
    :return: Response from blazegraph
    """
    if not namespace:
        raise HTTPError(400, "Namespace or repository missing")

    db_url = _namespace_url(namespace)
    headers = _set_accept_header(response_type)

    if content_type:
        headers['Content-Type'] = content_type

    if body_type:
        body = urlencode({body_type: payload})
    else:
        body = payload

    logging.debug(payload)
    try:
        rsp = yield AsyncHTTPClient().fetch(db_url, method="POST", body=body, headers=headers)
    except HTTPError as exc:
        # If response is 404 then namespace does not exist.
        # Lazily create namespace and retry request.
        if exc.code == 404:
            try:
                yield create_namespace(namespace)
            except HTTPError as exc:
                # Namespace already exists with a 409 error
                if exc.code != 409:
                    logging.error("%s:%s" % (str(exc.code), exc.message))
                else:
                    logging.warning('Namespace %s already exists' % namespace)

            rsp = yield AsyncHTTPClient().fetch(
                db_url, method="POST", body=body, headers=headers)
        else:
            raise exc

    raise Return(rsp)


class DatabaseConnection(object):
    def __init__(self, repository_id):
        self.repository_id = repository_id
        self.query = (partial(request, 'query', repository_id))
        self.update = (partial(request, 'update', repository_id))
        self.store = (partial(request, None, repository_id))
