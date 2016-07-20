# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.


import json
import logging
import rdflib
import re
import urllib
import uuid
from rdflib.query import Result
from tornado.gen import coroutine, Return

from . import helper
from ..queries import generic

ENTITY_ID_REGEX = "([0-9a-fA-F]{1,64})"


def build_sparql_filter(*args):
    if len(args):
        return "FILTER(%s)" % ((" && ".join(["(%s)" % c for c in args])),)
    return ""


def build_sparql_str(s):
    s = s.replace('\\', '\\\\').replace("\"", "\\\"")
    return "\"%s\"" % (s,)
    # return "\"%s\"^^xsd:string"%(s,)


def build_hub_reference(s):
    return "hub:%s" % (urllib.quote_plus(s),)


def validate_entity_id(entity_id):
    return re.match(ENTITY_ID_REGEX, entity_id)


def build_uuid_reference(s):
    if (not re.match(ENTITY_ID_REGEX, s)):
        raise helper.ValidationException("%r is not a valid uuid" % (s,))
    return "id:%s" % (s,)


class Entity(object):
    ## The following query ensure the object exists in the database and has the right type
    CLASS = None
    ID_NAME = "id"

    ## The following query returns a graph for the selected object
    INSERT_TIMESTAMPS = generic.GENERIC_INSERT_TIMESTAMPS
    CHECK_EXISTS = generic.GENERIC_CHECK_EXISTS
    LIST_BY_TIME = generic.GENERIC_LIST
    STRUCT_SELECT = None

    @classmethod
    def _parse_response(cls, rsp):
        return list(Result.parse(rsp.buffer))

    @classmethod
    def safe_id(cls, id):
        """
        Method to ensure an id used is sparql safe (general)

        :param id: the id to be normalised
        :returns: the normalised id
        """
        # virtual to be specialised accordingly by each entity
        if not re.match(r"([a-zA-Z0-9_.#+@:/%\-]+)", id):
            raise helper.ValidationException("Not a valid id '{}'".format(id))

        if id.startswith("http://"):
            return "<%s>" % (id,)

        if not re.match(r"([a-zA-Z0-9_.\-]+):([a-zA-Z0-9_.#+@%\-]+)", id):
            return cls.normalise_id(id)

        return id


    @classmethod
    def normalise_id(cls, id):
        """
        Class specific method use to normalise ids before to use them in queries.

        :param id: the id to be normalised
        :returns: the normalised id
        """
        # virtual to be specialised accordingly by each entity
        if id.startswith("http://"):
            return "<%s>" % (id,)
        return id

    @classmethod
    @coroutine
    def store(cls, repository, payload, content_type='application/xml'):
        """
        Store the assets in the database.

        :param payload: tornado.httputil.HTTPServerRequest instance
        :param repository: the linked-data database where to store the asset
        :param content_type: mimetype of the data uploaded
        :returns: list of encountered errors
        """

        if content_type == 'application/xml':
            helper.validate(payload, 'xml')
        elif content_type == 'application/ld+json':
            g = helper.validate(payload, 'json-ld')
            payload = g.serialize()
            content_type = 'application/xml'

        yield cls.call_event_handler("before_store", payload=payload, content_type=content_type, repository=repository)

        yield repository.store(payload, content_type=content_type)

        res = yield cls.call_event_handler("on_store", payload=payload, content_type=content_type,
                                           repository=repository)

        raise Return(res)

    @classmethod
    @coroutine
    def exists(cls, repository, entity_id, filters=None, extra_constraints=None):
        if extra_constraints is None:
            extra_constraints = []
        if filters is not None:
            extra_constraints.append(build_sparql_filter(*filters))
        query = generic.SPARQL_PREFIXES
        query += cls.CHECK_EXISTS.format(**{"id": cls.normalise_id(entity_id),
                                            "class": cls.CLASS,
                                            "filters": ".".join(extra_constraints, )
                                            }
                                         )
        rsp = yield repository.query(query, response_type='json')
        body = json.loads(str(rsp.body))
        raise Return(body['boolean'])

    @classmethod
    @coroutine
    def retrieve(cls, repository, entity_id, format="jsonld"):
        """
        Retrieve an object

        :param entity_id: id of offer offer
        :param repository: the linked-data database where to store the asset
        :return: a dictionary representing the offer
        """

        query = generic.SPARQL_PREFIXES
        if cls.STRUCT_SELECT is not None:
            struct_query = cls.STRUCT_SELECT
        else:
            struct_query = "BIND ( {id} as ?s ) "
        query += (generic.GENERIC_GET % (struct_query,)).format(**{'id': cls.normalise_id(entity_id), 'class': cls.CLASS})
        rsp = yield repository.query(query, response_type='#text/turtle')
        if format == "turtle":
            raise Return(rsp.body)
        if format == "graph":
            graph = rdflib.Graph()
            graph.parse(data=rsp.body, format="turtle")
            raise Return(graph)
        elif format == "jsonld":
            result = helper.rdf_to_json_ld(rsp.body, input_format='turtle')
            raise Return(result)
        else:
            raise ValueError("Unsupported serialisation format requested")

    @classmethod
    @coroutine
    def call_event_handler(cls, event, **kwargs):
        """
        used to call event handler to allow to extend generic behavior the generic model

        :param event: the name of the event handler to be called
        :param kwargs: arguments to be passed to the event handler
        :returns: the result of the last event handler
        """
        eh = getattr(cls, event, [])
        if callable(eh):
            res = yield eh(**kwargs)
            raise Return(res)
        elif type(eh) == list:
            res = None
            for o in eh:
                res = yield o(**kwargs)
            raise Return(res)
        raise ValueError

    @classmethod
    @coroutine
    def insert_timestamps(cls, repository, ids):
        """
        Insert new modified timestamps for list of ids

        :param repository: the linked-data database where to store the asset
        :param ids: list of asset ids
        """
        if not ids:
            raise Return()

        query = generic.SPARQL_PREFIXES
        query += ";\n".join(map(lambda i: cls.INSERT_TIMESTAMPS.format(entity_id=cls.normalise_id(i)), ids))
        if query:
            yield repository.update(query)

    @classmethod
    @coroutine
    def _retrieve_paged_ids(cls, filters, page, page_size, repository):
        """
        Query identifiers of assets that have been modified/added within time window.

        :param filters: a list of filter to be applied to the query
        :param repository_id: id of repository/namespace
        :param page: query offset
        :param page_size: number of assets per page
        :return: List of assets
        """
        page = max(0, page - 1)
        page_size = max(1, page_size)

        offset = page * page_size

        query = generic.SPARQL_PREFIXES
        query += cls.LIST_BY_TIME.format(**{
            'class': cls.CLASS,
            'id_name': cls.ID_NAME,
            'filter': build_sparql_filter(*filters),
            'extra_query': getattr(cls, "LIST_EXTRA_QUERY", "").format(id_name=cls.ID_NAME),
            'extra_query_ids': getattr(cls, "LIST_EXTRA_IDS", ""),
            'page_size': page_size,
            'offset': offset
        })

        rsp = yield repository.query(query)

        result = cls._parse_response(rsp)

        raise Return(result)

    @classmethod
    def float_range_constraint(cls, var, from_value, to_value, datatype="xsd:float"):
        """
        Build the expression associated with a constraint that can be used in a SPARQL filter
        """

        rc = []
        if to_value is not None:
            rc.append("?%s < \"%f\"^^%s" % (var, to_value, datatype))
        if from_value is not None:
            rc.append("?%s >= \"%f\"^^%s" % (var, from_value, datatype))
        return rc

    @classmethod
    def timerange_constraint(cls, var, from_time, to_time, datatype="xsd:dateTime"):
        """
        Build the expression associated with a constraint that can be used in a SPARQL filter
        """

        rc = []
        if to_time is not None:
            rc.append("?%s < \"%s\"^^%s" % (var, to_time, datatype))
        if from_time is not None:
            rc.append("?%s >= \"%s\"^^%s" % (var, from_time, datatype))
        return rc

    @classmethod
    @coroutine
    def match_attr(cls, repository, entity_id, predicate, filters=None, extra="", value="?o"):
        """
        :param repository: the linked-data database where to store the asset
        :param entity_id: the id of an offer
        :param predicate: the predicate used to access the attribute
        :param extra: extra match constraint that the object has to match
        :param filters: a set of constraint that the object has to match
        :return: True or False
        """
        if not filters:
            filters = []
        query = generic.SPARQL_PREFIXES
        query += generic.GENERIC_MATCH_ATTR.format(id=cls.normalise_id(entity_id), predicate=predicate,
                                                   filter=extra + build_sparql_filter(*filters),
                                                   value=value)

        rsp = yield repository.query(query, response_type='json')

        body = json.loads(rsp.body)
        value = body['boolean']
        raise Return(value)

    @classmethod
    @coroutine
    def get_attr(cls, repository, entity_id, predicate, filters=None, page=None, page_size=None):
        """
        Returns a list of attribute value attached to an entity

        :param repository: the linked-data database where to store the asset
        :param entity_id: the id of an offer
        :param predicate: the predicate used to access the attribute
        :param filters: a set of constraint that the object has to match
        :param page: an integer allowing for paginated replies
        :param page_size: an integer allowing for paginated replies
        :returns: True or False
        """
        if filters is None:
            filters = []
        query = generic.SPARQL_PREFIXES
        pagination = ""
        if page_size is not None:
            if page_size < 0:
                raise ValidationError
            if page is None or page < 1:
                page = 1
            page -= 1
            pagination = "ORDER BY ?o\nOFFSET %d\nLIMIT %d\n" % (page*page_size, page_size)
        query += generic.GENERIC_GET_ATTR.format(id=cls.normalise_id(entity_id), predicate=predicate,
                                                 filter=build_sparql_filter(*filters), pagination=pagination)

        rsp = yield repository.query(query)

        result = cls._parse_response(rsp)

        result = [x[0] for x in result]
        raise Return(result)

    @classmethod
    def format_value(cls, value, where_query, datatype=None, vname="?o"):
        if datatype:
            vtmpl = '"{value}"^^{type}'
        else:
            vtmpl = '<{value}>'

        def _format_value(val):
            val = str(val).encode("string-escape")
            if datatype is not None or '/' in val:
                val = vtmpl.format(value=val, type=datatype)
            return val

        if value is not None:
            if type(value) == list:
                value = ["  (%s)\n" % (_format_value(v),) for v in value]
                where_query += "VALUES ({}) {{  {}  }}\n".format(vname, "\n".join(value))
            else:
                where_query += "BIND ({} AS {})\n".format(_format_value(value), vname)

        return value, where_query

    @classmethod
    @coroutine
    def append_attr(cls, repository, entity_id, predicate, value, datatype, filters=None, prequery="", update_last_modified=True):
        """
        Append an attribute to an object

        :param repository: the linked-data database where to store the asset
        :param entity_id: the id of the entity
        :param predicate: the predicate used to access the attribute
        :param value: a serialised string representing the value
        :param datatype: the serialisation used
        """
        if filters is None:
            filters = []
        predicate_path = re.findall("(\([^)]*\)|<[^>]*>|\w+:\w+)(?=/|$)", predicate)
        query = generic.SPARQL_PREFIXES
        entity_id = cls.normalise_id(entity_id)

        query += prequery

        if type(value) != list:
            value = [value]

        if len(value):
            if len(predicate_path) > 1:
                where_query = """
                {id} {path} ?s .
                {filters}
                """.format(id=entity_id, path="/".join(predicate_path[:-1]), filters="\n".join(filters))
            else:
                where_query = "BIND ({} AS ?s)".format(entity_id)

            value, where_query = cls.format_value(value, where_query, datatype, "?to")
            value = "?to"

            query += generic.INSERT_WHERE % (
                generic.GENERIC_SET_ATTR.format(id="?s",
                                                predicate=predicate_path[-1],
                                                value=value),
                where_query
            )

        if update_last_modified:
            if query.strip()[-1] != ';':
                query += ";"
            query += cls.INSERT_TIMESTAMPS.format(entity_id=entity_id)

        yield repository.update(query)


    @classmethod
    @coroutine
    def filter_out_attr(cls, repository, entity_id, predicate, value, datatype, filters=None, prequery="", update_last_modified=True):
        """
        Remove attributes values from an attr

        :param repository: the linked-data database where to store the asset
        :param entity_id: the id of the entity
        :param predicate: the predicate used to access the attribute
        :param value: a serialised string representing the value
        :param datatype: the serialisation used
        """
        if filters is None:
            filters = []
        predicate_path = re.findall("(\([^)]*\)|<[^>]*>|\w+:\w+)(?=/|$)", predicate)
        entity_id = cls.normalise_id(entity_id)
        if len(predicate_path) > 1:
            where_query = """
                {id} {path} ?s .
                {filters}
            """.format(id=entity_id, path="/".join(predicate_path[:-1]), filters="\n".join(filters))
        else:
            where_query = "BIND ({} AS ?s)\n".format(entity_id)

        value, where_query = cls.format_value(value, where_query, datatype)

        query = generic.DELETE_TRIPLES_WHERE % (
            """
            {where_query}
            BIND({predicate} AS ?p) .
            ?s {predicate} ?o .
            """.format(
                    where_query=where_query,
                    id=entity_id,
                    predicate=predicate_path[-1]
            )
        )

        if update_last_modified:
            query += ";"
            query += cls.INSERT_TIMESTAMPS.format(entity_id=entity_id)

        yield repository.update(generic.SPARQL_PREFIXES + query)


    @classmethod
    @coroutine
    def set_attr(cls, repository, entity_id, predicate, value, datatype=None, filters=None, update_last_modified=True):
        """
        Set an attribute on an object and replace existing values.
        This method accept sparqlpath to resourcees with some limitations:
           The path must finish by a final "/" before the final predicate
           "|" allowed only inside "()" only one level of parenthesis.
           A typical valid predicate path looks like:
           (<http://openpermissions.org/definedBy>|rdf:type/<http://openpermissions.org/definedBy>)/<http://openpermissions.org/comment>

        :param repository: the linked-data database where to store the asset
        :param predicate: the predicate used to access the attribute.
                          Note this can also be a predicate path.
        :param entity_id: the id of the entity
        :param value: a serialised string representing the value
        :param datatype: the serialisation used
        """
        if filters is None:
            filters = []
        predicate_path = re.findall("(\([^)]*\)|<[^>]*>|\w+:\w+)(?=/|$)", predicate)
        entity_id = cls.normalise_id(entity_id)
        if len(predicate_path) > 1:
            where_query = """
                {id} {path} ?s .
                {filters}
            """.format(id=entity_id, path="/".join(predicate_path[:-1]), filters="\n".join(filters))
        else:
            where_query = "BIND ({} AS ?s)".format(entity_id)

        prequery = generic.DELETE_TRIPLES_WHERE % (
            """
            {where_query}
            BIND({predicate} AS ?p) .
            ?s {predicate} ?o .
            """.format(where_query=where_query,
                       id=entity_id,
                       predicate=predicate_path[-1]
                       )
        )
        prequery += ";"
        yield cls.append_attr(repository, entity_id, predicate, value, datatype, filters, prequery=prequery, update_last_modified=update_last_modified)

    @classmethod
    def _copy_graph(cls, g, entity_id):
        if cls.STRUCT_SELECT:
            query = generic.SPARQL_PREFIXES + cls.STRUCT_SELECT.format(id=cls.safe_id(entity_id))
            ids_to_update = [x[0] for x in g.query(query)]
        else:
            if not isinstance(entity_id, rdflib.URIRef):
                entity_id = helper.solve_ns(cls.normalise_id(entity_id))
            ids_to_update = [entity_id]

        new_id = [rdflib.URIRef(generic.PREFIXES['id'] + str(uuid.uuid4()).replace('-', '')) for x in ids_to_update]
        ng = rdflib.Graph()
        iquery = ng.query

        def nquery(query,*args, **kwargs):
            lines = query.split("\n")
            query = "\n".join([l for l in lines if "hint:Query hint:optimizer \"Runtime\"" not in l])
            return iquery(query, *args, **kwargs)
        ng.query = nquery

        for t in g:
            s, p, o = t
            if s in ids_to_update:
                s = new_id[ids_to_update.index(s)]
            if o in ids_to_update:
                o = new_id[ids_to_update.index(o)]

            ng.add((s, p, o))

        return ng

    @classmethod
    @coroutine
    def retrieve_copy(cls, repository, entity_id):
        """
        Retrieve a copy of the entity, which has all internal IDs changed
        """
        g = yield cls.retrieve(repository, entity_id, format="graph")
        raise Return(cls._copy_graph(g, entity_id))
