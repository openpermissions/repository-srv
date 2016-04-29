# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.


import csv
import json
import logging
import re
import urllib

from tornado.gen import Return, coroutine


from .framework.helper import solve_ns, ValidationException
from .framework.entity import Entity, build_uuid_reference

from .queries.policy import (
    POLICY_STRUCT_SELECT,
    OFFER_CLASS,
    POLICY_METADATA_ATTRIBUTE_MAP,
    ASSET_SELECTOR_CLASS,
    GET_POLICY_TARGETS
)

from .queries.generic import PREFIXES, SPARQL_PREFIXES
from .queries.asset import ASSET_GET_POLICIES_FOR_ASSETS, ASSET_CLASS

from .set import Set
from . import asset


class Policy(Entity):
    CLASS = OFFER_CLASS
    GET_POLICIES_FOR_ASSETS = ASSET_GET_POLICIES_FOR_ASSETS
    STRUCT_SELECT = POLICY_STRUCT_SELECT

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

    @staticmethod
    def _parse_row(cdb, row):
        """
        parse a row from the query result.
        :param row: a dictionary representing a row
        :return: a dictionary with a unified format for all id types with the
        following keys id, source_id, source_id_type, offer_ids.
        """
        row = {k: v.decode('utf-8') for k, v in row.iteritems()}
        # return only one HK if multiple HK
        entity_id = str(row['ids']).split('|')[0]
        source_id_type, source_id = row['entity_id_bundle'].split('#')
        source_id_type = source_id_type.split('/')[-1]

        entity_id = str(entity_id).split('/')[-1]
        result = {
            'entity_id': entity_id,
            'source_id': urllib.unquote_plus(source_id),
            'source_id_type': urllib.unquote_plus(source_id_type),
            'policies_ids': row['policies'].split('|')
        }

        return result

    @classmethod
    @coroutine
    def _process(cls, cdb, csv_buffer):
        """
        Attach license objects to asset data
        :param cdb: db containing the licenses
        :param csv_buffer: CSV reply containing policies for the assets queried
        :param assets: return asset associated with policies
        """
        assets = [cls._parse_row(cdb, row) for row in csv.DictReader(csv_buffer)]
        policy_ids = {offer_id for item in assets for offer_id in item['policies_ids']}

        # retrieve from db
        policies = yield {oid: cls.retrieve(cdb, oid) for oid in policy_ids}

        # replacing offer ids with actual offer
        for casset in assets:
            oids = casset.pop('policies_ids')
            casset[cls.__name__.lower()+'s'] = [policies[oid] for oid in oids]

        raise Return(assets)

    @classmethod
    @coroutine
    def retrieve_for_assets(cls, asset_ids, repository):
        """
        Retrieve offers by id and type of the id
        :param asset_ids: a list of id_types,ids for the assets
        :param repository: repository name (namespace in db)
        :return: list of offers for the asset
        """
        if not asset_ids:
            logging.warning('bulk query with no data')
            raise Return([])

        logging.debug("query : %r" % (asset_ids,))
        subquery = asset.Asset.asset_subselect_idlist(asset_ids)

        query = SPARQL_PREFIXES
        query += cls.GET_POLICIES_FOR_ASSETS.format(idname="entity", subquery=subquery, policy_type=cls.CLASS)
        rsp = yield repository.query(payload=query, response_type='csv')

        result = yield cls._process(repository, rsp.buffer)

        raise Return(result)

    @classmethod
    @coroutine
    def update_metadata(cls, repository, agreement_id, metadata, update_last_modified):
        ulm = update_last_modified
        for m in metadata.items():
            if m[0] not in POLICY_METADATA_ATTRIBUTE_MAP:
                raise ValidationException("Invalid metadata provided {}".format(m[0]))
            selector = POLICY_METADATA_ATTRIBUTE_MAP[m[0]]
            yield cls.set_attr(repository, agreement_id, selector["query"], m[1], "xsd::string", selector["filters"],
                               update_last_modified=ulm
                               )
            ulm = False

    @classmethod
    @coroutine
    def get_targets(cls, repository, entity_id):
        """
        Get target's from an entity's policy

        :param graph: an in-memory rdflib graph or DatabaseConnection
        :param entity_id: the policy's ID
        :returns: rdflib graph
        """
        rsp = yield repository.query(GET_POLICY_TARGETS.format(id=entity_id),
                                     response_type='json')

        results = json.loads(rsp.body)['results']['bindings']
        targets = [
                    {
                        'type': x['type']['value'],
                        'id': x['target']['value'].split('/')[-1],
                        'set_id': x.get('set_id', {}).get('value'),
                        'max_items': int(x.get('max_items', {}).get('value') or 1),
                        'sel_required': bool(x.get('sel_required', {}).get('value', False))
                    }
                    for x in results
                  ]

        raise Return(targets)

    @classmethod
    @coroutine
    def validate_assets(cls, repository, entity_id, asset_ids,
                        explicit=False, require_all=True):
        """
        Validates that a list of assets are permitted for a policy

        :param repository: a DatabaseConnection
        :param entity_id: the offer or agreement's ID
        :param asset_ids: the requested assets
        :param explicit: (optional) whether all targets specified in a policy
            must be explicitly selected in asset_ids
        :param require_all: (optional) raise a validation exception if
            some assets are not included in the policy
        :returns: validated list of asset IDs
        """
        targets = yield cls.get_targets(repository, entity_id)

        if not targets:
            raise ValidationException('Invalid policy - No default target')

        valid_assets = set([])
        asset_ids = set(asset_ids)
        for target in targets:
            target_id = target['id']
            if str(solve_ns(ASSET_SELECTOR_CLASS)) == target['type']:
                matched_ids = yield cls.validate_asset_in_selector(
                    repository,
                    target_id,
                    target['set_id'],
                    asset_ids,
                    max_items=target['max_items'])

                if target['sel_required']:
                    valid_assets.update(matched_ids)
                else:
                    valid_assets.update(set([target_id]))
                    asset_ids = asset_ids.difference(matched_ids)

                if asset_ids == valid_assets:
                    # no point looking at the remaining selectors if all of
                    # the assets are already validated
                    break
            elif str(solve_ns(ASSET_CLASS)) == target['type']:
                if explicit and asset_ids and target_id not in asset_ids:
                    msg = 'The policy requires you to accept {}'
                    raise ValidationException(msg.format(target_id))

                # NOTE: even if a user didn't ask for an asset, it's included
                # in the policy
                valid_assets.add(target_id)
            else:
                logging.warning("Policy's target has an unexpected type: %s",
                                target['type'])
                # ignore unexpected targets
                continue

        missing = set(asset_ids).difference(set(valid_assets))
        if missing and require_all:
            msg = 'Assets ({}) are not covered by this policy'
            raise ValidationException(msg.format(','.join(missing)))

        raise Return(list(valid_assets))

    @classmethod
    @coroutine
    def validate_asset_in_selector(cls, repository, target_id, set_id, assets,
                                   max_items=1):
        ids = set([])
        if set_id is None:
            raise Return(ids)

        if not assets:
            raise ValidationException('This policy requires you to enumerate '
                                      'the elements you want to accept')

        for cid in assets:
            present = yield Set.has_element(repository, set_id, cid)
            if present:
                ids.add(cid.split('/')[-1])

        # NOTE: we currently assume that offer do not provide access to union
        # of overlapping offer sets if this was the the case the previous
        # filter would be greedy, and it may be required to find how to
        # allocate the assets to the selectors...
        if len(ids) > max_items:
            raise ValidationException('This policy requires you to pick at most %d elements from %s')

        raise Return(ids)
