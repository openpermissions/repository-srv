# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

# Prefixes of the namespaces that we use
# will be added to sparql queries and turtle data and JSON-LD context
PREFIXES = {
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "owl": "http://www.w3.org/2002/07/owl#",
    'id': "http://openpermissions.org/ns/id/",
    "odrl": "http://www.w3.org/ns/odrl/2/",
    "op": "http://openpermissions.org/ns/op/1.1/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcterm": "http://purl.org/dc/terms/",
    "opex": "http://openpermissions.org/ns/opex/1.0/",
    'hub': "http://openpermissions.org/ns/hub/",
    "hint": "http://www.bigdata.com/queryHints#"
}

JSON_LD_CONTEXT = dict(PREFIXES)
JSON_LD_CONTEXT.update({
    "@vocab": "http://www.w3.org/ns/odrl/2/",
    "@language": "en",
    'op:alsoIdentifiedBy': {"@container": "@set", "type": "@id"},
    'duty': {"@container": "@set", "type": "@id"},
    'prohibition': {"@container": "@set", "type": "@id"},
    'permission': {"@container": "@set", "type": "@id"},
    'constraint': {"@container": "@set", "type": "@id"},
    'target': {"@container": "@set", "type": "@id"}
})

SPARQL_PREFIXES = "\n".join("PREFIX %s: <%s>" % i for i in PREFIXES.items())+"\n"
TURTLE_PREFIXES = "\n".join("@prefix %s: <%s> ." % i for i in PREFIXES.items())+"\n"

# Checks whether an entity exists
# :param id: Id of entity Returns true if an entity is of a certain class
# :param class: Entity Class Returns true if an entity is of a certain class
# :param filters: Optional filters to apply to check
# :returns boolean
GENERIC_CHECK_EXISTS = """
ASK  WHERE {{
    hint:Query hint:optimizer "Runtime" .

    {id} a {class} .
    BIND ( {id} as ?s ) .
    {filters}
}}
"""

# Adds a new timestamp for entity
# :param entity_id: Id of entity
GENERIC_INSERT_TIMESTAMPS = """
INSERT {{
  {entity_id} dcterm:modified ?now .
}}
WHERE {{
    BIND ( NOW() as ?now ) .
}}
"""

# Gets a list of entities
#
# :param id_name: name of the variable for the id for use in extra queries
# :param class: entity class
# :param extra_query: (optional) SPAQL query to determine extra results
# :param filter: (optional) SPAQL query to filter id_name
# :param page_size: number of results to return
# :param offset: start index of returned results

# :returns id_name: Variable id
# :returns extra_query_ids : variables that are returned from extra_query
# :last_modified: Timestamp entity was last modified
GENERIC_LIST = """
SELECT ?{id_name} {extra_query_ids} ?last_modified
WHERE {{
    hint:Query hint:optimizer "Runtime" .
    {{
        SELECT ?{id_name} (MAX(?when) AS ?last_modified)

        WHERE {{
            ?{id_name} a {class} .
            OPTIONAL {{ ?{id_name} dcterm:modified ?when  }}

            {filter}
        }}
        GROUP BY ?{id_name}
    }}
    {extra_query}
}}
ORDER BY ?last_modified
LIMIT {page_size}
OFFSET {offset}
"""

INSERT_DATA = """
INSERT DATA {
%s
}
"""

INSERT_WHERE = """
INSERT {
%s
}
WHERE {
%s
}
"""


DELETE_TRIPLES_WHERE = """
DELETE {
?s ?p ?o
}
WHERE {
%s
}
"""

# Get predicate value for entity
# :param id: id of entity
# :param predicate: predicate to get value for
# :param filter: (optional) SPAQL query to filter
# :param pagination: (optional) Limit and offset information

# :returns o: Predicate value
GENERIC_GET_ATTR = """
SELECT ?o WHERE
{{
  hint:Query hint:optimizer "Runtime" .

  {id} {predicate} ?o .
  {filter}
}}
{pagination}
"""


# Determine whether attribute value for entity is true
# :param id: id of entity
# :param predicate: predicate
# :param value: value of predicate
# :param filter: (optional) SPAQL query to filter

# :returns boolean
GENERIC_MATCH_ATTR = """
ASK WHERE
{{
  hint:Query hint:optimizer "Runtime" .

  {id} {predicate} {value} .
  {filter}
}}
"""

# Set predicate value for entity
# :param id: id of entity
# :param predicate: predicate to set value for
# :param value: value of predicate
GENERIC_SET_ATTR = """
   {id} {predicate} {value} .
"""

# Gets an entity
# :param id: id of entity
# :param class: class of entity
# :param %s: The STRUCT_QUERY which is responsible for defining the structure of the subgraph to be matched.
#            Subgraph enumerates the subjects that correspond to internal sub-objects.
#
# :returns: Entity Triples
GENERIC_GET = """
CONSTRUCT {{ ?s ?p ?o }}
WHERE
{{
  hint:Query hint:optimizer "Runtime" .

  {id} a {class} .
  {{
    %s
  }}

  ?s ?p ?o .
}}
"""
