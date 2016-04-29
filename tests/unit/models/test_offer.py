# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

import rdflib
from StringIO import StringIO

from mock import Mock, patch
from koi.test_helpers import make_future, gen_test

from repository.models.offer import Offer, solve_ns

from .util import TEST_NAMESPACE, create_mockdb


@gen_test
def test_retrieve_retrieve_offers_for_assets_empty_list():
    db = create_mockdb()
    result = yield Offer.retrieve_for_assets([], db)
    assert result == []


@patch('repository.models.offer.Offer._process')
@gen_test
def test_retrieve_retrieve_offers_for_assets_one_item(_process):
    expected = {'nice': 123}
    db = create_mockdb()
    db.query.return_value = make_future(Mock(buffer=None))
    _process.return_value = make_future(expected)

    result = yield Offer.retrieve_for_assets([{'source_id_type': 'chub', 'source_id': 'id0'}], db)

    assert result == expected


def test_parse_row_chub_id():
    class Repo:
        repository_id = "ee60514047"
    row = {'ids': 'a11beee1110', 'entity_id_bundle': 'http://ns/hub/hub_key'+'#'+'a11beee1110', 'policies': '0ffe31|0ffe32|0ffe33'}
    expected = {
        'entity_id': 'a11beee1110',
        'source_id': 'a11beee1110',
        'source_id_type': 'hub_key',
        'policies_ids': ['0ffe31', '0ffe32', '0ffe33']
    }
    assert Offer._parse_row(Repo, row) == expected


def test_parse_row_other_id():
    class Repo:
        repository_id = "ee60514047"
    id_type = 'id_type1'
    row = {
        'ids': 'a11beee1110',
        'entity_id_bundle': id_type+'#'+'id_value1',
        'policies': '0ffe31|0ffe32|0ffe33'
    }
    expected = {
        'entity_id': 'a11beee1110',
        'source_id': 'id_value1',
        'source_id_type': id_type,
        'policies_ids': ['0ffe31', '0ffe32', '0ffe33']
    }
    assert Offer._parse_row(Repo, row) == expected


@patch('repository.models.offer.Offer.retrieve')
@gen_test
def test_process_chub_id_type(retrieve):
    db = create_mockdb()

    retrieve.side_effect = lambda rid, oid: make_future({'entity_id': oid, 'repository_id': rid.repository_id})
    csv_buffer = StringIO('\n'.join([
        'entity_id_bundle,ids,policies',
        'http://ns/id/hub_key#a11beee1110,a11beee1110,0ffe31|0ffe32',
        'http://ns/id/hub_key#a11beee2220,a11beee2220,0ffe31|0ffe33'
    ]))

    expected = [
        {'entity_id': 'a11beee1110',
         'source_id': 'a11beee1110',
         'source_id_type': 'hub_key',
         'offers': [
             {'repository_id': TEST_NAMESPACE, 'entity_id': '0ffe31'},
             {'repository_id': TEST_NAMESPACE, 'entity_id': '0ffe32'}
         ]},
        {'entity_id': 'a11beee2220',
         'source_id': 'a11beee2220',
         'source_id_type': 'hub_key',
         'offers': [
             {'repository_id': TEST_NAMESPACE, 'entity_id': '0ffe31'},
             {'repository_id': TEST_NAMESPACE, 'entity_id': '0ffe33'}
         ]},
    ]

    result = yield Offer._process(db, csv_buffer)

    assert len(result) == len(expected)
    assert result[0] in expected
    assert result[1] in expected


@patch('repository.models.offer.Offer.retrieve')
@gen_test
def test_process_other_id_type(retrieve):
    db = create_mockdb()
    retrieve.side_effect = lambda rid, oid: make_future({'id': oid, 'rid': rid.repository_id})

    csv_buffer = StringIO('\n'.join([
        'ids,entity_id_bundle,policies',
        'a11beee1110,http://ns/hub/other_id#other_id1,0ffe31|0ffe32',
        'a11beee2220,http://ns/hub/other_id#other_id2,0ffe31|0ffe33'
    ]))
    expected = [
        {'entity_id': 'a11beee1110',
         'source_id': 'other_id1',
         'source_id_type': 'other_id',
         'offers': [
             {'rid': TEST_NAMESPACE, 'id': '0ffe31'},
             {'rid': TEST_NAMESPACE, 'id': '0ffe32'}
         ]},
        {'entity_id': 'a11beee2220',
         'source_id': 'other_id2',
         'source_id_type': 'other_id',
         'offers': [
             {'rid': TEST_NAMESPACE, 'id': '0ffe31'},
             {'rid': TEST_NAMESPACE, 'id': '0ffe33'}
         ]},
    ]
    result = yield Offer._process(db, csv_buffer)
    assert (result) == (expected)



@gen_test
def test_expired():
    db = create_mockdb()

    db.query.return_value = make_future(
        Mock(body='{"boolean": true}'))

    result = yield Offer.expired(db, '0ffe31', 'timestamp')
    assert result is True


@gen_test
def test_expire():
    db = create_mockdb()
    db.update.return_value = make_future(None)
    yield Offer.expire(db, '0ffe31', 'timestamp')

    assert db.update.call_count == 1



@gen_test
def test_create():
    db = create_mockdb()
    db.store.return_value = make_future(None)

    content_type = 'text/turtle'
    yield Offer.store(db, 'data', content_type=content_type)
    db.store.assert_called_once_with('data', content_type=content_type)

def test_solve_ns():
    assert(solve_ns("rdf:type") == rdflib.URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"))
