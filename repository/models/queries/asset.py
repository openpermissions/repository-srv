# -*- coding: utf-8 -*-
# Copyright 2016 Open Permissions Platform Coalition
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.


ASSET_CLASS = "op:Asset"

# Used in conjuncting with GENERIC_LIST query
# NOTE: This return all possible combinations of entity_id and alsoIdentifiedBy_id
# which is what we need for the index
ASSET_LIST_ID_NAME = "entity"
ASSET_LIST_EXTRA_IDS = """?source_id_value ?source_id_type"""
ASSET_LIST_EXTRA_QUERY = """
    ?{id_name} op:alsoIdentifiedBy ?alt_id .
            ?alt_id op:id_type ?source_id_type ;
                    op:value ?source_id_value .
"""

ASSET_APPEND_ALSO_IDENTIFIED = """
   {entity_id} op:alsoIdentifiedBy  _:bnode{bnodeuuid0} .
  _:bnode{bnodeuuid0} op:id_type {source_id_type} .
  _:bnode{bnodeuuid0} op:value	{source_id_value} .
  _:bnode{bnodeuuid0} rdf:type	op:Id .
    """

ASSET_GET_ALSO_IDENTIFIED = """
SELECT ?source_id_type ?source_id WHERE {{
  {entity_id} op:alsoIdentifiedBy ?id .
   ?id op:id_type  ?source_id_type .
   ?id op:value ?source_id .
}}
"""


# Returns offers or agreements associated with an asset
# The policies are associated either directly via odrl:target
#  or via an a set and an asset selector through odrl:target/op:fromSet/op:hasElement
# subquery : responsible for getting {idname}_entity {idname}_id_type {idname}_id_value
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

# NOTE: note used in blazegraph when onboarding
# assets to identify the assets coming from the user.
ASSET_QUERY_ALL_ENTITY_IDS = """
PREFIX op: <http://openpermissions.org/ns/op/1.0/>

SELECT DISTINCT ?entity_id WHERE
{
  ?entity_id rdf:type op:Asset  .
}
"""

# NOTE: this is being used by ASSET_GET_POLICIES_FOR_ASSETS
ASSET_SELECT_BY_ENTITY_ID = """
SELECT ?{idname}_entity ?{idname}_id_value ?{idname}_id_type WHERE {{
    VALUES (?{idname}_id_value) {{
        {idlist}
    }}
    BIND (?{idname}_id_value AS ?{idname}_entity)
    BIND (hub:hub_key AS ?{idname}_id_type)
}}
"""

# NOTE: this is being used by ASSET_GET_POLICIES_FOR_ASSETS
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
# used by GENERIC_GET
ASSET_STRUCT_SELECT = """ SELECT DISTINCT ?s {{ {id} (op:alsoIdentifiedBy)? ?s . }} """
