# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.


"""API assets handler. Query offers from the db."""
import arrow
from arrow.parser import ParserError
from koi.base import HTTPError
from tornado import gen

from .base import RepoBaseHandler
from .. import audit
from ..models.offer import Offer
from ..models.framework.db import DatabaseConnection


class OfferHandler(RepoBaseHandler):
    """Handler for individual offers"""

    @gen.coroutine
    def get(self, repository_id, offer_id):
        """
        Retrieve one offer by offer_id

        :param repository_id: the id of the repository
        :param offer_id: the id of an offer
        :return: A JSON object containing an offer
        """
        offer_obj = yield Offer.retrieve(DatabaseConnection(repository_id), offer_id)

        if not offer_obj:
            raise HTTPError(404, "offer {} not found".format(offer_id))

        self.finish({'status': 200, 'data': offer_obj})

    @staticmethod
    @gen.coroutine
    def _validate_offer_expiry(dbconn, offer_id, expires):
        """
        Check offer is not expired and that expires is a valid date

        :param repository_id: id of repository/namespace
        :param offer_id: id of offer
        :param expires: datetime
        """
        if isinstance(dbconn, basestring):
            dbconn = DatabaseConnection(dbconn)
        try:
            arrow.get(expires)
        except ParserError:
            raise HTTPError(400, "Invalid expires")

        now = arrow.utcnow().isoformat()
        expired = yield Offer.expired(dbconn, offer_id, now)
        if expired:
            raise HTTPError(400, "Already expired")

    @gen.coroutine
    def put(self, repository_id, offer_id):
        """
        Update when an offer should expire

        :param repository_id: id of repository/namespace
        :param offer_id: the id of an offer
        :return: A JSON object containing an offer_id and its expiry
        """
        data = self.get_json_body()
        expires = data['expires']

        repository = DatabaseConnection(repository_id)
        yield self._validate_offer_expiry(repository, offer_id, expires)
        yield Offer.expire(repository, offer_id, expires)
        audit.log_update_offer_expiry(self.client_organisation, offer_id, expires)

        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        self.finish({'status': 200, 'data': {'id': offer_id, 'expires': expires}})


class OffersHandler(RepoBaseHandler):
    """Handler for offers"""

    @gen.coroutine
    def get(self, repository_id):
        page = int(self.get_argument("page", "1"))
        page_size = int(self.get_argument("page_size", "20"))
        page_size = min(page_size, 1000)

        repository = DatabaseConnection(repository_id)

        offers = yield Offer._retrieve_paged_ids([], page=page, page_size=page_size, repository=repository)
        offers = [{'id': str(o[0]).split('/')[-1], 'title':o[1], 'last_modified': o[2]} for o in offers]
        self.finish({'status': 200, 'data': {'offers': offers}})

    @gen.coroutine
    def post(self, repository_id):
        """
        Create one offer. If the data contains an expires key, then that
        is the id of an offer that should be replaced with the new one.

        :param repository_id: str
        """
        offer_id = yield Offer.new_offer(
            DatabaseConnection(repository_id),
            self.request.body,
            format=self.data_format(),
            organisation_id=self.on_behalf_of,
            on_behalf_of="")

        errors = []
        if errors:
            raise HTTPError(400, errors)
        else:
            audit.log_added_offer(self.client_organisation, offer_id)
            self.set_header('Content-Type', 'application/json; charset=UTF-8')
            self.finish({'status': 200, 'data': {'id': offer_id}})
