# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

"""Handlers for namespaces"""
import logging
from koi.exceptions import HTTPError
from tornado.gen import coroutine
import tornado.httpclient
from .base import RepoBaseHandler
from ..models.framework.db import create_namespace


class NamespaceHandler(RepoBaseHandler):
    """Handler to initialise namespace"""
    @coroutine
    def post(self, repository_id):
        """
        Initialise a namespace if it has not already been initialised

        :param repository_id: id of repository/namespace
        """
        # If not running in standalone mode, the RepoBaseHandler will check to ensure repository id
        # is already registered with the accounts service, and will raise a 404 if not.

        try:
            yield create_namespace(repository_id)
        except tornado.httpclient.HTTPError as exc:
            # Must be converted to a tornado.web.HTTPError for the server
            # to handle it correctly
            logging.exception(exc.message)

            if exc.code == 409:
                raise HTTPError(400, 'Namespace {} already exists'.format(repository_id))
            else:
                raise HTTPError(500, 'Internal Server Error')

        self.finish({'status': 200})
