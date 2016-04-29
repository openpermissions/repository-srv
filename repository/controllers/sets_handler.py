# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.


"""API assets handler. Query offers from the db."""

from datetime import datetime
from tornado import gen

from koi.base import HTTPError

from .base import RepoBaseHandler
from .. import audit
from ..models.asset import Asset
from ..models.set import Set
from ..models.framework.helper import isoformat, date_format
from ..models.framework.db import DatabaseConnection


class SetsHandler(RepoBaseHandler):
    """List and create sets"""
    @gen.coroutine
    def get(self, repository_id):
        page = int(self.get_argument("page", "1"))
        page_size = int(self.get_argument("page_size", "20"))
        page_size = min(page_size, 1000)

        repository = DatabaseConnection(repository_id)
        sets = yield Set._retrieve_paged_ids([], page=page, page_size=page_size, repository=repository)
        sets = [{'id': str(o[0]).split('/')[-1], 'title':o[1], 'last_modified': o[2]} for o in sets]
        self.set_header('Content-Type', 'application/json')
        self.finish({'status': 200, 'data': {'sets': sets}})

    @gen.coroutine
    def post(self, repository_id):
        """
        Create a set.
        It is recommended to give sets a name.
        :param repository_id: str
        """

        title = self.get_argument('title', None)
        set_id = yield Set.new_set(DatabaseConnection(repository_id), title=title)
        audit.log(self.client_organisation, "Set created %s" % (set_id,))
        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        self.finish({'status': 200, 'data': {'id': set_id}})


class SetHandler(RepoBaseHandler):
    """Handler for individual sets"""

    @gen.coroutine
    def get(self, repository_id, set_id):
        """
        Retrieve one offer by set_id

        :param repository_id: the id of the repository
        :param set_id: the id of an offer
        :return: A JSON object containing an offer
        """
        repository = DatabaseConnection(repository_id)

        set_exists = yield Set.exists(repository, set_id)
        if not set_exists:
            raise HTTPError(404, "Set {} not found".format(set_id))

        set_obj = yield Set.retrieve(repository, set_id)

        self.finish({'status': 200, 'data': set_obj})


class SetAssetsHandler(RepoBaseHandler):
    """Link an asset with a set"""

    @gen.coroutine
    def get(self, repository_id, set_id):
        """
        Return all assets associated to a set

        :param repository_id: the id of the repository
        :param set_id: the id of an offer
        :return: A JSON object containing an offer
        """
        repository = DatabaseConnection(repository_id)

        set_exists = yield Set.exists(repository, set_id)
        if not set_exists:
            raise HTTPError(404, "Set {} not found".format(set_id))

        page = int(self.get_argument("page", "1"))
        page_size = int(self.get_argument("page_size", "100"))
        page_size = min(page_size, 1000)

        elements = yield Set.get_elements(repository, set_id, page, page_size)

        self.finish({'status': 200, 'data': {'assets': [e.split('/')[-1] for e in elements]}})

    @gen.coroutine
    def post(self, repository_id, set_id):
        """
        Replace all the elements in a set.

        :param repository_id: the id of the repository
        :param set_id: the id of an offer
        :return: A JSON object containing an offer
        """
        body = self.get_json_body(['assets'])
        repository = DatabaseConnection(repository_id)

        set_exists = yield Set.exists(repository, set_id)
        if not set_exists:
            raise HTTPError(404, "Set {} not found".format(set_id))

        yield Set.set_elements(repository, set_id, body['assets'])

        self.finish({'status': 200})


    @gen.coroutine
    def delete(self, repository_id, set_id):
        """
        Create the link between an element and a set.

        :param repository_id: the id of the repository
        :param set_id: the id of an offer
        :return: A JSON object containing an offer
        """
        repository = DatabaseConnection(repository_id)

        set_exists = yield Set.exists(repository, set_id)
        if not set_exists:
            raise HTTPError(404, "Set {} not found".format(set_id))

        yield Set.set_elements(repository, set_id, [])

        self.finish({'status': 200})


class SetAssetHandler(RepoBaseHandler):
    """Link an asset with a set"""
    @gen.coroutine
    def get(self, repository_id, set_id, asset_id):
        """
        Tells if an element is part of a set.

        :param repository_id: the id of the repository
        :param set_id: the id of an offer
        :return: A JSON object containing an offer
        """
        repository = DatabaseConnection(repository_id)

        set_exists = yield Set.exists(repository, set_id)
        if not set_exists:
            raise HTTPError(404, "Set {} not found".format(set_id))

        asset_exists = yield Asset.exists(repository, asset_id)
        if not asset_exists:
            raise HTTPError(404, "Asset {} not found".format(asset_id))

        res = yield Set.has_element(repository, set_id, asset_id)

        self.finish({'status': 200, 'data': {"is_member": res}})

    @gen.coroutine
    def post(self, repository_id, set_id, asset_id):
        """
        Create the link between an element and a set.

        :param repository_id: the id of the repository
        :param set_id: the id of an offer
        :return: A JSON object containing an offer
        """
        repository = DatabaseConnection(repository_id)

        set_exists = yield Set.exists(repository, set_id)
        if not set_exists:
            raise HTTPError(404, "Set {} not found".format(set_id))

        asset_exists = yield Asset.exists(repository, asset_id)
        if not asset_exists:
            raise HTTPError(404, "Asset {} not found".format(asset_id))

        yield Set.append_elements(repository, set_id, [asset_id])

        self.finish({'status': 200})

    @gen.coroutine
    def delete(self, repository_id, set_id, asset_id):
        """
        Create the link between an element and a set.

        :param repository_id: the id of the repository
        :param set_id: the id of an offer
        :return: A JSON object containing an offer
        """
        repository = DatabaseConnection(repository_id)

        set_exists = yield Set.exists(repository, set_id)
        if not set_exists:
            raise HTTPError(404, "Set {} not found".format(set_id))

        asset_exists = yield Asset.exists(repository, asset_id)
        if not asset_exists:
            raise HTTPError(404, "Asset {} not found".format(asset_id))

        yield Set.remove_elements(repository, set_id, [asset_id])

        self.finish({'status': 200})
