# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.


import logging
import rdflib
import re
import json

from tornado import gen

from .framework.entity import build_uuid_reference
from .queries.policy import (
    OFFER_CLASS,
    OFFER_EXPIRE_PREDICATE,
    POLICY_ASSIGNER,
    OFFER_LIST_EXTRA_IDS,
    OFFER_LIST_EXTRA_QUERY
)
from .queries.generic import (PREFIXES, SPARQL_PREFIXES)
from .framework.helper import solve_ns, future_wrap, ValidationException
from .policy import Policy
from .party import Party


class Offer(Policy):
    CLASS = OFFER_CLASS
    LIST_EXTRA_IDS = OFFER_LIST_EXTRA_IDS
    LIST_EXTRA_QUERY = OFFER_LIST_EXTRA_QUERY

    @classmethod
    def normalise_id(cls, entity_id):
        """
        Ensure offer ids have the right form.

        :param entity_id: The entity_id of the offer either in the form of an IRI, either as an id
        :returns: an id normalised usable in SPARQL queries
        """
        if entity_id.startswith(PREFIXES['id']):
            entity_id = entity_id[len(PREFIXES['id']):]
        entity_id = entity_id.lower()
        if not re.match("id:([0-9a-f]{1,64})", entity_id):
            return build_uuid_reference(entity_id)
        return entity_id

    @classmethod
    @gen.coroutine
    def expired(cls, repository, offer_id, timestamp):
        """
        Find if the Offer expires before the given timestamp

        :param repository_id: id of repository/namespace
        :param offer_id: the id of an offer
        :param timestamp : a given timestamp
        :return: True or False
        """
        result = yield cls.match_attr(repository, offer_id, OFFER_EXPIRE_PREDICATE,
                                      cls.timerange_constraint("o", None, timestamp))

        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def expire(cls, repository, offer_id, expiry_date):
        """
        Expire an offer

        :param repository_id: id of repository/namespace
        :param offer_id: the id of an offer
        :param expiry_date: new expiry date
        """
        if not isinstance(expiry_date, basestring):
            expiry_date = expiry_date.isoformat()

        logging.info('Setting Offer "{}" to expire at {}'
                     .format(offer_id, expiry_date))

        yield cls.set_attr(
            repository,
            offer_id,
            OFFER_EXPIRE_PREDICATE,
            expiry_date,
            "xsd:dateTime")

    @classmethod
    @gen.coroutine
    def new_offer(cls, repository, offer, assigner, format="xml"):
        """
        Create a new offer.

        :param repository: The database where we read the offer and create the agreement in
        :param offer: the text of the offer
        :param assigner: the assigner of the offer
        :param format: serialisation format of the offer
        """
        kwargs = {}
        g = rdflib.Graph()
        if format == "json-ld":
            try:
                offerj = json.loads(offer)
            except ValueError, e:
                raise ValidationException("Unable to parse offer data:" + str(e, ))

            if '@graph' in offerj:
                offer = json.dumps(offerj['@graph'])
                kwargs['context'] = offerj.get('@context', {})
        try:
            g.parse(data=offer, format=format, **kwargs)
        except ValueError, e:
            raise ValidationException("Unable to parse offer data:" + str(e, ))

        query = SPARQL_PREFIXES + "\nSELECT ?license_id WHERE {\n ?license_id a %s .\n}" % (cls.CLASS,)
        results = list(g.query(query))
        if len(results) != 1:
            raise ValidationException("Invalid number of offers submitted")
        initial_offer_id = results[0][0]
        logging.info("Found offer %s" % (initial_offer_id,))
        ng = cls._copy_graph(g, initial_offer_id)

        # find policy
        results = list(ng.query(query))
        offer_id = results[0][0]

        # set assigner
        party = yield Party.new_party(future_wrap(ng), assigner)
        yield cls.set_attr(future_wrap(ng), offer_id, POLICY_ASSIGNER,  solve_ns(Party.normalise_id(party)))

        rdfxml = ng.serialize()
        yield cls.store(repository, rdfxml)
        logging.info("Created offer {}".format(offer_id))
        raise gen.Return(str(offer_id).split('/')[-1])
