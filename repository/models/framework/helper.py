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
import json
import re

from koi.test_helpers import make_future

from ..queries.generic import PREFIXES, JSON_LD_CONTEXT


def future_wrap(x):
    """
    Wraps the method of an object so that they return futures.

    :param x: an instance of an object design with method that are not coroutine
    :return: a similar instance with method returning futures
    """
    class AutoFuture:
        def __getattr__(self, item):
            v = getattr(x, item)
            if callable(v):
                return lambda *args, **kwargs: make_future(v(*args, **kwargs))
    return AutoFuture()


def solve_ns(x):
    """
    Transforms a qname expression in a URIRef usable to construct triple.

    :param x: a qname
    :return: a URIRef to use with RDFLib
    """
    return rdflib.URIRef(re.sub("([A-Za-z0-9_-]+):(.*)", lambda r: PREFIXES[r.group(1)] + r.group(2), x))

def rdf_to_json_ld(rdf, json_ld_context=JSON_LD_CONTEXT, input_format='xml'):
    result = None
    if rdf:
        graph = rdflib.Graph().parse(data=rdf, format=input_format)

        if graph:
            string = graph.serialize(format='json-ld',
                                     context=json_ld_context)
            result = json.loads(string)

    return result


class PermissionException(Exception):
    """
    Raised when an action is semantically valid but not allowed by the repository
    """
    pass


class ValidationException(Exception):
    """
    Raised when data appears to be invalid
    """
    pass


def validate(data, format=None):
    """
    Takes a body and sees if it would blow up if it were
    passed to rdf lib.

    :param data: xml, ttl, or json-ld data
    :param format: used if format cannot be determined from source. Can either be 'xml', 'turtle' or 'json-ld'
    :return: None
    :raises ValidationException if there is anything wrong
    """
    graph = rdflib.Graph()
    kwargs = {}

    if format == "json-ld":
        try:
            json_data = json.loads(data)
        except ValueError, e:
            raise ValidationException("Unable to parse data:" + str(e, ))

        if '@graph' in json_data:
            data = json.dumps(json_data['@graph'])
            kwargs['context'] = json_data.get('@context', {})

    try:
        graph.parse(data=data, format=format, **kwargs)
        return graph
    except Exception, e:
        logging.error(data)
        raise ValidationException("error while parsing data+"+str(e))
