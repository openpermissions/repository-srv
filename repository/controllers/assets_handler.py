# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

"""
API assets handler. Stores data in database.
"""
import logging

import arrow
from arrow.parser import ParserError
from koi.exceptions import HTTPError
from tornado import gen
from tornado.options import options
from urllib import urlencode
from urlparse import urlunsplit

from .base import RepoBaseHandler
from .. import audit
from ..models import asset
from ..models.offer import Offer
from ..models.framework import helper
from ..models.framework.db import DatabaseConnection


def _validate_body(request):
    if request.body is None:
        raise HTTPError(400, "No Data in Body")
    if request.body == '':
        raise HTTPError(400, "Body is empty string")


def _unique_ids(body):
    ids = []
    for item in body:
        if item not in ids:
            ids.append(item)
    return ids


class IdentifiersHandler(RepoBaseHandler):
    """Responsible for returning ids of assets within time range"""

    def _get_time_arguments(self):
        """
        Get from_time and to_time from handler args and parse into valid format

        :return: (from_time, to_time)
        """
        from_time = self.get_argument('from', None)
        to_time = self.get_argument('to', None)

        # parse the value or get default value if parameter not specified
        now = arrow.utcnow()  # todo: why is the in the handler?
        try:
            if from_time is None:
                from_time = now.replace(days=-1)
            else:
                from_time = arrow.get(from_time)

            if to_time is None:
                to_time = now.replace(days=+1)
            else:
                to_time = arrow.get(to_time)
        except ParserError:
            raise HTTPError(400, "Invalid format")
        except (OverflowError, ValueError):
            raise HTTPError(400, "Date out of range")

        return from_time, to_time

    def _get_page_arguments(self):
        """
        Get page and paze_size arguments from handler and validate

        :return: (page, page_size)
        """
        try:
            page = int(self.get_argument('page', 1))
        except ValueError:
            raise HTTPError(400, "Invalid page")

        if page < 1:
            raise HTTPError(400, 'page must be >= 1')

        try:
            page_size = int(self.get_argument('page_size', 1000))
        except ValueError:
            raise HTTPError(400, "Invalid page_size")

        if page_size < 0 or page_size > options.max_page_size:
            raise HTTPError(
                400,
                'page_size must be between 0 and {}'.format(options.max_page_size))

        return page, page_size

    @gen.coroutine
    def get(self, repository_id):
        """
        Respond with JSON containing success or error message.

        :param repository_id: str
        """
        ids = None
        result_range = None
        from_time, to_time = self._get_time_arguments()
        page, page_size = self._get_page_arguments()
        status = 200

        # fetch the identifiers
        try:
            ids, result_range = yield asset.retrieve_paged_assets(
                DatabaseConnection(repository_id),
                from_time,
                to_time,
                page=page,
                page_size=page_size)
        except Exception:
            status = 500
            logging.exception("Error while retrieving ids from database")

        result = {
            'status': status,
            'data': ids,
            'metadata': {
                'service_id': options.service_id,
                'result_range': result_range,
                'query_range': (from_time.isoformat(), to_time.isoformat()),
            }
        }

        if ids:
            next_page = urlunsplit((
                self.request.protocol,
                self.request.host,
                self.request.path,
                urlencode({
                    'page_size': page_size,
                    'page': page + 1,
                    'from': result_range[1],
                    'to': to_time.isoformat()
                }),
                ''
            ))
            result['metadata']['next'] = next_page

        self.finish(result)


class AssetsHandler(RepoBaseHandler):
    """Responsible for storing assets for a repository in database"""
    @gen.coroutine
    def post(self, repository_id):
        """
        Respond with JSON containing success or error message.

        :param repository_id: str
        """
        _validate_body(self.request)
        helper.validate(self.request.body, format=self.data_format())

        assets_data = yield asset.store(
            DatabaseConnection(repository_id),
            self.request.body,
            self.get_content_type())

        audit.log_added_assets(
            assets_data,
            self.token,
            repository_id=repository_id)

        self.finish({'status': 200})


class AssetHandler(RepoBaseHandler):
    """Handler for individual assets"""

    @gen.coroutine
    def get(self, repository_id, asset_id):
        """
        Retrieve one asset by asset_id

        :param repository_id: the id of the repository
        :param asset_id: the id of an asset
        :return: A JSON object containing an asset
        """
        db = DatabaseConnection(repository_id)
        asset_obj = yield asset.Asset.retrieve(db, asset_id)

        if not asset_obj:
            raise HTTPError(404, "asset {} not found".format(asset_id))

        self.finish({'status': 200, 'data': asset_obj})


class AssetIDHandler(RepoBaseHandler):
    """Responsible for storing asset ids in database"""

    @gen.coroutine
    def post(self, repository_id, entity_id):
        """Respond with JSON containing success or error message."""
        exists = yield asset.exists(DatabaseConnection(repository_id), entity_id)

        if not exists:
            raise HTTPError(404, 'Asset "{}" does not exist '.format(entity_id))

        data = self.get_json_body(required=['ids'])
        errors = yield asset.add_ids(DatabaseConnection(repository_id), entity_id, data['ids'])

        if len(errors) > 0:
            raise HTTPError(400, errors)
        else:
            audit.log_asset_ids(entity_id, data['ids'], self.token)
            self.finish({'status': 200})

    @gen.coroutine
    def get(self, repository_id, entity_id):
        """Respond with JSON with source_id and source_id_type for entity."""
        dbc = DatabaseConnection(repository_id)
        exists = yield asset.exists(dbc, entity_id)
        if not exists:
            raise HTTPError(404, 'Asset "{}" does not exist '.format(entity_id))

        result = yield asset.Asset.get_also_identified_by(dbc, entity_id)

        self.finish({'status': 200, 'data': result})

class BulkOfferHandler(RepoBaseHandler):
    """Handler for offers"""

    METHOD_ACCESS = {
        "POST": RepoBaseHandler.READ_ACCESS,
        "OPTIONS": RepoBaseHandler.READ_ACCESS
    }

    @gen.coroutine
    def post(self, repository_id):
        """
        Retrieve offers by bulk

        :param repository_id: str
        """
        body = _unique_ids(self.get_json_body())
        try:
            result = yield Offer.retrieve_for_assets(body, DatabaseConnection(repository_id))
        except KeyError as error:
            logging.info(error.message)
            raise HTTPError(400, "Invalid object in post body")

        self.finish({'status': 200, 'data': result})
