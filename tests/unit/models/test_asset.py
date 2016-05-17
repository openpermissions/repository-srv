# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.


from __future__ import unicode_literals
import json
from functools import partial
from datetime import datetime
from StringIO import StringIO
import uuid
import os
from mock import patch, Mock
from tornado.ioloop import IOLoop
from koi.test_helpers import gen_test, make_future
from repository.models.asset import store, send_notification
from repository.models import asset
from repository.models.framework.db import DatabaseConnection

from .util import create_mockdb


ASSET_TEMPLATE = """
_:Id1_d435a6cdd786300dff204ee7c2ef942d3e9034e2_N28_ad0d7ec34e9135c60ece82d3d231d0e0c75a6a46_N30 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://openpermissions.org/ns/op/1.0/Id> .
<{hub_key}> <http://openpermissions.org/ns/opex/0.1/distributedBy> <https://openpermissions.org/s0/hub1/party/pid/testco> .
_:Id1_8f21840a222b74b97016b6a91781ac43414356d7_N33_8707c18164e538ad0dbbea652968661c2f7f9b0d_N32 <http://openpermissions.org/ns/op/1.0/value> "e48e2bb8-bda5-424e-885d-c2ffec1fe887" .
<{hub_key}> <http://openpermissions.org/ns/op/1.0/description> "Deer" .
<https://openpermissions.org/s0/hub1/party/rightsourceid/RightSource1> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://openpermissions.org/ns/op/1.0/Party> .
_:Id1_d435a6cdd786300dff204ee7c2ef942d3e9034e2_N28_ad0d7ec34e9135c60ece82d3d231d0e0c75a6a46_N30 <http://openpermissions.org/ns/op/1.0/value> "23" .
<{hub_key}> <http://openpermissions.org/ns/op/1.0/alsoIdentifiedBy> _:Id1_d435a6cdd786300dff204ee7c2ef942d3e9034e2_N28_ad0d7ec34e9135c60ece82d3d231d0e0c75a6a46_N30 .
<https://openpermissions.org/s0/hub1/right/bapla/hk/12> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://openpermissions.org/ns/op/1.0/Policy> .
<{hub_key}> <http://openpermissions.org/ns/opex/0.1/explicitOffer> <https://openpermissions.org/s0/hub1/right/bapla/hk/11> .
<{hub_key}> <http://openpermissions.org/ns/op/1.0/alsoIdentifiedBy> _:Id1_8f21840a222b74b97016b6a91781ac43414356d7_N33_8707c18164e538ad0dbbea652968661c2f7f9b0d_N32 .
<{hub_key}> <http://openpermissions.org/ns/opex/0.1/suppliedBy> <https://openpermissions.org/s0/hub1/party/rightsourceid/RightSource1> .
<https://openpermissions.org/s0/hub1/right/bapla/hk/11> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://openpermissions.org/ns/op/1.0/Policy> .
_:Id1_d435a6cdd786300dff204ee7c2ef942d3e9034e2_N28_ad0d7ec34e9135c60ece82d3d231d0e0c75a6a46_N30 <http://openpermissions.org/ns/op/1.0/id_type> "testcopictureid" .
<https://openpermissions.org/s0/hub1/party/pid/testco> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://openpermissions.org/ns/op/1.0/Party> .
<{hub_key}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://openpermissions.org/ns/op/1.0/Asset> .
_:Id1_8f21840a222b74b97016b6a91781ac43414356d7_N33_8707c18164e538ad0dbbea652968661c2f7f9b0d_N32 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://openpermissions.org/ns/op/1.0/Id> .
_:Id1_8f21840a222b74b97016b6a91781ac43414356d7_N33_8707c18164e538ad0dbbea652968661c2f7f9b0d_N32 <http://openpermissions.org/ns/op/1.0/id_type> "picscoutpictureid" .
<{hub_key}> <http://openpermissions.org/ns/opex/0.1/explicitOffer> <https://openpermissions.org/s0/hub1/right/bapla/hk/12> .
"""

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), '../..', 'data')
TEST_NAMESPACE = 'c8ab01'


def get_valid_xml():
    with open(os.path.abspath(os.path.join(FIXTURE_DIR, 'sample.xml')), 'r') as fr:
        return fr.read()


def test_foo():
    hub_key = 'https://openpermissions.org/s0/hub1/asset/testco/testcopictureid/{}'.format(uuid.uuid4())
    doc = ASSET_TEMPLATE.format(hub_key=hub_key)
    results = asset.get_asset_ids(doc, 'text/rdf+n3')
    expected = [
        {u'entity_id': hub_key.split('/')[-1]}]
    assert sorted(results) == sorted(expected)


