# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.


import jwt
import logging
from urllib import urlencode

import tornado.httpclient
from tornado.gen import coroutine, Return
from tornado.options import options

from koi.exceptions import HTTPError
from koi.base import BaseHandler

from repository.models.framework.helper import PermissionException, ValidationException

from chub import API


class RepoBaseHandler(BaseHandler):
    client_organisation = None
    on_behalf_of = None
    CONTENT_TYPE_MAP = {
        'application/xml': 'xml',
        'text/rdf+n3': 'turtle',
        'application/ld+json': 'json-ld'
    }
    ALLOWED_CONTENT_TYPES = CONTENT_TYPE_MAP.keys()
    DEFAULT_CONTENT_TYPE = 'application/xml'

    def send_error(self, status_code=500, **kwargs):
        """
        Override tornado.RequestHandler's send_error to set the status code
        for exceptions
        """
        if 'exc_info' in kwargs:
            exc = kwargs['exc_info'][1]
            if isinstance(exc, ValidationException):
                status_code = 400
                kwargs['reason'] = 'Invalid data: ' + str(exc.args[0])
            elif isinstance(exc, PermissionException):
                status_code = 403
                kwargs['reason'] = 'Operation not allowed: ' + str(exc.args[0])

        return super(RepoBaseHandler, self).send_error(status_code, **kwargs)

    @coroutine
    def verify_repository_token(self, token, requested_access, repository_id=None):
        """
        Verify access to repository

        :param repository_id: id of repository being accessed
        :param token: Access token
        :param requested_access: the access level the client has requested
        :returns: boolean
        """
        client = API(options.url_auth,
                     auth_username=options.service_id,
                     auth_password=options.client_secret,
                     ca_certs=options.ssl_ca_cert)
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                   'Accept': 'application/json'}
        data = {
            'token': token,
            'requested_access': requested_access
        }
        if repository_id:
            data['resource_id'] = repository_id

        client.auth.verify.prepare_request(headers=headers, request_timeout=180)

        try:
            result = yield client.auth.verify.post(body=urlencode(data))
        except tornado.httpclient.HTTPError as ex:
            # Must be converted to a tornado.web.HTTPError for the server
            # to handle it correctly
            logging.exception(ex.message)
            raise HTTPError(500, 'Internal Server Error')
        raise Return(result['has_access'])

    @coroutine
    def prepare(self):
        """
        If OAuth verification is required, validate provided token.

        :raise: HTTPError if token does not have access
        """
        repository_id = self.path_kwargs.get('repository_id')

        requested_access = self.endpoint_access(self.request.method)
        use_oauth = getattr(options, 'use_oauth', None)
        if use_oauth and requested_access is not self.UNAUTHENTICATED_ACCESS:
            token = self.request.headers.get('Authorization', '').split(' ')[-1]
            if token:
                has_access = yield self.verify_repository_token(token, requested_access, repository_id)
                if not has_access:
                    msg = "'{}' access not granted.".format(requested_access)
                    raise HTTPError(403, msg)
                decoded_token = jwt.decode(token, verify=False)
                self.client_organisation = decoded_token['sub']
                self.on_behalf_of = decoded_token['client']['id']
            else:
                msg = 'OAuth token not provided'
                raise HTTPError(401, msg)

    def get_content_type(self):
        """
        Check the content type

        Override the request handler's list of ALLOWED_CONTENT_TYPES to control
        the permitted content types.

        :raises HTTPError: 415 status code if not allowed
        """
        content_type = self.request.headers.get('Content-Type', self.DEFAULT_CONTENT_TYPE)
        short_content_type = content_type.lower().split(';')[0]
        if short_content_type not in self.ALLOWED_CONTENT_TYPES:
            msg = '{} not supported. Must be one of {}'.format(
                content_type, ','.join(self.ALLOWED_CONTENT_TYPES)
            )
            raise HTTPError(415, msg)

        return content_type

    def data_format(self):
        """
        Get the data format from the content type (e.g. xml, turtle)

        Used for rdflib

        :raises HTTPError: 415 status code if content type is not allowed
        """
        content_type = self.get_content_type()
        return self.CONTENT_TYPE_MAP[content_type]
