# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.


import datetime
import logging
import rdflib

from tornado.gen import Return, coroutine

from .framework.helper import isoformat
from .framework.helper import future_wrap, solve_ns, ValidationException
from .queries.generic import SPARQL_PREFIXES
from .queries.policy import AGREEMENT_CLASS, POLICY_TARGET, POLICY_ASSIGNEE

from .offer import Offer
from .party import Party
from .policy import Policy


class Agreement(Policy):
    CLASS = AGREEMENT_CLASS

    @classmethod
    @coroutine
    def new_agreement(cls, repository, offer_id,  asset_ids=None,
                      metadata=None, organisation_id=None, on_behalf_of=None):
        """
        Create an agreement for a specified offer.

        :param repository: The database where we read the offer and create the agreement in
        :param offer_id: The offer id that is to be transformed into an agreement
        :param asset_ids: The list of assets the person wants to accept in the offer
        :param metadata: Other metadata indicating the value of the constraints
        """
        if asset_ids is None:
            asset_ids = []

        exists = yield Offer.exists(repository, offer_id)
        if not exists:
            raise ValidationException('Offer "{}" does not exist'
                                      .format(offer_id))

        # perform deep copy by changing all internal ids
        ng = yield Offer.retrieve_copy(repository, offer_id)

        # find policy
        query = SPARQL_PREFIXES + "\nSELECT ?license_id WHERE {\n ?license_id a %s .\n}" % (Offer.CLASS,)
        agreement_id = list(ng.query(query))[0][0]

        # change policy type
        ng.remove((agreement_id, rdflib.RDF.type, solve_ns(Offer.CLASS)))
        ng.add((agreement_id, rdflib.RDF.type, solve_ns(cls.CLASS)))

        #  set agreement date

        yield cls.set_attr(future_wrap(ng), agreement_id, "dcterm:dateAccepted",
                           isoformat(datetime.datetime.utcnow()), "xsd:dateTime", update_last_modified=True)


        # link agreement to offer
        ng.add((agreement_id, solve_ns("dcterm:references"), solve_ns(cls.normalise_id(offer_id))))

        assets_covered = yield cls.validate_assets(repository, offer_id, asset_ids)

        if not len(assets_covered):
            raise ValidationException("You haven't selected any asset")

        normalised = [solve_ns(cls.normalise_id(x)) for x in assets_covered]
        yield cls.set_attr(future_wrap(ng), agreement_id, POLICY_TARGET, normalised, update_last_modified=False)

        # set other agreement metadata
        if metadata:
            yield cls.update_metadata(future_wrap(ng), agreement_id, metadata, update_last_modified=False)

        # set assignee
        party_id = yield Party.new_party(future_wrap(ng), organisation_id, on_behalf_of)
        ng.add((agreement_id, solve_ns(POLICY_ASSIGNEE), solve_ns(Party.normalise_id(party_id))))

        # write agreement
        yield repository.store(ng.serialize(format="xml"), content_type="application/xml")
        logging.info("Created agreement {}".format(agreement_id))
        raise Return((str(agreement_id).split('/')[-1], [str(a).split('/')[-1] for a in assets_covered]))
