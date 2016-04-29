# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

"""Handlers for agreements"""
import json
from koi.base import HTTPError
from tornado.gen import coroutine


from .base import RepoBaseHandler
from ..models.asset import Asset
from ..models.agreement import Agreement
from ..models.framework.helper import ValidationException
from ..models.framework.db import DatabaseConnection


class AgreementsHandler(RepoBaseHandler):
    """Handler to create agreement"""
    @coroutine
    def post(self, repository_id):
        """
        Transform an offer into an agreement

        :param repository_id: id of repository/namespace
        :param offer_id: the id of an offer
        :return: A JSON object containing an offer_id and its expiry
        """
        data = self.get_json_body(['offer_id', 'party_id'])
        offer_id = data.get('offer_id')
        party_id = data.get('party_id')
        asset_ids = data.get('asset_ids')
        metadata = data.get('metadata')
        if metadata and isinstance(metadata, basestring):
            try:
                metadata = json.loads(metadata)
            except:
                raise ValidationException("Invalid metadata - could not be parsed : %r"%(metadata,))

        agreement_id, assets_covered = yield Agreement.new_agreement(
            DatabaseConnection(repository_id),
            offer_id,
            asset_ids,
            metadata=metadata,
            organisation_id=self.on_behalf_of,
            on_behalf_of=party_id)

        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        self.finish({'status': 200, 'data': {'id': agreement_id, "assets": assets_covered}})


class AgreementHandler(RepoBaseHandler):
    """Handler for an individual agreement"""

    @coroutine
    def get(self, repository_id, agreement_id):
        """
        Retrieve an agreement

        :param repository_id: the repository's ID
        :param agreement_id: the agreement's ID
        """
        db = DatabaseConnection(repository_id)
        obj = yield Agreement.retrieve(db, agreement_id)

        if not obj:
            raise HTTPError(404, "Agreement {} not found".format(agreement_id))

        self.finish({'status': 200, 'data': obj})


class AgreementCoverageHandler(RepoBaseHandler):
    @coroutine
    def get(self, repository_id, agreement_id):
        """
        validate assets are covered by an agreement

        :param repository_id: the repository's ID
        :param agreement_id: the agreement's ID
        """
        repository = DatabaseConnection(repository_id)

        asset_ids = self.get_argument('asset_ids').split(',')
        asset_ids = [Asset.normalise_id(x)[3:] for x in asset_ids]

        validated = yield Agreement.validate_assets(
            repository,
            agreement_id,
            asset_ids,
            require_all=False)

        covered = list(set(validated).intersection(set(asset_ids)))
        self.finish({'status': 200, 'data': {'covered_by_agreement': covered}})
