# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.


import uuid
import re
from queries.generic import PREFIXES, TURTLE_PREFIXES
from tornado.gen import coroutine, Return

from .framework.entity import (Entity, build_sparql_str, build_uuid_reference)
from .queries.party import PARTY_TEMPLATE

class Party(Entity):
    CLASS = "op:Party"

    @classmethod
    def normalise_id(cls, entity_id):
        """
        Ensure offer ids have the right form.

        :param entity_id: The entity_id of the offer either in the form of an IRI, either as an id
        :returns: an id normalised usable in SPARQL queries
        """
        if entity_id.startswith(PREFIXES['id']):
            entity_id = entity_id[len(PREFIXES['id']):]
        entity_id=entity_id.lower()
        if not re.match("id:([0-9a-f]{1,64})", entity_id):
            return build_uuid_reference(entity_id)
        return entity_id


    @classmethod
    @coroutine
    def new_party(cls, repository, provider):
        """
        Instantiate a party with following attributes
        """
        new_id = str(uuid.uuid4()).replace('-', '')
        party = PARTY_TEMPLATE.format(id="id:"+new_id,
                                      class_=cls.CLASS,
                                      provider=build_sparql_str(provider)
                                      )
        party=TURTLE_PREFIXES + party
        if hasattr(repository, "parse"):
            yield repository.parse(data=party, format="turtle")
        else:
            yield repository.store(party, content_type="application/x-turtle")
        raise Return(new_id)
