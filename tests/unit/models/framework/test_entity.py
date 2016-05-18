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
import rdflib
from koi.test_helpers import make_future, gen_test

from repository.models.framework.entity import Entity
from repository.models.framework.helper import solve_ns, future_wrap
# use this for accessing internal nodes of the ontology
_entities = {}


def entity(class_name):
    global _entities
    if class_name is None:
        class_name = "?noclassrelax"
    if class_name not in _entities:
        class T(Entity):
            CLASS = class_name

        _entities[class_name] = T
    return _entities[class_name]


def test_entity_copy_change_single_id():
    entity_id = solve_ns("id:01234")
    g = rdflib.Graph()
    g.add((entity_id, rdflib.RDF.type, rdflib.OWL.Thing))
    ng = Entity._copy_graph(g, entity_id)
    ng = list(ng)
    assert (ng[0][0] != entity_id)


def test_entity_copy_change_multiple_id():
    entity_id = solve_ns("id:01234")
    entity_id2 = solve_ns("id:23456")
    g = rdflib.Graph()


    class TestEntity(Entity):
        CLASS = "hub:Test"
        STRUCT_SELECT = """ SELECT DISTINCT ?s {{ {id} (hub:pred)? ?s . }} """

    g.add((entity_id, rdflib.RDF.type, solve_ns("hub:Test")))
    g.add((entity_id, solve_ns("hub:pred"), entity_id2))
    ng = TestEntity._copy_graph(g, entity_id)
    ng = list(ng)
    assert len(ng) == 2
    assert ng[0][0] != entity_id
    assert ng[1][0] != entity_id
    assert ng[0][2] != entity_id2
    assert ng[1][2] != entity_id2


def test_entity_entity_memoizes():
    assert entity("id:Test") is entity("id:Test")


def test_entity_entity_memoizes2():
    assert entity(None) is entity(None)


def test_entity_entity_memoizes3():
    assert entity("id:Test2") is not entity("id:Test")


@gen_test
def test_set_get_match_attr():
    entity_id = solve_ns("id:01234")
    g = rdflib.Graph()
    
    class_ = "hub:Test"
    g.add((entity_id, rdflib.RDF.type, solve_ns(class_)))
    g = rdflib.Graph()
    old_query = g.query

    def new_query(query, *args, **kwargs):
        lines = query.split("\n")
        query = "\n".join([l for l in lines if "hint:Query hint:optimizer \"Runtime\"" not in l])
        use_json = 0
        if "response_type" in kwargs:
            if "json" == kwargs["response_type"]:
                use_json = 1
            del kwargs["response_type"]
        res = old_query(query, *args, **kwargs)
        if use_json:
            class Response:
                body = json.dumps({'boolean': list(res)[0]})

            return Response
        else:
            return res

    g.query = new_query
    wg = future_wrap(g)
    e = entity(class_)

    e._parse_response = classmethod(lambda cls, x: x)

    r = yield e.match_attr(wg, entity_id, "hub:pred1")
    assert not r
    r = yield e.match_attr(wg, entity_id, "hub:pred1", Entity.float_range_constraint("o", 0.5, 1.5))
    assert not r
    yield e.set_attr(wg, entity_id, "hub:pred1", 1, "xsd:integer")
    r = yield e.match_attr(wg, entity_id, "hub:pred1")
    assert r
    r = yield e.match_attr(wg, entity_id, "hub:pred1", Entity.float_range_constraint("o", 0.5, 1.5))
    assert r
    r = yield e.get_attr(wg, entity_id, "hub:pred1")
    assert r == [rdflib.Literal("1", datatype=rdflib.XSD.integer)]
    yield e.set_attr(wg, entity_id, "hub:pred1", 2, "xsd:integer")
    r = yield e.get_attr(wg, entity_id, "hub:pred1")
    assert r == [rdflib.Literal("2", datatype=rdflib.XSD.integer)]
    yield e.set_attr(wg, entity_id, "hub:pred1", [3, 4], "xsd:integer")
    r = yield e.get_attr(wg, entity_id, "hub:pred1")
    assert set(r) == set([rdflib.Literal("3", datatype=rdflib.XSD.integer), rdflib.Literal("4", datatype=rdflib.XSD.integer)])
    yield e.set_attr(wg, entity_id, "hub:pred1", [], "xsd:integer")
    r = yield e.get_attr(wg, entity_id, "hub:pred1")
    assert r == []
    # test paging
    yield e.set_attr(wg, entity_id, "hub:pred1", list(range(50)), "xsd:integer")
    yield e.append_attr(wg, entity_id, "hub:pred1", list(range(50, 100)), "xsd:integer")
    yield e.append_attr(wg, entity_id, "hub:pred1", list(range(100, 150)), "xsd:integer")
    r = yield e.get_attr(wg, entity_id, "hub:pred1", page_size=30)
    assert len(r) == len(list(range(30)))
    assert r == [rdflib.Literal(str(i), datatype=rdflib.XSD.integer) for i in range(30)]
    r = yield e.get_attr(wg, entity_id, "hub:pred1", page_size=30,page=2)
    assert len(r) == len(list(range(30)))
    assert r == [rdflib.Literal(str(i), datatype=rdflib.XSD.integer) for i in range(30, 60)]
    # test filter_out
    yield e.filter_out_attr(wg, entity_id, "hub:pred1", range(0, 100, 2), "xsd:integer")
    r = yield e.get_attr(wg, entity_id, "hub:pred1", page_size=30)
    assert len(r) == len(list(range(30)))
    assert r == [rdflib.Literal(str(i), datatype=rdflib.XSD.integer) for i in range(1, 61, 2)]
    # test utf8
    yield e.set_attr(wg, entity_id, "hub:pred1", r'\xe3\x83\x81\xe3\x83\xa7\xe3\x82\xb3\xe3\x83\x81\xe3\x83\xa7\xe3\x82\xb3'.decode('utf8'), "xsd:string")
    r = yield e.get_attr(wg, entity_id, "hub:pred1")
    assert(str(r[0]).decode('utf8') == r'\xe3\x83\x81\xe3\x83\xa7\xe3\x82\xb3\xe3\x83\x81\xe3\x83\xa7\xe3\x82\xb3')
