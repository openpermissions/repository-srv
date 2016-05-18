# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

import rdflib
from mock import patch
from koi.test_helpers import make_future, gen_test
from repository.models.set import Set
from .util import create_mockdb


@gen_test
def test_set_new_set():
    db = create_mockdb()
    r = yield Set.new_set(db)
    assert len(r)
    assert db.store.call_count == 1

@gen_test
def test_set_has_element():
    db = create_mockdb()

    class mocked_rep:
        body = "{\"boolean\": false}"

    db.query.return_value = make_future(mocked_rep)

    r = yield Set.has_element(db, "504504", "12345")
    assert r is False


@gen_test
def test_set_get_elements():
    db = create_mockdb()

    reply = [(rdflib.Literal(1,),), (rdflib.Literal(2,),), (rdflib.Literal(3,),)]
    db.query.return_value = make_future(reply)
    with patch('repository.models.set.Set._parse_response') as parse_response:
        parse_response.side_effect = lambda x: x
        r = yield Set.get_elements(db, "504504")

    assert set(r) == set([x[0] for x in reply])


@gen_test
def test_set_set_elements2():
    db = create_mockdb()
    yield Set.set_elements(db, "504504", ["1d0001", "1d0002"])
    assert db.update.call_count == 1

@gen_test
def test_set_append_elements():
    db = create_mockdb()
    yield Set.append_elements(db, "504504", ["1d0001", "1d0002"])
    assert db.update.call_count == 1

@gen_test
def test_set_remove_elements():
    db = create_mockdb()
    yield Set.remove_elements(db, "504504", ["1d0001", "1d0002"])
    assert db.update.call_count == 1