@patch('repository.models.asset.send_notification', return_value=make_future(None))
@patch('repository.models.asset.get_asset_ids', return_value=[{u'entity_id': 'fa0',
         u'source_id': u'id1',
         u'source_id_type': u'testcopictureid'}])
@gen_test
def test_store_db_called(get_asset_ids, send_notification):
    db = DatabaseConnection(TEST_NAMESPACE)
    db.store = Mock()
    db.update = Mock()
    db.store.return_value = make_future(None)
    db.update.return_value = make_future(None)
    yield db.store(get_valid_xml())

    assert db.store.call_count==1


@patch('repository.models.asset.send_notification', return_value=make_future(None))
@patch('repository.models.asset.get_asset_ids', return_value=[{u'entity_id': 'fa0',
         u'source_id': u'id1',
         u'source_id_type': u'testcopictureid'}])
@gen_test
def test_store_db_called_with_content_type(get_asset_ids, send_notification):
    db = create_mockdb()
    yield store(db, 'valid_json_data',
        content_type='application/json')
    db.store.assert_called_once_with(
        'valid_json_data',
        content_type='application/json')


@patch('repository.models.asset.send_notification', return_value=make_future(None))
@patch('repository.models.asset.get_asset_ids', return_value=[])
@patch('repository.models.asset.IOLoop')
@gen_test
def test_store_notification_sent(IOLoop, get_asset_ids, send_notification):
    db = create_mockdb()
    yield store(db, get_valid_xml())
    assert IOLoop.current().spawn_call_back.called_once_with(send_notification)


@patch('repository.models.asset.send_notification', return_value=make_future(None))
@patch('repository.models.asset.get_asset_ids', return_value=[{'entity_id':  'res'}])
@gen_test
def test_store_return_value(get_asset_ids, send_notification):
    db = create_mockdb()
    result = yield store(db, get_valid_xml())
    assert result == [{'entity_id':  'res'}]


@patch('repository.models.asset.get_token', return_value=make_future('token1234'))
@patch('repository.models.asset.API')
@patch('repository.models.asset.options')
@gen_test
def test_notification(options, API, get_token):
    db = create_mockdb()
    options.service_id = 'a test service ID'
    client = API()

    client.index.get.return_value = make_future({
        'service_name': 'Index Service',
        'service_id': 'index1234',
        'version': '0.1.0'
    })

    client.index.notifications.post.return_value = make_future(None)
    yield send_notification(db)

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    body = json.dumps({'id': db.repository_id})

    client.index.notifications.prepare_request.assert_called_with(
        request_timeout=options.request_timeout,
        headers=headers,
        body=body
    )

    assert get_token.called
    assert client.index.notifications.post.called


@patch('repository.models.asset.get_token')
@patch('repository.models.asset.logging')
@patch('repository.models.asset.API')
@patch('repository.models.asset.options')
@gen_test
def test_notification_get_token_error(options, API, logging, get_token):
    options.service_id = 'a test service ID'
    client = API()
    db = create_mockdb()
    get_token.side_effect = Exception

    yield send_notification(db)

    assert not client.index.notifications.prepare_request.called
    assert not client.index.notifications.post.called
    assert logging.exception.called


###############################################################################
# exists                                                                      #
###############################################################################
@gen_test
def test_exists_query_called():
    db = create_mockdb()
    response = Mock()
    response.body = '{"boolean":true}'
    db.query.return_value = make_future(response)
    entity_id = 'e3a2221e118'
    assert db.query.call_count == 0
    yield asset.exists(db, entity_id)
    assert db.query.call_count == 1


@gen_test
def test_exists_true():
    db = create_mockdb()
    response = Mock()
    response.body = '{"boolean":true}'
    db.query.return_value = make_future(response)
    entity_id = 'e3a2221e118'
    result = yield asset.exists(db, entity_id)
    assert result is True


@gen_test
def test_exists_false():
    db = create_mockdb()
    response = Mock()
    response.body = '{"boolean":false}'
    db.query.return_value = make_future(response)
    entity_id = 'e321111e118'
    result = yield asset.exists(db, entity_id)
    assert result is False



###############################################################################
# insert_timestamps                                                           #
###############################################################################
@gen_test
def test_insert_timestamps_no_ids():
    db = create_mockdb()
    db.update.return_value = make_future([])
    yield asset.insert_timestamps(db, [])
    assert db.update.call_count == 0


@gen_test
def test_insert_timestamps_one_id_update_called():
    db = create_mockdb()
    db.update.return_value = make_future('')
    yield asset.insert_timestamps(db, ['asset1'])
    assert db.update.call_count == 1


@gen_test
def test_insert_timestamps_multiple_ids_update_called():
    db = create_mockdb()
    db.update.return_value = make_future('')

    yield asset.insert_timestamps(db, ['asset1', 'asset2'])

    assert db.update.call_count == 1


