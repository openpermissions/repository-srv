# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

import string

ASSET_CLASS = "op:Asset"

# Used in conjunction with GENERIC_LIST query
# This return all possible combinations of entity_id and alsoIdentifiedBy_id which is what we need for the index
# :param id_name: name of the variable for the id
# :returns source_id_value: Value of Source Id for asset
# :returns source_id_type: Type of Source Id for asset
ASSET_LIST_ID_NAME = "entity"
ASSET_LIST_EXTRA_IDS = """?source_id_value ?source_id_type"""
ASSET_LIST_EXTRA_QUERY = """
    ?{id_name} op:alsoIdentifiedBy ?alt_id .
            ?alt_id op:id_type ?source_id_type ;
                    op:value ?source_id_value .
"""

# Adds a new alsoIdentifiedBy triple for entity
# :param entity_id: Id of entity
# :param source_id_type: Type of Source Id for asset
# :param source_id_value: Value of Source Id for asset
# :param bnodeuuid0: Dynamically generated identifier for blank node
ASSET_APPEND_ALSO_IDENTIFIED = """
   {entity_id} op:alsoIdentifiedBy  _:bnode{bnodeuuid0} .
  _:bnode{bnodeuuid0} op:id_type {source_id_type} .
  _:bnode{bnodeuuid0} op:value	{source_id_value} .
  _:bnode{bnodeuuid0} rdf:type	op:Id .
    """

# Gets all alsoIdentifiedBy triples for entity
# :param entity_id: Id of entity
# :return source_id_type: Type of Source Id for asset
# :return source_id: Value of Source Id for asset
ASSET_GET_ALSO_IDENTIFIED = """
SELECT ?source_id_type ?source_id WHERE {{
  {entity_id} op:alsoIdentifiedBy ?id .
   ?id op:id_type  ?source_id_type .
   ?id op:value ?source_id .
}}
"""


# Returns offers or agreements associated with an asset, grouped by source_id/source_id_type pairs
# The policies are associated either directly via odrl:target
# or via an a set and an asset selector through odrl:target/op:fromSet/op:hasElement
# :param id_name: name of the variable for the id
# :param subquery: responsible for getting {idname}_entity {idname}_id_type {idname}_id_value
# :param policy_type: Offer or Agreement
#
# :returns idname_id_bundle: source_id_type#source_id_value
# :returns ids: |-separated list of ids for an asset
# :returns policies: |-separated list of policies for an asset
ASSET_GET_POLICIES_FOR_ASSETS = """
SELECT ?{idname}_id_bundle  (GROUP_CONCAT(DISTINCT ?entity_entity; separator='|') as ?ids) (GROUP_CONCAT(DISTINCT ?policy; separator='|') as ?policies)
WHERE
{{
    hint:Query hint:optimizer "Runtime" .

    {subquery}

    BIND (CONCAT(STR(?{idname}_id_type), "#" , STR(?{idname}_id_value)) AS ?{idname}_id_bundle) .

    {{ ?policy odrl:target ?{idname}_entity  . ?policy a {policy_type} . }}
    UNION
    {{ ?policy odrl:target/op:fromSet/op:hasElement ?{idname}_entity . ?policy a {policy_type} . }}

}}
GROUP BY ?{idname}_id_bundle
"""

# UTILITY

# Gets ids for all assets in graph
# NOTE: Not used in blazegraph. Used when onboarding assets to identify the assets coming from the user.
# :returns entity_id: Id of Asset
#PREFIX op: <http://openpermissions.org/ns/op/1.0/>
ASSET_QUERY_ALL_ENTITY_IDS = """

SELECT DISTINCT ?entity_id WHERE
{
  ?entity_id rdf:type op:Asset  .
}
"""

# Gets identifiers for an asset by entity id, for use in ASSET_GET_POLICIES_FOR_ASSETS
# :param idname: name of the variable for the id
# :param idlist: List of entity ids

# :returns idname_entity: name of the variable for the id value
# :returns idname_id_value: source id value
# :returns idname_id_type: source id type
ASSET_SELECT_BY_ENTITY_ID = """
SELECT ?{idname}_entity ?{idname}_id_value ?{idname}_id_type WHERE {{
    VALUES (?{idname}_id_value) {{
        {idlist}
    }}
    BIND (?{idname}_id_value AS ?{idname}_entity)
    BIND (hub:hub_key AS ?{idname}_id_type)
}}
"""

# Gets identifiers for an asset by id value & id type, for use in ASSET_GET_POLICIES_FOR_ASSETS
# :param idname: name of the variable for the id
# :param idlist: List of idname_id_type and idname_id_value pairs

# :returns idname_entity: name of the variable for the id value
# :returns idname_id_value: source id value
# :returns idname_id_type: source id type
ASSET_SELECT_BY_SOURCE_ID = """
SELECT ?{idname}_entity  ?{idname}_id_value ?{idname}_id_type {{
    VALUES ( ?{idname}_id_type ?{idname}_id_value) {{
        {idlist}
    }}
    ?alt_id op:value ?{idname}_id_value .
    ?alt_id op:id_type ?{idname}_id_type .
    ?{idname}_entity op:alsoIdentifiedBy ?alt_id .
}}
"""

# Returns the subjects of the triples that are involved in an asset identified by asset_id
# used by GENERIC_GET.
ASSET_STRUCT_SELECT = """ SELECT DISTINCT ?s {{ {id} (op:alsoIdentifiedBy)? ?s . }} """

FIND_ENTITY_TEMPLATE = string.Template("""
PREFIX hub: <http://openpermissions.org/ns/hub/>
SELECT DISTINCT ?s
WHERE {?s ?p ?o.
	?o  	<http://openpermissions.org/ns/op/1.1/value>  ?id;
<http://openpermissions.org/ns/op/1.1/id_type>  ?idtype
		.
		VALUES (?id ?idtype) {
		$id_filter
		}
	}
""")

SOURCE_ID_FILTER_TEMPLATE = string.Template("""
("$id" hub:$id_type)
""")

FIND_ENTITY_SOURCE_IDS_TEMPLATE = string.Template("""
SELECT DISTINCT ?id ?idtype
WHERE {<h$entity_id> ?p ?o.
?o  	<http://openpermissions.org/ns/op/1.1/value>  ?id;
<http://openpermissions.org/ns/op/1.1/id_type> ?idtype.}
""")

FIND_ENTITY_COUNT_BY_SOURCE_IDS_TEMPLATE = string.Template("""
PREFIX hub: <http://openpermissions.org/ns/hub/>
SELECT (COUNT(?s) AS ?count)
WHERE {?s ?p ?o.
		?o 
           <http://openpermissions.org/ns/op/1.1/value> "$source_id";
			<http://openpermissions.org/ns/op/1.1/id_type> hub:$source_id_type
			.    
      FILTER NOT EXISTS {<$entity_id> ?p ?o}
                 }
""")

DELETE_ID_TRIPLES_TEMPLATE = string.Template("""
PREFIX hub: <http://openpermissions.org/ns/hub/>
#DELETE
CONSTRUCT
WHERE {?s 
           <http://openpermissions.org/ns/op/1.1/value> "$source_id";
			<http://openpermissions.org/ns/op/1.1/id_type> hub:$source_id_type;
      ?p ?o.}
""")

DELETE_ENTITY_TRIPLE_TEMPLATE = string.Template("""
#DELETE
CONSTRUCT
WHERE {
<$entity_id> ?p ?o}
""")