###############################################################################
# _retrieve_paged_ids                                                         #
###############################################################################
@gen_test
def test__retrieve_paged_ids_query_contains_from_time():
    db = create_mockdb()

    response = Mock()
    response.buffer = StringIO("""<?xml version="1.0"?>
<sparql xmlns="http://www.w3.org/2005/sparql-results#"><results></results>
</sparql>""")

    db.query.return_value = make_future(response)

    yield asset.retrieve_paged_assets(
        db,
        datetime(2016, 1, 1, 0, 0, 0),
        datetime(2016, 1, 2, 0, 0, 0),
        page=1,
        page_size=1000
    )
    assert db.query.call_args[0][0].find('2016-01-01T00:00:00') >= 0


@gen_test
def test__retrieve_paged_ids_query_contains_to_time():
    db = create_mockdb()

    response = Mock()
    response.buffer = StringIO("""<?xml version="1.0"?>
<sparql xmlns="http://www.w3.org/2005/sparql-results#"><results></results>
</sparql>""")

    db.query.return_value = make_future(response)

    yield asset.retrieve_paged_assets(
        db,
        datetime(2016, 1, 1, 0, 0, 0),
        datetime(2016, 1, 2, 0, 0, 0),
        page=1,
        page_size=1000
    )
    assert db.query.call_args[0][0].find('2016-01-02T00:00:00') >= 0


@gen_test
def test__retrieve_paged_ids_query_contains_limit():
    db = create_mockdb()

    response = Mock()
    response.buffer = StringIO("""<?xml version="1.0"?>
<sparql xmlns="http://www.w3.org/2005/sparql-results#"><results></results>
</sparql>""")

    db.query.return_value = make_future(response)

    yield asset.retrieve_paged_assets(
        db,
        datetime(2016, 1, 1, 0, 0, 0),
        datetime(2016, 1, 2, 0, 0, 0),
        page=1,
        page_size=1000
    )
    assert db.query.call_args[0][0].find('LIMIT 1000') >= 0


@gen_test
def test__retrieve_paged_ids_query_contains_no_offset():
    db = create_mockdb()

    response = Mock()
    response.buffer = StringIO("""<?xml version="1.0"?>
<sparql xmlns="http://www.w3.org/2005/sparql-results#"><results></results>
</sparql>""")
    db.query.return_value = make_future(response)

    yield asset.retrieve_paged_assets(
        db,
        datetime(2016, 1, 1, 0, 0, 0),
        datetime(2016, 1, 2, 0, 0, 0),
        page=1,
        page_size=1000)
    assert db.query.call_args[0][0].find('OFFSET 0') >= 0


@gen_test
def test__retrieve_paged_ids_query_contains_offset():
    db = create_mockdb()

    response = Mock()
    response.buffer = StringIO("""<?xml version="1.0"?>
<sparql xmlns="http://www.w3.org/2005/sparql-results#"><results></results>
</sparql>""")

    db.query.return_value = make_future(response)

    yield asset.retrieve_paged_assets(
        db,
        datetime(2016, 1, 1, 0, 0, 0),
        datetime(2016, 1, 2, 0, 0, 0),
        page=10,
        page_size=2000)
    assert db.query.call_args[0][0].find('OFFSET 18000') >= 0


@gen_test
def test__retrieve_paged_ids_query_no_result():
    db = create_mockdb()

    response = Mock()
    response.buffer = StringIO("""<?xml version="1.0"?>
<sparql xmlns="http://www.w3.org/2005/sparql-results#">
  <head>
    <variable name="entity_uri"/>
    <variable name="source_id_type"/>
    <variable name="source_id"/>
    <variable name="last_modified"/>
  </head>
  <results>
  </results>
</sparql>
""")

    db.query.return_value = make_future(response)

    result = yield asset.retrieve_paged_assets(
        db,
        datetime(2016, 1, 1, 0, 0, 0),
        datetime(2016, 1, 2, 0, 0, 0),
        10,
        2000)

    assert result[0] == []



###############################################################################
# _insert_ids                                                                 #
###############################################################################
@gen_test
def test__insert_ids_no_ids():
    db = create_mockdb()
    yield asset._insert_ids(db, 'assetid1', [])
    assert not db.update.call_count >= 1


@gen_test
def test__insert_ids_one_id():
    db = create_mockdb()
    db.update.return_value = make_future('')
    yield asset._insert_ids(db, 'assetid1', [{'source_id': 'id1', 'source_id_type': 'id_type1'}])
    assert db.update.call_count == 1


@gen_test
def test__insert_ids_multiple_ids():
    db = create_mockdb()
    db.update.return_value = make_future('')
    yield asset._insert_ids(db, 'assetid1',
        [{'source_id': 'id1', 'source_id_type': 'id_type1'},
         {'source_id': 'id2', 'source_id_type': 'id_type2'}])
    assert db.update.call_count >= 1


@gen_test
def test__insert_ids_contains_id():
    db = create_mockdb()
    db.update.return_value = make_future('')
    yield asset._insert_ids(db, 'assetid1',
        [{'source_id': 'id1', 'source_id_type': 'id_type1'}])
    assert db.update.call_args[0][0].find('id1') >= 0


@gen_test
def test__insert_ids_contains_id_type():
    db = create_mockdb()
    db.update.return_value = make_future('')
    yield asset._insert_ids(db, 'assetid1', [{'source_id': 'id1', 'source_id_type': 'id_type1'}])
    assert db.update.call_args[0][0].find('id_type1') >= 0


@gen_test
def test__insert_ids_contains_assetid():
    db = create_mockdb()
    db.update.return_value = make_future('')
    entity_id = 'assetid1'
    yield asset._insert_ids(
        db,
        entity_id,
        [{'source_id': 'id1', 'source_id_type': 'id_type1'}])
    assert db.update.call_count==1
    assert db.update.call_args[0][0].find(entity_id) >= 0


@gen_test
def test_get_also_identified_id():
    db = create_mockdb()
    query_res = [('bbb', 'bb'), ('sss', 'bb')]
    expected_res = [{'source_id_type': x[0], 'source_id': x[1]} for x in query_res]
    db.query.return_value = make_future(query_res)

    with patch('repository.models.asset.Asset._parse_response') as parse_response:
        parse_response.side_effect = lambda x: x
        res = yield asset.Asset.get_also_identified_by(
            db,
            "a01230123013"
        )
    assert (res == expected_res)

@gen_test
def test__insert_ids_update_csv():
    db = create_mockdb()
    db.update.return_value = make_future('')
    yield asset._insert_ids(
        db,
        'assetid1',
        [{'source_id': 'id1', 'source_id_type': 'id_type1'}])
    assert db.update.call_args[1]['response_type'] == 'csv'


###############################################################################
# _validate_ids                                                               #
###############################################################################
def test__validate_ids_no_ids():
    func = partial(asset._validate_ids, [])
    result = IOLoop.instance().run_sync(func)
    assert not result


def test__validate_ids_no_errors():
    func = partial(
        asset._validate_ids,
        [{'source_id': 'id1', 'source_id_type': 'id_type1'}, {'source_id': 'id2', 'source_id_type': 'id_type2'}]
    )
    result = IOLoop.instance().run_sync(func)
    assert not result


def test__validate_ids_missing_id():
    result = asset._validate_ids(
        [{'source_id_type': 'id_type1'}, {'source_id': 'id2', 'source_id_type': 'id_type2'}]
    )
    assert result == ['Missing source_id for entry:1']


def test__validate_ids_missing_id_type():
    result = asset._validate_ids( [{'source_id': 'id1', 'source_id_type': 'id_type1'}, {'source_id': 'id2'}])
    assert result == ['Missing source_id_type for entry:2']


def test__validate_ids_multiple_errors():
    result = asset._validate_ids([{'source_id': 'id1'}, {'source_id_type': 'id_type1'}])
    assert result == ['Missing source_id_type for entry:1', 'Missing source_id for entry:2']


###############################################################################
# add_ids                                                                     #
###############################################################################
@patch('repository.models.asset.insert_timestamps')
@patch('repository.models.asset._insert_ids')
@gen_test
def test_insert_ids_no_ids(_insert_ids, insert_timestamps):
    db = create_mockdb()
    result = yield asset.add_ids(db, 'asset1', [])
    assert _insert_ids.call_count == 0
    assert insert_timestamps.call_count == 0
    assert not result


@patch('repository.models.asset.insert_timestamps')
@patch('repository.models.asset._insert_ids')
@gen_test
def test_insert_ids_no_errors(_insert_ids, insert_timestamps):
    db = create_mockdb()
    _insert_ids.return_value = make_future(None)
    insert_timestamps.return_value = make_future(None)

    result = yield asset.add_ids(db, 'asset1',
                                 [{'source_id': 'id1', 'source_id_type': 'id_type1'}])
    _insert_ids.assert_called_with(db, 'asset1', [{'source_id': 'id1', 'source_id_type': 'id_type1'}])
    insert_timestamps.assert_called_with(db, ['asset1'])
    assert not result


@patch('repository.models.asset.insert_timestamps')
@patch('repository.models.asset._insert_ids')
@gen_test
def test_insert_ids_errors(_insert_ids, insert_timestamps):
    db = create_mockdb()
    result = yield asset.add_ids(db, 'asset1', [{'source_id': 'id1'}])
    assert not _insert_ids.call_count >= 1
    assert not insert_timestamps.call_count >= 1
    assert result == ['Missing source_id_type for entry:1']
